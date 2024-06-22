import os
import praw
import random
import time

from dotenv import load_dotenv
from reddit_shorts.class_submission import Submission
from reddit_shorts.config import subreddits

load_dotenv()
reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']


def connect_to_reddit(reddit_client_id: str, reddit_client_secret: str, **kwargs) -> praw.Reddit:
    firefox_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"

    try:
        reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=firefox_user_agent
        )
        return reddit

    except Exception as e:
        print(f"Error connecting to Reddit API: {e}")
        return None


def get_story_from_reddit(reddit: praw.Reddit or None = None, **kwargs) -> dict:
    print("Getting a story from Reddit...")
    strategy = 'hot'

    while True:
        subreddit = random.choice(subreddits)
        subreddit_name = subreddit[0]

        try:
            if reddit is None:
                print("Reddit API connection failed. Attempting to reconnect...")
                reddit = connect_to_reddit(reddit_client_id, reddit_client_secret)
                time.sleep(5)

        except praw.exceptions.APIException as api_exception:
            print(f"PRAW API Exception: {api_exception}")
            reddit = None

        except Exception as e:
            print(f"Error: {e}")

        if strategy == 'random':
            submission = reddit.subreddit(subreddit_name).random()
            if submission is None:
                print(f"This subreddit bans the use of .random: {subreddit}")
                continue

                submission_data = Submission.process_submission(subreddit, submission, **kwargs)
                if submission_data:
                    return submission_data.as_dict()

        else:
            for submission in reddit.subreddit(f"{subreddit_name}").hot(limit=20):
                submission_data = Submission.process_submission(subreddit, submission, **kwargs)
                if submission_data:
                    return submission_data.as_dict()
