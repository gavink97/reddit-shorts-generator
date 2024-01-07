import os
import praw
import random
import time
import re

from dotenv import load_dotenv
from praw.models import MoreComments

from config import launcher_path
from scripts.class_submission import identify_post_type
from scripts.query_db import check_if_video_exists, write_to_db, check_for_admin_posts

load_dotenv()
reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_database = os.environ['MYSQL_DB']


def connect_to_reddit(reddit_client_id, reddit_client_secret):
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


def get_story_from_reddit(subreddits: [], platform_tts, test_mode, reddit, platform):
    # reduce complexity / break down into smaller functions if possible
    print("Getting a story from Reddit...")
    tts_character_limit = 200
    min_character_len = 300

    if platform == "youtube":
        max_character_len = 830

    elif platform == "tiktok":
        max_character_len = 2400

    url_pattern = re.compile(r'http', flags=re.IGNORECASE)

    while True:
        subreddit = random.choice(subreddits)
        subreddit_name = subreddit[0]
        subreddit_music_type = subreddit[1]

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

        # submission = reddit.subreddit(subreddit_name).random()
        for submission in reddit.subreddit(f"{subreddit_name}").hot(limit=20):
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
            submission_type = reddit_submission.kind

            if submission_type == "image" or submission_type == "video":
                # print(f"This submission is not in text {submission_title}")
                continue

            # print(submission_title)

            if url_pattern.search(submission_text.lower()):
                # print("Skipping post that contains a link")
                continue

            if test_mode is False:
                admin_post = check_for_admin_posts(db_user, db_pass, db_host, db_port, db_database, submission_id)
                if admin_post is True:
                    continue

            suitable_submission = False

            for top_level_comment in submission.comments:
                if isinstance(top_level_comment, MoreComments):
                    continue

                top_comment_author = top_level_comment.author
                top_comment_body = top_level_comment.body
                top_comment_id = top_level_comment.id

                top_comment_author = str(top_comment_author)
                top_comment_author = top_comment_author.replace("-", "")

                # print(top_comment_body)
                if top_comment_author == "AutoModerator":
                    # print("Skipping bot comment")
                    continue

                if top_comment_author == submission_author:
                    # print("Skipping Submission Authors comment")
                    continue

                if url_pattern.search(top_comment_body.lower()):
                    # print("Skipping comment that contains a link")
                    continue

                total_length = len(submission_title) + len(submission_text) + len(top_comment_body) + len(platform_tts)
                print(f"{subreddit_name}:{submission_title} Total:{total_length}")

                if total_length < min_character_len:
                    continue

                if total_length <= max_character_len:
                    if test_mode is True:
                        suitable_submission = True
                        break

                    else:
                        video_exists = check_if_video_exists(db_user, db_pass, db_host, db_port, db_database, submission_id, top_comment_id)
                        if video_exists is False:
                            suitable_submission = True
                            break

                        else:
                            continue

            if suitable_submission is True:
                print("Found a suitable submission!")
                print(f"Suitable Submission:{subreddit}:{submission_title} Total:{total_length}")

                if not os.path.exists(f"{launcher_path}/temp/ttsoutput/texts/"):
                    os.makedirs(f"{launcher_path}/temp/ttsoutput/texts/")

                if len(submission_title) >= tts_character_limit:
                    with open(f'{launcher_path}/temp/ttsoutput/texts/{submission_author}_title.txt', 'w', encoding='utf-8') as file:
                        file.write(submission_title)

                if len(submission_text) >= tts_character_limit:
                    with open(f'{launcher_path}/temp/ttsoutput/texts/{submission_author}_content.txt', 'w', encoding='utf-8') as file:
                        file.write(submission_text)

                if len(top_comment_body) >= tts_character_limit:
                    with open(f'{launcher_path}/temp/ttsoutput/texts/{top_comment_author}.txt', 'w', encoding='utf-8') as file:
                        file.write(top_comment_body)

                if test_mode is False:
                    write_to_db(db_user, db_pass, db_host, db_port, db_database, submission_id, top_comment_id)

                return (subreddit_name,
                        subreddit_music_type,
                        submission_author,
                        submission_title,
                        submission_text,
                        submission_score,
                        submission_comments_int,
                        submission_timestamp,
                        submission_type,
                        top_comment_author,
                        top_comment_body)
