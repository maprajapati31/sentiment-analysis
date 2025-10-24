#print("Before import snscrape")
#import snscrape
#print("snscrape imported successfully")
#import snscrape.modules.twitter as sntwitter !! this method throws error!!
# sntwitter = importlib.import_module("snscrape.modules.twitter")
# print("twitter module imported successfully")

import importlib
import json
from datetime import date
from pathlib import Path
import yaml

sntwitter = importlib.import_module("snscrape.modules.twitter")

def fetch_tweets(keyword, max_results, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fname = f"{output_dir}/{keyword}_{date.today()}.jsonl"

    if Path(fname).exists() and Path(fname).stat().st_size > 0:
        print(f"🟡 Already scraped: {fname}")
        return

    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f"{keyword} lang:en").get_items()):
        if i >= max_results:
            break
        tweets.append({
            "id": tweet.id,
            "date": tweet.date.isoformat(),
            "content": tweet.content,
            "username": tweet.user.username
        })

    with open(fname, "w", encoding="utf-8") as f:
        for t in tweets:
            json.dump(t, f)
            f.write("\n")
    print(f"✅ Saved {len(tweets)} tweets → {fname}")


if __name__ == "__main__":
    with open("configs/config.yml") as c:
        cfg = yaml.safe_load(c)
    for kw in cfg["keywords"]:
        fetch_tweets(kw, cfg["max_results"], cfg["output_dir"])

