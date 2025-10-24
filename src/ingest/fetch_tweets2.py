
import snscrape.modules.twitter as snstwitter
import pandas as pd
from tqdm import tqdm

start_date = pd.Timestamp('2025-01-01')
end_date = pd.Timestamp('now').floor('D')

query = "Jensen Huang OR NVIDIA since:{} until:{}".format(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

limit = 10000

tweets = []

# Loop over each year
for year in range(start_date.year, end_date.year+1):
    # Define the start and end dates for the current year
    year_start_date = pd.Timestamp('{}-01-01'.format(year))
    year_end_date = pd.Timestamp('{}-12-31'.format(year))

    # Define the query string for the current year
    year_query = "{} since:{} until:{}".format(query, year_start_date.strftime('%Y-%m-%d'), year_end_date.strftime('%Y-%m-%d'))

    # Loop over each tweet for the current year
    for tweet in tqdm(snstwitter.TwitterSearchScraper(year_query).get_items()):
        if len(tweets) >= limit*(year-start_date.year+1):
            break
        else:
            tweets.append([tweet.id,tweet.date,tweet.username, tweet.content,
                           tweet.hashtags,tweet.retweetCount,tweet.likeCount,
                           tweet.replyCount,tweet.source,
                           tweet.user.location,tweet.user.verified,
                           tweet.user.followersCount,tweet.user.friendsCount])
            
df = pd.DataFrame(tweets, columns=['ID','Timestamp','User','Text',
                                   'Hashtag','Retweets','Likes',
                                   'Replies','Source',
                                   'Location','Verified_Account',
                                   'Followers','Following'])


