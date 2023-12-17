import os
import sys
import time
import praw
import ssl
import whisper_timestamped
import moviepy.video.fx.all as vfx
import math
import random
import json
import pytz
import datetime
from dotenv import load_dotenv
from praw.models import MoreComments
from tiktok_tts import tts
from moviepy.editor import *
from moviepy.audio.fx.volumex import volumex
from moviepy.audio.fx.all import audio_fadeout
from moviepy.video.fx.resize import resize
from moviepy.video.fx.fadeout import fadeout
from upload_to_youtube import initialize_upload, get_authenticated_service
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from PIL import Image, ImageFont, ImageDraw

ssl._create_default_https_context = ssl._create_unverified_context

# launcher_path = sys.argv[0]
launcher_path = "/Users/gavinkondrath/projects/youtube_shorts"

timezone = pytz.timezone('US/Central')
current_time = datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M")

load_dotenv()
reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']
tiktok_session_id = os.environ['TIKTOK_SESSION_ID']
youtube_api_client = os.environ['YOUTUBE_API_CLIENT_ID']
youtube_api_secret = os.environ['YOUTUBE_API_CLIENT_SECRET']

firefox_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"

reddit = praw.Reddit(
        client_id=f"{reddit_client_id}",
        client_secret=f"{reddit_client_secret}",
        user_agent=f"{firefox_user_agent}"
        )


def get_story_from_reddit():
    global submission_subreddit
    global submission_author
    global submission_title
    global submission_score
    global submission_comments_number
    global submission_timestamp
    global top_comment_author
    global top_comment_body
    global tts_character_limit
    global youtube_only_tts

    youtube_tts_file = f"{launcher_path}/youtube_tts.txt"

    try:
        with open(youtube_tts_file, 'r') as file:
            youtube_only_tts = file.read()

    except FileNotFoundError:
        print(f"File {youtube_tts_file} not found.")

    # Make stories taken from reddit more random
    # Make an array of subreddits to take the stories from

    tts_character_limit = 200
    submission_subreddit = "askreddit"
    subreddit = reddit.subreddit(submission_subreddit)
    for submission in subreddit.hot(limit=3):
        submission_author = submission.author
        submission_title = submission.title
        submission_score = submission.score
        submission_comments_number = submission.num_comments
        submission_timestamp = submission.created_utc
        comment_counter = 1
        comment_counter_limit = 10

        print(f"Submissions title length: {len(submission_title)}")
        if len(submission_title) > tts_character_limit:
            with open(f'{launcher_path}/ttsoutput/texts/{submission_author}.txt', 'w', encoding='utf-8') as file:
                file.write(submission_title)

        for top_level_comment in submission.comments:
            if isinstance(top_level_comment, MoreComments):
                continue
            comment_counter += 1
            top_comment_author = top_level_comment.author
            top_comment_body = top_level_comment.body

            print(f"Top Comment length: {len(top_comment_body)}")

            total_length = len(youtube_only_tts) + len(submission_title) + len(top_comment_body)

            print(f"Total length: {total_length}")

            if total_length <= 300 or total_length > 900:
                continue

            else:

                if len(top_comment_body) > tts_character_limit:
                    with open(f'{launcher_path}/ttsoutput/texts/{top_comment_author}.txt', 'w', encoding='utf-8') as file:
                        file.write(top_comment_body)
                        return top_level_comment, submission

            if comment_counter == comment_counter_limit:
                break


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


