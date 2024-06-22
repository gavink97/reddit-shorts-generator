import argparse
import os
import ssl

from dotenv import load_dotenv
from apiclient.errors import HttpError

from reddit_shorts.config import launcher_path, project_path
from reddit_shorts.get_reddit_stories import get_story_from_reddit, connect_to_reddit
from reddit_shorts.make_submission_image import generate_reddit_story_image
from reddit_shorts.make_tts import generate_tiktok_tts
from reddit_shorts.create_short import create_short_video
from reddit_shorts.make_youtube_metadata import create_video_title, create_video_keywords
from reddit_shorts.query_db import create_tables
from reddit_shorts.upload_to_youtube import initialize_upload, get_authenticated_service

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
tiktok_secret_id = os.environ['TIKTOK_SESSION_ID_UPLOAD']
reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']

VALID_PLATFORM_CHOICES = ("tiktok", "youtube", "both", "video")


def run_script(**kwargs) -> list:
    reddit = connect_to_reddit(reddit_client_id, reddit_client_secret)

    submission_data = get_story_from_reddit(reddit, **kwargs)

    generate_reddit_story_image(**{**submission_data, **kwargs})

    tts_tracks = generate_tiktok_tts(**{**submission_data, **kwargs})

    # fix tts_tracks being a tuple
    short_file_path = create_short_video(**{**tts_tracks, **submission_data, **kwargs})

    short_video_title = create_video_title(**{**submission_data, **kwargs})

    return short_video_title, short_file_path, submission_data


# rewrite this function
def main(**kwargs) -> None:
    platform = kwargs.get("platform")
    db_path = f'{project_path}/reddit-shorts/shorts.db'

    if not os.path.isfile(db_path):
        create_tables()

    if platform == "tiktok":
        try:
            from tiktok_uploader.upload import upload_video

        except ImportError:
            print("Tiktok Uploader is unavailable")

        short_video_title, short_file_path, submission_data = run_script(**kwargs)

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

    elif platform == "youtube":

        short_video_title, short_file_path, submission_data = run_script(**kwargs)

        submission_title = submission_data.get('title')
        subreddit = submission_data.get('subreddit')

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

    elif platform == "both":
        # rewrite to make 2 videos with different platform tts
        run_script(platform)

    elif platform == "video":
        # no tiktok tts
        run_script(platform)


def parse_my_args() -> dict:
    # enable insertion of video, text, music
    # if text input is enabled should skip making the reddit image
    # rewrite to accept video as a platform
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--platform", choices=VALID_PLATFORM_CHOICES, default=VALID_PLATFORM_CHOICES[3], help="Choose what platform to upload to:")
    parser.add_argument("-i", "--input", type=str.lower, action='store', default=False, help="Input your own text")
    parser.add_argument("-v", "--video", type=str.lower, action='store', default=False, help="Input your own video path")
    parser.add_argument("-m", "--music", type=str.lower, action='store', default=False, help="Input your own music") 
    parser.add_argument("-pf", "--filter", action="store_true", default=False, help="Profanity filter")

    args = parser.parse_args()

    platform = args.platform
    profanity_filter = args.filter

    # input_text = args.input
    # input_video = args.video
    # input_music = args.music

    return {
        'platform': platform,
        'filter': profanity_filter,
    }


def run() -> None:
    args = parse_my_args()
    main(**args)


if __name__ == '__main__':
    run()

else:
    print("problem with __main__")
    run()
