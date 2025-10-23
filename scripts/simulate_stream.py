import pandas as pd, time, os
SRC = "data/batch_input/posts.csv"
DEST = "data/stream_landing"
CHUNK, SLEEP = 1, 10
os.makedirs(DEST, exist_ok=True)
df = pd.read_csv(SRC)
for i in range(0, len(df), CHUNK):
    fname = f"{DEST}/posts_{i//CHUNK:04d}.csv"
    df.iloc[i:i+CHUNK].to_csv(fname, index=False)
    print("Dropped:", fname)
    time.sleep(SLEEP)