def generate_reddit_story_image():
    global submission_subreddit
    global submission_author
    global submission_title
    global submission_timestamp
    global submission_score
    global submission_comments_number

    story_template = Image.open(f"{launcher_path}/resources/images/reddit_submission_template.png")
    submission_image = f"{launcher_path}/resources/images/{submission_author}_submission_image.png"

    if len(str(submission_author)) > 22:
        submission_author_formatted = str(submission_author)[:22]
        return submission_author_formatted
    else:
        submission_author_formatted = str(submission_author)

    characters_to_linebreak = 37
    start_index = 0
    chunks = []

    while start_index < len(submission_title):
        end_index = start_index + characters_to_linebreak
        if end_index < len(submission_title):
            end_index = split_string_at_space(submission_title, end_index)
        chunks.append(submission_title[start_index:end_index].strip())
        start_index = end_index + 1

    submission_title_formatted = '\n'.join(chunks)

    line_break_count = submission_title_formatted.count('\n')

    if line_break_count >= 3:
        third_line_break_index = submission_title_formatted.find('\n', submission_title_formatted.find('\n', submission_title_formatted.find('\n') + 1) + 1)
        submission_title_formatted = submission_title_formatted[:third_line_break_index]

    converted_time = datetime.datetime.fromtimestamp(submission_timestamp)
    submission_time_formatted = format_relative_time(converted_time)

    submission_score_formatted = abbreviate_number(submission_score)
    submission_comments_formatted = abbreviate_number(submission_comments_number)

    draw = ImageDraw.Draw(story_template)
    twenty_pt_bold = ImageFont.truetype("arialbd.ttf", 82)
    twenty_pt_reg = ImageFont.truetype("arial.ttf", 82)
    twenty_six_pt_bold = ImageFont.truetype("arialbd.ttf", 110)

    # write function to take into account other subreddits

    subreddit_image_path = f"{launcher_path}/resources/images/askreddit_community.png"
    community_logo = Image.open(subreddit_image_path)
    community_logo = community_logo.resize((244, 244))

    story_template.paste(community_logo, (222, 368), mask=community_logo)

    draw.text((569, 459), submission_author_formatted, (35, 31, 32,), font=twenty_pt_bold)

    author_length = draw.textlength(submission_author_formatted, font=twenty_pt_bold)

    author_length_offset = 569 + author_length

    draw.ellipse(((author_length_offset + 36), 504, (author_length_offset + 50), 518), (35, 31, 32,))

    draw.text(((author_length_offset + 95), 459), submission_time_formatted, (35, 31, 32,), font=twenty_pt_reg)

    draw.multiline_text((236, 672), submission_title_formatted, (35, 31, 32,), font=twenty_six_pt_bold, spacing=43.5)

    draw.text((460, 1253), submission_score_formatted, (35, 31, 32,), font=twenty_pt_bold)

    draw.text((1172, 1253), submission_comments_formatted, (35, 31, 32,), font=twenty_pt_bold)

    story_template.save(submission_image)


def generate_tiktok_tts():
    global submission_title
    global submission_author
    global top_comment_body
    global top_comment_author
    global tts_character_limit
    global narrator_track
    global commentor_track
    global youtube_only_track
    global youtube_tts_file
    global youtube_only_tts

    tiktok_narrator = "en_us_001"
    tiktok_commentor = "en_us_006"
    my_tts = "en_us_007"

    narrator_track = f"{launcher_path}/ttsoutput/{submission_author}.mp3"
    commentor_track = f"{launcher_path}/ttsoutput/{top_comment_author}.mp3"
    youtube_only_track = f"{launcher_path}/ttsoutput/youtube_only.mp3"

    if len(youtube_only_tts) > tts_character_limit:
        tts(session_id=tiktok_session_id, text_speaker=my_tts,
            file=youtube_tts_file, filename=youtube_only_track)

    else:
        tts(session_id=tiktok_session_id, text_speaker=my_tts,
            req_text=youtube_only_tts, filename=youtube_only_track)

    if len(submission_title) > tts_character_limit:
        tts(session_id=tiktok_session_id, text_speaker=tiktok_narrator,
            file=f'{launcher_path}/ttsoutput/texts/{submission_author}.txt', filename=narrator_track)

    else:
        tts(session_id=tiktok_session_id, text_speaker=tiktok_narrator,
            req_text=submission_title, filename=narrator_track)

    if len(top_comment_body) > tts_character_limit:
        tts(session_id=tiktok_session_id, text_speaker=tiktok_commentor,
            file=f'{launcher_path}/ttsoutput/texts/{top_comment_author}.txt', filename=commentor_track)

    else:
        tts(session_id=tiktok_session_id, text_speaker=tiktok_commentor,
            req_text=top_comment_body, filename=commentor_track)


