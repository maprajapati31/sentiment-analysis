import os
import time
import json
import yaml
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
import tweepy
from tweepy.errors import TooManyRequests

# ────────────────────────────────
# Load credentials & config
# ────────────────────────────────
load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

def fetch_tweets(keyword, lang, max_results, days, output_dir):
    """Fetch tweets for a keyword and handle rate limits gracefully."""
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fname = f"{output_dir}/{keyword}_{end_time.strftime('%Y%m%d_%H%M')}.jsonl"

    try:
        tweets = client.search_recent_tweets(
            query=f"{keyword} lang:{lang} -is:retweet",
            max_results=max_results,
            tweet_fields=["id", "text", "author_id", "created_at"],
            start_time=start_time,
            end_time=end_time,
        )
        with open(fname, "w", encoding="utf-8") as f:
            for tweet in tweets.data or []:
                json.dump(tweet.data, f)
                f.write("\n")
        print(f"✅ {len(tweets.data or [])} tweets → {fname}")

    except TooManyRequests as e:
        # Extract reset time from headers if available
        reset_timestamp = int(e.response.headers.get("x-rate-limit-reset", 0))
        wait_sec = max(0, reset_timestamp - time.time()) + 10
        wait_min = int(wait_sec // 60)
        print(f"⚠️  Rate limit reached. Sleeping for ~{wait_min} min ({int(wait_sec)} s)…")
        time.sleep(wait_sec)
        return fetch_tweets(keyword, lang, max_results, days, output_dir)

    except Exception as e:
        print(f"❌ Error fetching '{keyword}': {e}")

    return fname


if __name__ == "__main__":
    with open("configs/config.yml") as c:
        cfg = yaml.safe_load(c)

    for kw in cfg["keywords"]:
        fetch_tweets(
            keyword=kw,
            lang=cfg["lang"],
            max_results=cfg["max_results"],
            days=cfg["days"],
            output_dir=cfg["output_dir"],
        )
        # Wait between keywords to stay below per-minute limits
        print("⏳ Waiting 60 s before next keyword…")
        time.sleep(60)

