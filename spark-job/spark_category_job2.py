import os
from pyspark.sql import SparkSession, functions as F

# ----------------------------------------------------------------------
# 1. Initialize Spark with MongoDB Connector
# ----------------------------------------------------------------------
spark = (
    SparkSession.builder
    .appName("PostCategoryIncrementalClassifier")
    .config("spark.mongodb.read.connection.uri", os.environ["MONGODB_URI"])
    .config("spark.mongodb.write.connection.uri", os.environ["MONGODB_URI"])
    .config("spark.mongodb.read.database", "SocialMediaAnalytics")
    .config("spark.mongodb.write.database", "SocialMediaAnalytics")
    .getOrCreate()
)

# ----------------------------------------------------------------------
# 2. Load source and target collections
# ----------------------------------------------------------------------
posts_df = (
    spark.read.format("mongodb")
    .option("database", "SocialMediaAnalytics")
    .option("collection", "posts")
    .load()
)

posts_updated_df = (
    spark.read.format("mongodb")
    .option("database", "SocialMediaAnalytics")
    .option("collection", "posts_updated")
    .load()
)

# ----------------------------------------------------------------------
# 3. Identify new or unclassified posts
# ----------------------------------------------------------------------
# New = not present in posts_updated
# Unclassified = category == "Unclassified" or null
new_posts = posts_df.join(posts_updated_df.select("_id"), on="_id", how="left_anti")

unclassified_posts = posts_df.filter(
    (F.col("category").isNull()) | (F.col("category") == "Unclassified")
)

to_classify = new_posts.unionByName(unclassified_posts).dropDuplicates(["_id"])

# ----------------------------------------------------------------------
# 4. Define category classifier logic
# ----------------------------------------------------------------------
def classify_post(content, hashtags):
    text = (content or "").lower()
    tags = " ".join(hashtags or []).lower()

    if any(word in text + tags for word in ["travel", "trip", "explore", "vacation", "tokyo", "paris"]):
        return "Travel"
    elif any(word in text + tags for word in ["food", "restaurant", "cuisine", "taste", "meal"]):
        return "Food"
    elif any(word in text + tags for word in ["tech", "ai", "machine learning", "data", "software"]):
        return "Technology"
    elif any(word in text + tags for word in ["fitness", "workout", "gym", "health", "running"]):
        return "Health & Fitness"
    elif any(word in text + tags for word in ["music", "movie", "art", "concert"]):
        return "Entertainment"
    else:
        return "General"

classify_udf = F.udf(classify_post)

# ----------------------------------------------------------------------
# 5. Classify only required posts
# ----------------------------------------------------------------------
classified = (
    to_classify.withColumn("category", classify_udf(F.col("content"), F.col("hashtags")))
)

# ----------------------------------------------------------------------
# 6. Append results to posts_updated (incremental write)
# ----------------------------------------------------------------------
classified.write \
    .format("mongodb") \
    .mode("append") \
    .option("uri", os.environ["MONGODB_URI"]) \
    .option("database", "SocialMediaAnalytics") \
    .option("collection", "posts_updated") \
    .save()

# ----------------------------------------------------------------------
# 7. Log summary
# ----------------------------------------------------------------------
print(f"✅ Classified and appended {classified.count()} posts to 'posts_updated'")

spark.stop()