def create_youtube_short():
    global narrator_track
    global commentor_track
    global youtube_only_track
    global youtube_short_file
    global submission_author

    submission_image = f"{launcher_path}/resources/images/{submission_author}_submission_image.png"

    # fix the stupid bug with the audio clip
    # make array of minecraft gameplay / other videos to use for videos
    # make array of music to use for videos that takes volumex into account
    # add gaussian blur effect to beginning of the video
    # style the subtitles better

    short_file_name = f"{submission_author}"
    youtube_short_file = f"{launcher_path}/uploads/youtube/{short_file_name}.mp4"

    minecraft_gameplay = f"{launcher_path}/resources/footage/relaxing_minecraft_parkour.mp4"

    narrator_audio = AudioFileClip(narrator_track)
    commentor_audio = AudioFileClip(commentor_track)
    youtube_only_audio = AudioFileClip(youtube_only_track)

    # this addresses some bug with moviepy
    narrator_audio.set_start(0.35)
    narrator_audio.set_end(narrator_audio.duration - 0.35)
    commentor_audio.set_start(0.35)
    commentor_audio.set_end(commentor_audio.duration - 0.40)
    commentor_audio_adjusted = volumex(commentor_audio, 1.4)
    youtube_only_audio.set_start(0.35)
    youtube_only_audio.set_end(youtube_only_audio.duration - 0.35)
    youtube_only_adjusted = volumex(youtube_only_audio, 1.5)

    space_between_tts = 2

    narrator_audio_duration = math.floor(narrator_audio.duration + space_between_tts)
    commentor_audio_duration = math.floor(commentor_audio.duration + space_between_tts)
    youtube_only_audio_duration = math.floor(youtube_only_audio.duration)

    soundduration = narrator_audio_duration + commentor_audio_duration + youtube_only_audio_duration + 2
    minecraft_video = VideoFileClip(minecraft_gameplay)
    resource_video_duration = math.floor(minecraft_video.duration)

    point = random.randint(0, resource_video_duration - soundduration)

    uplifting_music = f"{launcher_path}/resources/music/uplifting.mp3"

    music_track = AudioFileClip(uplifting_music).subclip(0, soundduration)
    music_track.set_start(0.35)
    music_track.set_end(music_track.duration - 0.35)
    music_track_adjusted = volumex(music_track, 0.3)
    music_track_faded = audio_fadeout(music_track_adjusted, 5)

    tracks_mixed = CompositeAudioClip([narrator_audio,
                                       commentor_audio_adjusted.set_start(narrator_audio_duration),
                                       youtube_only_adjusted.set_start(narrator_audio_duration + commentor_audio_duration),
                                       music_track_faded])

    tts_combined = f"{launcher_path}/ttsoutput/combined.mp3"
    tracks_mixed.write_audiofile(tts_combined, fps=44100)
    whisper_model = whisper_timestamped.load_model("base", device="cpu")
    track_mixed_transcribed = whisper_timestamped.transcribe(whisper_model, tts_combined, language="en", beam_size=5, best_of=5, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), fp16=False)

    channel_watermark = TextClip("@HIDDEN Reddit", fontsize=10, color="white").set_position((360, 20)).set_duration(soundduration)

    reddit_image = ImageClip(submission_image).set_duration(narrator_audio_duration)
    reddit_image_resized = resize(reddit_image, 0.16)
    reddit_image_resized = reddit_image_resized.set_pos(("center", 200))

    resource_video_clipped = VideoFileClip(minecraft_gameplay).subclip(point, point + soundduration)
    (w, h) = resource_video_clipped.size
    resource_video_clipped = vfx.crop(resource_video_clipped, width=480, height=720, x_center=w/2, y_center=h/2)
    resource_video_clipped.audio = tracks_mixed

    subtitles = []
    subtitles.append(resource_video_clipped)
    subtitles.append(channel_watermark)
    subtitles.append(reddit_image_resized)

    for segment in track_mixed_transcribed["segments"]:
        for word in segment["words"]:
            subtitle_text = word["text"].upper()
            subtitle_start = word["start"]
            subtitle_end = word["end"]
            subtitle_duration = subtitle_end - subtitle_start
            subtitle_track = TextClip(txt=subtitle_text, fontsize=50, font="Helvetica-Bold", color="white")
            subtitle_track = subtitle_track.set_start(subtitle_start).set_duration(subtitle_duration).set_pos(("center", 550))
            subtitles.append(subtitle_track)


    resource_video_clipped = CompositeVideoClip(subtitles)
    resource_video_clipped_fx = fadeout(resource_video_clipped, 5)
    resource_video_clipped_fx.write_videofile(youtube_short_file, fps=30)


def create_video_title():
    global submission_title
    global short_video_title
    youtube_title_limit = 100

    youtube_hashtags = "#reddit #askreddit"

    truncation_limit = youtube_title_limit - len(youtube_hashtags) - 4

    if len(submission_title) >= truncation_limit:
        truncated_youtube_title = submission_title[:truncation_limit]
        if truncated_youtube_title.endswith(' '):
            truncated_youtube_title = truncated_youtube_title[:-1]

        short_video_title = f"{truncated_youtube_title}... {youtube_hashtags}"
    else:
        short_video_title = f"{submission_title} {youtube_hashtags}"


def upload_short_to_youtube(youtube_short_file, short_video_title):

    args = argparser.parse_args()
    video_description = ""
    video_category = "24"
    video_keywords = ""
    video_privacy_status = "private"

    youtube = get_authenticated_service(args)

    try:
        initialize_upload(youtube, youtube_short_file, short_video_title, video_description, video_category, video_keywords, video_privacy_status)

    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))


# def clean_up():
    # Delete all files generated when making the video


# replace globals with parameters for each function
get_story_from_reddit()
generate_reddit_story_image()
generate_tiktok_tts()
create_youtube_short()
# create_video_title()
# upload_short_to_youtube(youtube_short_file, short_video_title)
# clean_up()
