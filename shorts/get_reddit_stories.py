import os
import random
import time

import praw

from shorts.class_submission import Submission
from shorts.config import _subreddits


def _connect_to_reddit(**kwargs) -> praw.Reddit:
    client_id = os.environ['REDDIT_CLIENT_ID']
    client_secret = os.environ['REDDIT_CLIENT_SECRET']
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        return reddit

    except Exception as e:
        raise Exception(f"Error connecting to Reddit API: {e}")


def _get_content(reddit: praw.Reddit or None = None, **kwargs) -> dict:
    print("Getting a story from Reddit...")
    strategy = kwargs.get('strategy')

    while True:
        subreddit = random.choice(_subreddits)
        subreddit_name = subreddit[0]

        try:
            if reddit is None:
                print("Connecting to reddit api...")
                reddit = _connect_to_reddit()
                time.sleep(5)

        except Exception as e:
            raise Exception(e)

        match strategy:
            case "random":
                submission = reddit.subreddit(subreddit_name).random()
                if submission is None:
                    print(
                        f"This subreddit bans the use of .random: {subreddit}"
                    )

                    continue

                    submission_data = Submission.process_submission(
                        subreddit,
                        submission,
                        **kwargs
                    )

                    if submission_data:
                        return submission_data.as_dict()

            case "hot" | _:
                for submission in reddit.subreddit(subreddit_name).hot(limit=20):
                    submission_data = Submission.process_submission(
                        subreddit,
                        submission,
                        **kwargs
                    )

                    if submission_data:
                        return submission_data.as_dict()
