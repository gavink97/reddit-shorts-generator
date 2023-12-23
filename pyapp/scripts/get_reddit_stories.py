import os
import praw
import random
from dotenv import load_dotenv
from praw.models import MoreComments
from scripts.class_submission import identify_post_type
from config import launcher_path

load_dotenv()
reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']

firefox_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"

reddit = praw.Reddit(
        client_id=f"{reddit_client_id}",
        client_secret=f"{reddit_client_secret}",
        user_agent=f"{firefox_user_agent}"
        )


def get_story_from_reddit(subreddits: []):
    youtube_tts_path = os.path.join(launcher_path, "youtube_tts.txt")

    try:
        with open(youtube_tts_path, 'r') as file:
            youtube_tts = file.read()

    except FileNotFoundError:
        print(f"File {youtube_tts_path} not found.")

    tts_character_limit = 200

    while True:
        subreddit = random.choice(subreddits)
        submission = reddit.subreddit(subreddit).random()

        if submission is None:
            print(f"This subreddit bans the use of .random: {subreddit}")
            continue

        submission_author = submission.author
        submission_title = submission.title
        submission_is_self = submission.is_self
        submission_text = submission.selftext
        submission_url = submission.url
        submission_score = submission.score
        submission_comments_int = submission.num_comments
        submission_timestamp = submission.created_utc

        reddit_submission = identify_post_type(submission_is_self, submission_text, submission_url)

        if reddit_submission.kind == "image" or reddit_submission.kind == "video":
            print(f"This submission is not in text {submission_title}")
            continue

        suitable_submission = False

        for top_level_comment in submission.comments:
            if isinstance(top_level_comment, MoreComments):
                continue

            top_comment_author = top_level_comment.author
            top_comment_body = top_level_comment.body

            if top_comment_author == "AutoModerator":
                print("Skipping bot comment")
                continue

            total_length = len(submission_title) + len(submission_text) + len(top_comment_body) + len(youtube_tts)

            if 300 < total_length <= 900:
                suitable_submission = True

                break

        if suitable_submission:
            print("found suitable submission")
            submission_type = reddit_submission.kind

            if len(submission_title) > tts_character_limit:
                with open(f'{launcher_path}/temp/ttsoutput/texts/{submission_author}_title.txt', 'w', encoding='utf-8') as file:
                    file.write(submission_title)

            if len(submission_text) > tts_character_limit:
                with open(f'{launcher_path}/temp/ttsoutput/texts/{submission_author}_post.txt', 'w', encoding='utf-8') as file:
                    file.write(submission_text)

            if len(top_comment_body) > tts_character_limit:
                with open(f'{launcher_path}/temp/ttsoutput/texts/{top_comment_author}.txt', 'w', encoding='utf-8') as file:
                    file.write(top_comment_body)

            return (subreddit,
                    submission_author,
                    submission_title,
                    submission_text,
                    submission_score,
                    submission_comments_int,
                    submission_timestamp,
                    submission_type,
                    top_comment_author,
                    top_comment_body)

            break
