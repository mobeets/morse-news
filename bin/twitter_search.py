import os
import re
# from twython import Twython

# CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
# CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
# OAUTH_TOKEN = os.environ['TWITTER_OAUTH_TOKEN']
# OAUTH_TOKEN_SECRET = os.environ['TWITTER_OAUTH_TOKEN_SECRET']

def user_handle():
    return Twython(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

def remove_url(text):
    has_url = lambda text: re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    return ' '.join([x for x in text.split() if has_url(x)])

def clean_tweet(text):
    return remove_url(text).replace('@','').replace('#','')

def status_text(status):
    return status['text']

def status_search(handle, query):
    return handle.search(q=query)

def tweets_from_query(handle, query, n):
    tweets = [clean_tweet(status_text(status)) for status in status_search(handle, query)['statuses']]
    if n:
        tweets = tweets[:n]
    return '...'.join(tweets)
