__author__ = 'agustin'
from simon_project.settings import DEBUG
import logging
import twitter
from simon_project import passwords as passwords
from simon_app.decorators import timed_command


@timed_command(name="Tweeting")
def tweet(text):

    logger = logging.getLogger(__name__)
    logger.info("Sending tweet")

    api = twitter.Api(
        consumer_key=passwords.TWITTER['consumer_key'],
        consumer_secret=passwords.TWITTER['consumer_secret'],
        access_token_key=passwords.TWITTER['access_token'],
        access_token_secret=passwords.TWITTER['access_token_secret']
    )

    if DEBUG:
        print "[tweet]: " + text
    else:
        api.PostUpdate(text)