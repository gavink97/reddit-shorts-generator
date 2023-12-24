import os
import praw
from dotenv import load_dotenv
# from praw.models import MoreComments
# from config import launcher_path
from class_submission import identify_post_type

load_dotenv()
reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']

firefox_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"

reddit = praw.Reddit(
        client_id=f"{reddit_client_id}",
        client_secret=f"{reddit_client_secret}",
        user_agent=f"{firefox_user_agent}"
        )

subreddit = "TheMajorityReport"


def identify_submission_type():
    submission = reddit.subreddit(subreddit).random()

    submission_author = submission.author
    submission_title = submission.title
    submission_is_self = submission.is_self
    submission_text = submission.selftext
    submission_url = submission.url
    submission_id = submission.id

    print(submission_author)
    print(submission_id)
    print(submission_title)
    identified_post = identify_post_type(submission_is_self, submission_text, submission_url)
    print(identified_post.kind)
    print(submission_text)
    print(len(submission_text))


identify_submission_type()