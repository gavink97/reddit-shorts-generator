# Author: Gavin Kondrath | gav.ink
# Created on: Dec 18th, 2023

import argparse
import os
import ssl

from dotenv import load_dotenv
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from config import launcher_path, footage, music
from scripts.get_reddit_stories import get_story_from_reddit
from scripts.make_submission_image import generate_reddit_story_image
from scripts.make_tts import generate_tiktok_tts
from scripts.create_short import create_short_video
from scripts.make_video_title import create_video_title
from scripts.minor_operations import check_video_fps, tts_for_platform
from scripts.init_db import test_db_connection, create_tables
from scripts.upload_to_youtube import initialize_upload, get_authenticated_service
from tiktok_uploader.upload import upload_video

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
tiktok_secret_id = os.environ['TIKTOK_SESSION_ID_UPLOAD']
db_host = os.environ['MYSQL_HOST']
db_port = os.environ['MYSQL_PORT']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_database = os.environ['MYSQL_DB']

VALID_PLATFORM_CHOICES = ("tiktok", "youtube", "both")

# add more subbreddits

subreddits = [
        "askreddit",
        "askmen",
        "nostupidquestions",
        "askuk",
        "unpopularopinion",
        "todayilearned",
        "showerthoughts"
        ]


def make_youtube(test_mode):
    platform = "youtube"
    (platform_tts_path, platform_tts) = tts_for_platform(platform)

    (subreddit,
     submission_author,
     submission_title,
     submission_text,
     submission_score,
     submission_comments_int,
     submission_timestamp,
     submission_type,
     top_comment_author,
     top_comment_body) = get_story_from_reddit(subreddits, platform_tts, test_mode)

    generate_reddit_story_image(submission_author, submission_title, subreddit, submission_timestamp, submission_score, submission_comments_int)

    (narrator_title_track,
     narrator_content_track,
     commentor_track,
     platform_tts_track) = generate_tiktok_tts(submission_title, submission_author, submission_text, top_comment_body, top_comment_author, platform_tts_path, platform_tts)

    short_file_path = create_short_video(footage, music, submission_author, submission_text, narrator_title_track, narrator_content_track, commentor_track, platform_tts_track)

    short_video_title = create_video_title(submission_title, subreddit)

    args = argparser.parse_args()
    video_description = ""
    video_category = "20"  # Gaming
    video_keywords = ""
    video_privacy_status = "public"
    notify_subs = False

    # add minecraft as a game played / keywords / video description

    youtube = get_authenticated_service(args)

    try:
        initialize_upload(youtube, short_file_path, short_video_title, video_description, video_category, video_keywords, video_privacy_status, notify_subs)

    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

    os.remove(short_file_path)


def make_tiktok(test_mode):
    platform = "tiktok"
    (platform_tts_path, platform_tts) = tts_for_platform(platform)

    (subreddit,
     submission_author,
     submission_title,
     submission_text,
     submission_score,
     submission_comments_int,
     submission_timestamp,
     submission_type,
     top_comment_author,
     top_comment_body) = get_story_from_reddit(subreddits, platform_tts, test_mode)

    generate_reddit_story_image(submission_author, submission_title, subreddit, submission_timestamp, submission_score, submission_comments_int)

    (narrator_title_track,
     narrator_content_track,
     commentor_track,
     platform_tts_track) = generate_tiktok_tts(submission_title, submission_author, submission_text, top_comment_body, top_comment_author, platform_tts_path, platform_tts)

    short_file_path = create_short_video(footage, music, submission_author, submission_text, narrator_title_track, narrator_content_track, commentor_track, platform_tts_track)

    short_video_title = create_video_title(submission_title, subreddit)

    upload_video(short_file_path, description=short_video_title, cookies=f'{launcher_path}/cookies.txt', browser='firefox', headless=True)
    os.remove(short_file_path)


if __name__ == '__main__':
    # add recovery if script fails
    parser = argparse.ArgumentParser(description="Automating Reddit Shorts: to YouTube or TikTok")
    parser.add_argument("-p", "--platform", choices=VALID_PLATFORM_CHOICES, default=VALID_PLATFORM_CHOICES[2], help="Choose what platform to upload to:")
    parser.add_argument("-t", "--test", action='store_true',  default=False, help="Enable test mode: disables checking database")
    args = parser.parse_args()

    platform_choice = args.platform
    test_mode = args.test

    if test_mode is False:
        test_db_connection(db_user, db_pass, db_host, db_port, db_database)
        create_tables(db_user, db_pass, db_host, db_port, db_database)

    check_video_fps(footage)

    if platform_choice == "tiktok":
        make_tiktok(test_mode)

    elif platform_choice == "youtube":
        make_youtube(test_mode)

    elif platform_choice == "both":
        # if this is selected it should be making the same story for both tiktok and youtube. Adjust accordingly
        make_youtube(test_mode)
        make_tiktok(test_mode)