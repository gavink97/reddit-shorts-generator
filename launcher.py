# Author: Gavin Kondrath | gav.ink
# Created on: Dec 18th, 2023

import argparse
import os
import time
import schedule

from tiktok_uploader.upload import upload_video
from scripts.create_short import get_story_from_reddit, generate_reddit_story_image, generate_tiktok_tts, create_short_video, create_video_title, upload_short_to_youtube, check_video_fps
from config import launcher_path

VALID_PLATFORM_CHOICES = ("tiktok", "youtube", "both")

subreddits = [
        "askreddit",
        "askmen",
        "nostupidquestions",
        "askuk",
        "unpopularopinion",
        "todayilearned",
        "showerthoughts"
        ]

footage = [
        f"{launcher_path}/resources/footage/bbswitzer_relaxing_minecraft_parkour.mp4",
        f"{launcher_path}/resources/footage/gianleco_13_mins_minecraft_parkour.mp4",
        f"{launcher_path}/resources/footage/gianleco_6_mins_minecraft_parkour.mp4",
        f"{launcher_path}/resources/footage/spicysauce_2_hours_minecraft_parkour.mp4"
        ]

music = [
        f"{launcher_path}/resources/music/morninglightmusic_uplifting_inspiring.mp3"
        ]


def make_youtube():
    get_story_from_reddit(subreddits)
    generate_reddit_story_image()
    generate_tiktok_tts()
    create_short_video(footage, music)
    create_video_title()

    short_file_path = create_short_video(footage, music)
    short_video_title = create_video_title()

    # upload_short_to_youtube(short_file_path, short_video_title)


def make_tiktok():
    get_story_from_reddit(subreddits)
    generate_reddit_story_image()
    generate_tiktok_tts()
    create_short_video(footage, music)
    create_video_title()

    short_file_path = create_short_video(footage, music)
    short_video_title = create_video_title()

    upload_video(short_file_path, description=short_video_title, cookies=f'{launcher_path}/cookies.txt')
    # headless=True


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
