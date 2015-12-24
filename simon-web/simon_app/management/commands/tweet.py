__author__ = 'agustin'

def tweet(text):
    import twitter
    from simon_project import passwords as passwords

    api = twitter.Api(
        consumer_key=passwords.TWITTER['consumer_key'],
        consumer_secret=passwords.TWITTER['consumer_secret'],
        access_token_key=passwords.TWITTER['access_token'],
        access_token_secret=passwords.TWITTER['access_token_secret']
    )
    api.PostUpdate(text)