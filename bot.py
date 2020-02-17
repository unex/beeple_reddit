import os, sys
import re
import tweepy
import praw

from derw import log

# Twitter
CONSUMER_TOKEN = os.environ.get("CONSUMER_TOKEN")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

# Reddit
SUBREDDIT = os.environ.get("SUBREDDIT")

auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
twitter = tweepy.API(auth)

log.debug(f'Successfully logged into twitter as @{twitter.me().screen_name}')

r = praw.Reddit('RenegadeAI', user_agent='/r/beeple')
log.debug(f'Successfully logged into reddit as {r.user.me()}')

LAST_POST_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'LAST_POST')
if os.path.isfile(LAST_POST_FILE):
    with open(LAST_POST_FILE, 'r') as f:
        LAST_POST = int(f.read())
else:
    LAST_POST = 0

re_title = re.compile("([A-Z]{1,}[\s\W])")

tweets = twitter.user_timeline('beeple', count=10)
for tweet in reversed(tweets):
    if "everyday" in [ht['text'] for ht in tweet.entities['hashtags']]:
        title = ''.join(re.findall(re_title, tweet.text)).strip()
        url = tweet.entities['media'][0]['media_url_https']

        if tweet.id > LAST_POST:
            try:
                submission = r.subreddit(SUBREDDIT).submit(title, url=url, flair_id='8c1b7e86-e96b-11e8-852f-0e6f8368cab6', resubmit=False)
                submission.mod.approve()

                log.info(f'Submitted {title} {submission.shortlink}')

                LAST_POST = tweet.id

                break

            except praw.exceptions.APIException as e:
                if e.error_type in ["ALREADY_SUB"]:
                    log.error(f'{e.message}: {title}')

                else:
                    log.critical(e)
                    break

            except Exception as e:
                log.critical(e)
                break

with open(LAST_POST_FILE, 'w+') as f:
    f.write(f'{LAST_POST}')
