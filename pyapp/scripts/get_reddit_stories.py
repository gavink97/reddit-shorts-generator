import os
import praw
import random
from dotenv import load_dotenv
from praw.models import MoreComments
from scripts.class_submission import identify_post_type
from scripts.query_db import check_if_video_exists, write_to_db
from config import launcher_path

load_dotenv()
reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_database = os.environ['MYSQL_DB']

firefox_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"

reddit = praw.Reddit(
        client_id=f"{reddit_client_id}",
        client_secret=f"{reddit_client_secret}",
        user_agent=f"{firefox_user_agent}"
        )


def get_story_from_reddit(subreddits: [], platform_tts, test_mode):
    # organize comments by score
    # see if can get hot & random submissions
    # figure out why this gets stuck sometimes in Docker

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
        submission_id = submission.id

        submission_author = str(submission_author)
        submission_author = submission_author.replace("-", "")

        reddit_submission = identify_post_type(submission_is_self, submission_text, submission_url)

        if reddit_submission.kind == "image" or reddit_submission.kind == "video":
            print(f"This submission is not in text {submission_title}")
            continue

        print(submission_title)

        suitable_submission = False

        for top_level_comment in submission.comments:
            if isinstance(top_level_comment, MoreComments):
                continue

            top_comment_author = top_level_comment.author
            top_comment_body = top_level_comment.body
            top_comment_id = top_level_comment.id
            top_comment_score = top_level_comment.score

            top_comment_author = str(top_comment_author)
            top_comment_author = top_comment_author.replace("-", "")

            print(top_comment_body)
            if top_comment_author == "AutoModerator":
                print("Skipping bot comment")
                continue

            total_length = len(submission_title) + len(submission_text) + len(top_comment_body) + len(platform_tts)

            if 300 < total_length <= 900:
                if test_mode is True:
                    break

                else:
                    video_exists = check_if_video_exists(db_user, db_pass, db_host, db_port, db_database, submission_id, top_comment_id)

                    if video_exists is False:
                        suitable_submission = True
                        break

                    else:
                        continue

        if suitable_submission:
            print("found suitable submission")
            submission_type = reddit_submission.kind

            if not os.path.exists(f"{launcher_path}/temp/ttsoutput/texts/"):
                os.makedirs(f"{launcher_path}/temp/ttsoutput/texts/")

            if len(submission_title) > tts_character_limit:
                with open(f'{launcher_path}/temp/ttsoutput/texts/{submission_author}_title.txt', 'w', encoding='utf-8') as file:
                    file.write(submission_title)

            if len(submission_text) > tts_character_limit:
                with open(f'{launcher_path}/temp/ttsoutput/texts/{submission_author}_content.txt', 'w', encoding='utf-8') as file:
                    file.write(submission_text)

            if len(top_comment_body) > tts_character_limit:
                with open(f'{launcher_path}/temp/ttsoutput/texts/{top_comment_author}.txt', 'w', encoding='utf-8') as file:
                    file.write(top_comment_body)

            if test_mode is False:
                write_to_db(db_user, db_pass, db_host, db_port, db_database, submission_id, top_comment_id)

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
