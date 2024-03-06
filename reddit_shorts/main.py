import argparse
import os
import ssl

from dotenv import load_dotenv
from apiclient.errors import HttpError

from reddit_shorts.config import footage, music, subreddits, launcher_path
from reddit_shorts.get_reddit_stories import get_story_from_reddit, connect_to_reddit
from reddit_shorts.make_submission_image import generate_reddit_story_image
from reddit_shorts.make_tts import generate_tiktok_tts
from reddit_shorts.create_short_v2 import create_short_video
from reddit_shorts.make_youtube_metadata import create_video_title, create_video_keywords
from reddit_shorts.utils import tts_for_platform
from reddit_shorts.query_db import create_tables
from reddit_shorts.upload_to_youtube import initialize_upload, get_authenticated_service

try:
    from tiktok_uploader.upload import upload_video

except ImportError:
    print("Tiktok Uploader is not available")

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
tiktok_secret_id = os.environ['TIKTOK_SESSION_ID_UPLOAD']
reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']

VALID_PLATFORM_CHOICES = ("tiktok", "youtube", "both", "video")


def run_script(platform: str):
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
     top_comment_body) = get_story_from_reddit(subreddits, platform_tts, reddit, platform)

    generate_reddit_story_image(submission_author, submission_title, subreddit, submission_timestamp, submission_score, submission_comments_int)

    (narrator_title_track,
     narrator_content_track,
     commentor_track,
     platform_tts_track) = generate_tiktok_tts(submission_title, submission_author, submission_text, top_comment_body, top_comment_author, platform_tts_path, platform_tts)

    short_file_path = create_short_video(footage, music, submission_author, submission_text, narrator_title_track, narrator_content_track, commentor_track, platform_tts_track, subreddit_music_type)

    short_video_title = create_video_title(submission_title, subreddit, platform)

    return short_video_title, short_file_path, submission_title, subreddit


def main():
    # enable insertion of video, text, music
    # if text input is enabled should skip making the reddit image
    # rewrite to accept video as a platform
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--platform", choices=VALID_PLATFORM_CHOICES, default=VALID_PLATFORM_CHOICES[3], help="Choose what platform to upload to:")
    parser.add_argument("-i", "--input", type=str.lower, action='store', default=False, help="Input your own text")
    parser.add_argument("-v", "--video", type=str.lower, action='store', default=False, help="Input your own video path")
    parser.add_argument("-m", "--music", type=str.lower, action='store', default=False, help="Input your own music")
    args = parser.parse_args()

    platform_choice = args.platform
    # input_text = args.input
    # input_video = args.video
    # input_music = args.music

    create_tables()

    if platform_choice == "tiktok":
        short_video_title, short_file_path = run_script(platform_choice)

        max_retry_attempts = 5
        retry_count = 0

        while retry_count < max_retry_attempts:
            try:
                upload_video(short_file_path, description=short_video_title, cookies=f'{launcher_path}/cookies.txt', browser='firefox', headless=False)
                break

            except Exception as e:
                print(f"Upload failed with exception: {e}. Retrying... Attempt {retry_count + 1} of {max_retry_attempts}")
                retry_count += 1

            if retry_count == max_retry_attempts:
                print("Max retries exceeded. Failed to upload a video to tiktok.")
                break

        if os.path.exists(short_file_path):
            os.remove(short_file_path)

    elif platform_choice == "youtube":
        short_video_title, short_file_path, submission_title, subreddit = run_script(platform_choice)

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

    elif platform_choice == "both":
        # rewrite to make 2 videos with different platform tts
        run_script(platform_choice)

    elif platform_choice == "video":
        # no tiktok tts
        run_script(platform_choice)


if __name__ == '__main__':
    main()
