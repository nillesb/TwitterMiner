# Brian Nilles
# Date: 9/15/2021

import json

import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener
from tweepy import API
from tweepy import Cursor
import numpy as np
import pandas as pd

consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

class TwitterClient:
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_fiends=10):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_fiends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets=10):
        home_timeline_tweets = []
        for tweets in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweets)
        return home_timeline_tweets


class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        return auth


class TwitterStreamer:
    """Streaming and processing tweets as they are posted"""

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetch_tweet_filename, hash_tag_list):
        # Completes twitter authentication and streaming API

        listener = TwitterListener(fetch_tweet_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        api = tweepy.API(auth)

        # Filters twitter stream to capture data by hashtags
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)


class TwitterListener(StreamListener):
    """Prints received tweets to stdout"""

    def __init__(self, fetch_tweet_filename):
        self.fetch_tweet_filename = fetch_tweet_filename

    def on_data(self, raw_data):
        try:
            print(raw_data)
            with open(self.fetch_tweet_filename, 'a') as tf:
                tf.write(raw_data)
            return True
        except BaseException as e:
            print(f"Error on data:  {e}")
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # Return False on data method if rate limit reached
            return False
        print(status_code)


class TweetAnalyzer:
    """Functional analysis and categorizing content of tweets"""

    def tweets_to_dataframe(self, tweeters):
        daf = pd.DataFrame(data=[tweet.text for tweet in tweeters], columns=['tweets'])
        daf['id'] = np.array([tweet.id for tweet in tweeters])
        daf['len'] = np.array([len(tweet.text) for tweet in tweeters])
        daf['date'] = np.array([tweet.created_at for tweet in tweeters])
        daf['source'] = np.array([tweet.source for tweet in tweeters])
        daf['likes'] = np.array([tweet.favorite_count for tweet in tweeters])
        daf['retweets'] = np.array([tweet.retweet_count for tweet in tweeters])

        return daf


if __name__ == "__main__":
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    tweet_analyzer = TweetAnalyzer()

    tweets = api.user_timeline(screen_name='DonaldjTrumpjr', count=200)
    # print(dir(tweets[0]))
    df = tweet_analyzer.tweets_to_dataframe(tweets)

    # Get average length over all tweets
    print(np.mean(df['len']))


    # get number of likes for most liked tweet
    print(np.max(df['likes']))

    # with pd.option_context('display.max_rows', None,
    #                        'display.max_columns', None,
    #                        'display.precision', 3,
    #                        ):
    #     print(df.head(10))
