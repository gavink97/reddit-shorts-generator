import datetime
from moviepy.editor import VideoFileClip


def split_string_at_space(text, index):
    while index >= 0 and text[index] != ' ':
        index -= 1
    return index


def abbreviate_number(number):
    number = int(number)
    if number >= 10**9:
        return '{:.1f}B'.format(number / 10**9)
    elif number >= 10**6:
        return '{:.1f}M'.format(number / 10**6)
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


def check_video_fps(footage: []):
    for video in footage:
        check_fps = VideoFileClip(video)
        rate = check_fps.fps

        print(f"FPS : {str(rate)}")

        if rate != 30:
            check_fps.write_videofile(video, fps=30)
