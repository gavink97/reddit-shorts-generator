# Author: Gavin Kondrath | gav.ink
# Created on: Dec 18th, 2023

import argparse
import os
import ssl

from dotenv import load_dotenv
from apiclient.errors import HttpError

from config import launcher_path, footage, music, subreddits
from scripts.get_reddit_stories import get_story_from_reddit, connect_to_reddit
from scripts.make_submission_image import generate_reddit_story_image
from scripts.make_tts import generate_tiktok_tts
from scripts.create_short_v2 import create_short_video
from scripts.make_youtube_metadata import create_video_title, create_video_keywords
from scripts.utils import tts_for_platform
from scripts.init_db import test_db_connection, create_tables
from scripts.upload_to_youtube import initialize_upload, get_authenticated_service
from tiktok_uploader.upload import upload_video

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
tiktok_secret_id = os.environ['TIKTOK_SESSION_ID_UPLOAD']
reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_database = os.environ['MYSQL_DB']

VALID_PLATFORM_CHOICES = ("tiktok", "youtube", "both", "video")


def make_video(test_mode):
    platform = "youtube"
    (platform_tts_path, platform_tts) = tts_for_platform(platform)

    reddit = connect_to_reddit(reddit_client_id, reddit_client_secret)

    (subreddit,
     subreddit_music_type,
     submission_author,
     submission_title,
     submission_text,
     submission_score,
     submission_comments_int,
     submission_timestamp,
     submission_type,
     top_comment_author,
     top_comment_body) = get_story_from_reddit(subreddits, platform_tts, test_mode, reddit, platform)

    generate_reddit_story_image(submission_author, submission_title, subreddit, submission_timestamp, submission_score, submission_comments_int)

    (narrator_title_track,
     narrator_content_track,
     commentor_track,
     platform_tts_track) = generate_tiktok_tts(submission_title, submission_author, submission_text, top_comment_body, top_comment_author, platform_tts_path, platform_tts)

    create_short_video(footage, music, submission_author, submission_text, narrator_title_track, narrator_content_track, commentor_track, platform_tts_track, subreddit_music_type)

    create_video_title(submission_title, subreddit, platform)


def make_youtube(test_mode):
    platform = "youtube"
    (platform_tts_path, platform_tts) = tts_for_platform(platform)
    reddit = connect_to_reddit(reddit_client_id, reddit_client_secret)

    (subreddit,
     subreddit_music_type,
     submission_author,
     submission_title,
     submission_text,
     submission_score,
     submission_comments_int,
     submission_timestamp,
     submission_type,
     top_comment_author,
     top_comment_body) = get_story_from_reddit(subreddits, platform_tts, test_mode, reddit, platform)

    generate_reddit_story_image(submission_author, submission_title, subreddit, submission_timestamp, submission_score, submission_comments_int)

    (narrator_title_track,
     narrator_content_track,
     commentor_track,
     platform_tts_track) = generate_tiktok_tts(submission_title, submission_author, submission_text, top_comment_body, top_comment_author, platform_tts_path, platform_tts)

    short_file_path = create_short_video(footage, music, submission_author, submission_text, narrator_title_track, narrator_content_track, commentor_track, platform_tts_track, subreddit_music_type)

    short_video_title = create_video_title(submission_title, subreddit, platform)

    additional_keywords = "hidden reddit,hidden,reddit,minecraft,gaming"
    youtube_shorts_keywords = create_video_keywords(submission_title, subreddit, additional_keywords)

    video_description = ""
    video_category = "20"  # Gaming
    video_keywords = youtube_shorts_keywords
    video_privacy_status = "public"
    notify_subs = False

    # add minecraft as a game played / video description

    youtube = get_authenticated_service()

    try:
        initialize_upload(youtube, short_file_path, short_video_title, video_description, video_category, video_keywords, video_privacy_status, notify_subs)

    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

    if os.path.exists(short_file_path):
        os.remove(short_file_path)


def make_tiktok(test_mode):
    platform = "tiktok"
    (platform_tts_path, platform_tts) = tts_for_platform(platform)
    reddit = connect_to_reddit(reddit_client_id, reddit_client_secret)

    (subreddit,
     subreddit_music_type,
     submission_author,
     submission_title,
     submission_text,
     submission_score,
     submission_comments_int,
     submission_timestamp,
     submission_type,
     top_comment_author,
     top_comment_body) = get_story_from_reddit(subreddits, platform_tts, test_mode, reddit, platform)

    generate_reddit_story_image(submission_author, submission_title, subreddit, submission_timestamp, submission_score, submission_comments_int)

    (narrator_title_track,
     narrator_content_track,
     commentor_track,
     platform_tts_track) = generate_tiktok_tts(submission_title, submission_author, submission_text, top_comment_body, top_comment_author, platform_tts_path, platform_tts)

    short_file_path = create_short_video(footage, music, submission_author, submission_text, narrator_title_track, narrator_content_track, commentor_track, platform_tts_track, subreddit_music_type)

    short_video_title = create_video_title(submission_title, subreddit, platform)

    max_retry_attempts = 5
    retry_count = 0

    while retry_count < max_retry_attempts:
        try:
            upload_video(short_file_path, description=short_video_title, cookies=f'{launcher_path}/cookies.txt', browser='firefox', headless=True)
            break

        except Exception as e:
            print(f"Upload failed with exception: {e}. Retrying... Attempt {retry_count + 1} of {max_retry_attempts}")
            retry_count += 1

        if retry_count == max_retry_attempts:
            print("Max retries exceeded. Failed to upload a video to tiktok.")
            break

    if os.path.exists(short_file_path):
        os.remove(short_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Automating Reddit Shorts: to YouTube or TikTok")
    parser.add_argument("-p", "--platform", choices=VALID_PLATFORM_CHOICES, default=VALID_PLATFORM_CHOICES[2], help="Choose what platform to upload to:")
    parser.add_argument("-t", "--test", action='store_true',  default=False, help="Enable test mode: disables checking database")
    args = parser.parse_args()

    platform_choice = args.platform
    test_mode = args.test

    if test_mode is False:
        test_db_connection(db_user, db_pass, db_host, db_port, db_database)
        create_tables(db_user, db_pass, db_host, db_port, db_database)

    if platform_choice == "tiktok":
        make_tiktok(test_mode)

    elif platform_choice == "youtube":
        make_youtube(test_mode)

    elif platform_choice == "video":
        make_video(test_mode)

    elif platform_choice == "both":
        make_youtube(test_mode)
        make_tiktok(test_mode)
