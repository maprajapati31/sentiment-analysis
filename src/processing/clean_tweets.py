import re

import pandas as pd
import json
from pathlib import Path

def load_tweets(data_dir="data/raw"):
    files = list(Path(data_dir).glob("*.jsonl"))
    tweets = []
    for f in files:
        with open(f, "r", encoding="utf-8") as infile:
            for line in infile:
                try:
                    tweets.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    df = pd.DataFrame(tweets)
    print(f"✅ Loaded {len(df)} tweets from {len(files)} files")
    return df


def clean_text(text):
    text = re.sub(r"http\S+", "", text)          # remove URLs
    text = re.sub(r"@\w+", "", text)             # remove mentions
    text = re.sub(r"#", "", text)                # remove hashtags symbol
    text = re.sub(r"[^A-Za-z0-9\s]+", "", text)  # remove non-alphanumeric
    text = text.lower().strip()
    return text

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt


if __name__ == "__main__":
    df = load_tweets()
    df["clean_text"] = df["text"].apply(clean_text)

    analyzer = SentimentIntensityAnalyzer()

    def get_sentiment(text):
        score = analyzer.polarity_scores(text)["compound"]
        if score > 0.05:
            return "positive"
        elif score < -0.05:
            return "negative"
        else:
            return "neutral"

    df["sentiment"] = df["clean_text"].apply(get_sentiment)
    # ────────────────────────────────────────────────────────────────────────────────

    # Save processed data
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.to_csv("data/processed/cleaned_sentiments.csv", index=False)
    print("✅ Sentiment-tagged dataset saved at data/processed/cleaned_sentiments.csv")

    # Optional visualization
    sentiment_counts = df["sentiment"].value_counts()
    sentiment_counts.plot(kind="bar", color=["green", "red", "gray"])
    plt.title("Tweet Sentiment Distribution")
    plt.xlabel("Sentiment")
    plt.ylabel("Count")

    plt.savefig("data/processed/sentiment_distribution.png", bbox_inches="tight")
    plt.close()

    plt.show()


