from datetime import datetime, timedelta
import os, csv, glob, re
import psycopg2
from urllib.parse import urlparse
from airflow import DAG
from airflow.operators.python import PythonOperator

# ---------------------------------------------------------
# DB connection helper
# ---------------------------------------------------------
import psycopg2, os

def get_pg_conn():
    dsn = os.environ.get("AIRFLOW_CONN_POSTGRES_DEFAULT")
    if not dsn:
        raise ValueError("AIRFLOW_CONN_POSTGRES_DEFAULT not found in environment variables.")
    # remove the prefix if Airflow added 'postgresql+psycopg2://'
    dsn = dsn.replace('postgresql+psycopg2://', 'postgresql://')
    conn = psycopg2.connect(dsn)
    return conn


# ---------------------------------------------------------
# SQL for schema + tables
# ---------------------------------------------------------
DDL_SQL = """
CREATE SCHEMA IF NOT EXISTS sentiment;

CREATE TABLE IF NOT EXISTS sentiment.posts_clean (
  post_id TEXT PRIMARY KEY,
  created_at TIMESTAMP,
  brand TEXT,
  text TEXT,
  lang TEXT,
  text_clean TEXT,
  sentiment INTEGER
);

CREATE TABLE IF NOT EXISTS sentiment.brand_sentiment_now (
  brand TEXT,
  window_start TIMESTAMP,
  window_end TIMESTAMP,
  n_posts INT,
  pos_rate NUMERIC,
  neg_rate NUMERIC,
  PRIMARY KEY (brand, window_end)
);
"""

# ---------------------------------------------------------
# Basic text cleaning & sentiment scoring
# ---------------------------------------------------------
POS = {"good","great","love","awesome","amazing","excellent","fantastic","happy"}
NEG = {"bad","terrible","hate","awful","poor","sad","worst","disappointed"}

def clean_text(text):
    t = text.lower()
    t = re.sub(r"http\S+|[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def score(text):
    toks = text.split()
    p = sum(1 for w in toks if w in POS)
    n = sum(1 for w in toks if w in NEG)
    return 1 if p>n else (-1 if n>p else 0)

# ---------------------------------------------------------
# Tasks
# ---------------------------------------------------------
def init_schema():
    with get_pg_conn() as conn, conn.cursor() as cur:
        cur.execute(DDL_SQL)
        conn.commit()

def load_and_process():
    landing = os.path.join("/opt/airflow", "data", "stream_landing")
    files = sorted(glob.glob(os.path.join(landing, "*.csv")))
    if not files:
        print("No new files found.")
        return

    with get_pg_conn() as conn, conn.cursor() as cur:
        for f in files:
            with open(f, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                rows = []
                for r in reader:
                    text = r.get("text", "")
                    cleaned = clean_text(text)
                    sent = score(cleaned)
                    rows.append((
                        r.get("post_id"),
                        r.get("created_at"),
                        r.get("brand"),
                        text,
                        r.get("lang"),
                        cleaned,
                        sent
                    ))
            cur.executemany("""
                INSERT INTO sentiment.posts_clean
                (post_id, created_at, brand, text, lang, text_clean, sentiment)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (post_id) DO NOTHING;
            """, rows)
            os.remove(f)
        conn.commit()
    print("Loaded and processed files.")

def update_window():
    with get_pg_conn() as conn, conn.cursor() as cur:
        cur.execute("""
        WITH bounds AS (
          SELECT NOW() - INTERVAL '10 minutes' AS ws, NOW() AS we
        ),
        c AS (
          SELECT brand,
                 COUNT(*) AS n,
                 AVG(CASE WHEN sentiment=1 THEN 1.0 ELSE 0 END) AS pos_rate,
                 AVG(CASE WHEN sentiment=-1 THEN 1.0 ELSE 0 END) AS neg_rate,
                 (SELECT ws FROM bounds) AS ws,
                 (SELECT we FROM bounds) AS we
          FROM sentiment.posts_clean
          WHERE created_at BETWEEN (SELECT ws FROM bounds) AND (SELECT we FROM bounds)
          GROUP BY brand
        )
        INSERT INTO sentiment.brand_sentiment_now(brand, window_start, window_end, n_posts, pos_rate, neg_rate)
        SELECT brand, ws, we, n, pos_rate, neg_rate FROM c
        ON CONFLICT (brand, window_end) DO UPDATE
          SET n_posts=EXCLUDED.n_posts,
              pos_rate=EXCLUDED.pos_rate,
              neg_rate=EXCLUDED.neg_rate;
        """)
        conn.commit()
    print("Updated rolling window.")
# ---------------------------------------------------------
# DAG definition
# ---------------------------------------------------------
default_args = {
    "owner": "meera",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="sentiment_stream_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/5 * * * *",   # every 5 minutes
    catchup=False,
    default_args=default_args,
    tags=["sentiment","stream"],
) as dag:

    t1 = PythonOperator(task_id="init_schema", python_callable=init_schema)
    t2 = PythonOperator(task_id="load_and_process", python_callable=load_and_process)
    t3 = PythonOperator(task_id="update_window", python_callable=update_window)

    t1 >> t2 >> t3

