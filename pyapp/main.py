# Author: Gavin Kondrath | gav.ink
# Created on: Dec 18th, 2023

import argparse
import os
import time
import schedule

from tiktok_uploader.upload import upload_video
from scripts.create_short import get_story_from_reddit, generate_reddit_story_image, generate_tiktok_tts, create_short_video, create_video_title, upload_short_to_youtube, check_video_fps
from config import launcher_path, footage, music

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


def make_youtube():
    get_story_from_reddit(subreddits)
    generate_reddit_story_image()
    generate_tiktok_tts()
    create_short_video(footage, music)
    create_video_title()

    short_file_path = create_short_video(footage, music)
    short_video_title = create_video_title()

    upload_short_to_youtube(short_file_path, short_video_title)


def make_tiktok():
    # customize functions for TikTok
    get_story_from_reddit(subreddits)
    generate_reddit_story_image()
    generate_tiktok_tts()
    create_short_video(footage, music)
    create_video_title()

    short_file_path = create_short_video(footage, music)
    short_video_title = create_video_title()

    upload_video(short_file_path, description=short_video_title, cookies=f'{launcher_path}/cookies.txt')
    # headless=True
    os.remove(short_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Automating Reddit Shorts: to YouTube or TikTok")
    parser.add_argument("-p", "--platform", choices=VALID_PLATFORM_CHOICES, default=VALID_PLATFORM_CHOICES[2], help="Choose what platform to upload to:")
    args = parser.parse_args()

    platform_choice = args.platform

    check_video_fps(footage)

    if platform_choice == "tiktok":
        make_tiktok()

    elif platform_choice == "youtube":
        make_youtube()

    elif platform_choice == "both":
        make_youtube()
        # make_tiktok()
