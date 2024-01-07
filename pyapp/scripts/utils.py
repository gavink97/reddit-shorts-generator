import datetime
import os
import random
import unicodedata

from config import launcher_path

# launcher_path = "/Users/gavinkondrath/projects/youtube_shorts/pyapp"


def split_string_at_space(text, index):
    while index >= 0 and text[index] != ' ':
        index -= 1
    return index


def abbreviate_number(number):
    number = int(number)
    if number >= 10**10:
        return '{:.0f}B'.format(number / 10**9)
    elif number >= 10**9:
        return '{:.1f}B'.format(number / 10**9)
    elif number >= 10**7:
        return '{:.0f}M'.format(number / 10**6)
    elif number >= 10**6:
        return '{:.1f}M'.format(number / 10**6)
    elif number >= 10**4:
        return '{:.0f}k'.format(number / 10**3)
    elif number >= 10**3:
        return '{:.1f}k'.format(number / 10**3)
    else:
        return str(number)


def format_relative_time(previous_time):
    current_time = datetime.datetime.now()
    time_difference = current_time - previous_time

    minutes = time_difference.total_seconds() / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7
    months = days / 30
    years = days / 365

    if years >= 1:
        return f"{int(years)} year{'s' if int(years) > 1 else ''} ago"
    elif months >= 1:
        return f"{int(months)} month{'s' if int(months) > 1 else ''} ago"
    elif weeks >= 1:
        return f"{int(weeks)} week{'s' if int(weeks) > 1 else ''} ago"
    elif days >= 1:
        return f"{int(days)} day{'s' if int(days) > 1 else ''} ago"
    elif hours >= 1:
        return f"{int(hours)} hr. ago"
    elif minutes >= 1:
        return f"{int(minutes)} mins ago"
    else:
        return "Just now"


def tts_for_platform(platform):
    if platform == "youtube":
        platform_tts_path = os.path.join(launcher_path, "youtube_tts.txt")

        try:
            with open(platform_tts_path, 'r') as file:
                platform_tts = file.read()

        except FileNotFoundError:
            print(f"File {platform_tts_path} not found.")

    elif platform == "tiktok":
        platform_tts_path = os.path.join(launcher_path, "tiktok_tts.txt")

        try:
            with open(platform_tts_path, 'r') as file:
                platform_tts = file.read()

        except FileNotFoundError:
            print(f"File {platform_tts_path} not found.")

    return (platform_tts_path, platform_tts)


def random_choice_music(music, subreddit_music_type):
    available_music = [(link, volume) for link, volume, music_type in music if music_type == subreddit_music_type]

    if available_music:
        random_song = random.choice(available_music)
        resource_music_link = random_song[0]
        resource_music_volume = random_song[1]
        return resource_music_link, resource_music_volume

    else:
        return None, None


def remove_format_characters(text):
    return ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C')
