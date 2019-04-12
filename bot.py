import os, sys
import pytumblr
import praw

from derw import log

# Tumblr
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")
OAUTH_SECRET = os.environ.get("OAUTH_SECRET")

# Reddit
SUBREDDIT = os.environ.get("SUBREDDIT")

client = pytumblr.TumblrRestClient(
    CONSUMER_KEY,
    CONSUMER_SECRET,
    OAUTH_TOKEN,
    OAUTH_SECRET
)

log.debug(f'Successfully logged into tumblr as {client.info()["user"]["name"]}')

r = praw.Reddit('RenegadeAI', user_agent='/r/beeple')
log.debug(f'Successfully logged into reddit as {r.user.me()}')

LAST_POST_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'LAST_POST')
if os.path.isfile(LAST_POST_FILE):
    with open(LAST_POST_FILE, 'r') as f:
        LAST_POST = int(f.read())
else:
    LAST_POST = 0

posts = client.posts('beeple.tumblr.com', type='photo', limit=5).get('posts')
for post in reversed(posts):
    if 'photos' in post:
        id = post.get("id")
        title = post.get("summary")
        url = post.get("photos")[0]["original_size"]["url"]

        if id > LAST_POST:
            try:
                submission = r.subreddit(SUBREDDIT).submit(title, url=url, flair_id='8c1b7e86-e96b-11e8-852f-0e6f8368cab6', resubmit=False)
                submission.mod.approve()

                log.info(f'Submitted {title} {submission.shortlink}')
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

            LAST_POST = id

with open(LAST_POST_FILE, 'w+') as f:
    f.write(f'{LAST_POST}')
