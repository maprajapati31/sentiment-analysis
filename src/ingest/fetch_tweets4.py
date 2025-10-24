import snscrape.modules.twitter as sntwitter
import json
from datetime import date
from pathlib import Path
import yaml
import os

def fetch_tweets(keyword, max_results, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fname = f"{output_dir}/{keyword}_{date.today()}.jsonl"

    if os.path.exists(fname) and os.path.getsize(fname) > 0:
        print(f"🟡 Already scraped today: {fname}")
        return

    print(f"🔍 Fetching tweets for '{keyword}' ...")

    tweets = []
    try:
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{keyword} lang:en').get_items()):
            if i >= max_results:
                break
            tweets.append({
                "id": tweet.id,
                "date": tweet.date.isoformat(),
                "content": tweet.content,
                "username": tweet.user.username,
            })
    except Exception as e:
        print(f"❗ Could not fetch tweets for '{keyword}': {e}")
        return

    if tweets:
        with open(fname, "w", encoding="utf-8") as f:
            for t in tweets:
                json.dump(t, f)
                f.write("\n")
        print(f"✅ Saved {len(tweets)} tweets → {fname}")
    else:
        print(f"⚠️ No tweets saved for '{keyword}'")

if __name__ == "__main__":
    with open("configs/config.yml") as c:
        cfg = yaml.safe_load(c)
    for kw in cfg["keywords"]:
        fetch_tweets(kw, cfg["max_results"], cfg["output_dir"])

