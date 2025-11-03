import os
from pyspark.sql import SparkSession, functions as F

# ----------------------------------------------------------------------
# 1. Initialize Spark with MongoDB Connector
# ----------------------------------------------------------------------
spark = (
    SparkSession.builder
    .appName("PostCategoryClassifier")
    .config("spark.mongodb.read.connection.uri", os.environ["MONGODB_URI"])
    .config("spark.mongodb.write.connection.uri", os.environ["MONGODB_URI"])
    .config("spark.mongodb.read.database", "SocialMediaAnalytics")
    .config("spark.mongodb.read.collection", "posts")
    .config("spark.mongodb.write.database", "SocialMediaAnalytics")
    .config("spark.mongodb.write.collection", "posts_updated")
    .getOrCreate()
)

# ----------------------------------------------------------------------
# 2. Load posts data
# ----------------------------------------------------------------------
posts_df = spark.read.format("mongodb").load()

# ----------------------------------------------------------------------
# 3. Filter unclassified posts
# ----------------------------------------------------------------------
unclassified = posts_df.filter(
    (F.col("category").isNull()) | (F.col("category") == "Unclassified")
)

# ----------------------------------------------------------------------
# 4. Define classification logic (very simple keyword-based example)
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
# 5. Apply classification and overwrite only the category field
# ----------------------------------------------------------------------
classified = unclassified.withColumn("new_category", classify_udf(F.col("content"), F.col("hashtags")))
updates = classified.withColumn("category", F.col("new_category")).drop("new_category")


# ----------------------------------------------------------------------
# 6. Combine updated posts with the already-classified ones
# ----------------------------------------------------------------------
# Rename columns to avoid conflicts before join
updates_renamed = updates.select(
    "_id",
    F.col("category").alias("updated_category")
)

merged_df = (
    posts_df.join(updates_renamed, on="_id", how="left")
    .withColumn("category", F.coalesce(F.col("updated_category"), F.col("category")))
    .drop("updated_category")
)



# ----------------------------------------------------------------------
# 7. Write full updated posts to new collection
# ----------------------------------------------------------------------
merged_df.write \
    .format("mongodb") \
    .mode("overwrite") \
    .option("uri", os.environ["MONGODB_URI"]) \
    .option("database", "SocialMediaAnalytics") \
    .option("collection", "posts_updated") \
    .save()

# ----------------------------------------------------------------------
# 8. Log results
# ----------------------------------------------------------------------
updated_count = updates.count()
print(f"✅ Updated {updated_count} posts and saved to 'posts_updated'")

spark.stop()

