import os
import whisper_timestamped
import moviepy.video.fx.all as vfx
import math
import random

from moviepy.editor import CompositeVideoClip, CompositeAudioClip, TextClip, AudioFileClip, VideoFileClip, ImageClip
from moviepy.audio.fx.volumex import volumex
from moviepy.audio.fx.all import audio_fadeout
from moviepy.video.fx.resize import resize
from moviepy.video.fx.fadeout import fadeout

from config import launcher_path
from scripts.minor_operations import random_choice_music


def create_short_video(footage: [], music: [], submission_author, submission_text, narrator_title_track, narrator_content_track, commentor_track, platform_tts_track, subreddit_music_type):
    # rewrite into smaller functions
    # fix bug with whisper not always giving subtitles
    # fix ffmpeg bug on tts
    # migrate to ffmpeg-python (maybe)
    submission_image = f"{launcher_path}/temp/images/{submission_author}.png"
    short_file_path = f"{launcher_path}/temp/uploads/{submission_author}.mp4"
    tts_combined = f"{launcher_path}/temp/ttsoutput/combined.mp3"

    random_video = random.choice(footage)
    # resource_music_link, resource_music_volume, resource_music_type = random.choice(music)

    resource_music_link, resource_music_volume = random_choice_music(music, subreddit_music_type)

    # resource_music_link = music[0][0]
    # resource_music_volume = music[0][1]

    if submission_text == "":
        narrator_audio = AudioFileClip(narrator_title_track)
        commentor_audio = AudioFileClip(commentor_track)
        platform_tts_audio = AudioFileClip(platform_tts_track)

        narrator_audio.set_start(0.35)
        narrator_audio.set_end(narrator_audio.duration - 0.35)

        commentor_audio.set_start(0.35)
        commentor_audio.set_end(commentor_audio.duration - 0.35)
        commentor_audio_adjusted = volumex(commentor_audio, 1.4)

        platform_tts_audio.set_start(0.35)
        platform_tts_audio.set_end(platform_tts_audio.duration - 0.35)
        platform_tts_audio_adjusted = volumex(platform_tts_audio, 1.5)

        space_between_tts = 1

        narrator_audio_duration = math.floor(narrator_audio.duration + space_between_tts)
        commentor_audio_duration = math.floor(commentor_audio.duration + space_between_tts)
        platform_tts_audio_duration = math.floor(platform_tts_audio.duration)

        soundduration = narrator_audio_duration + commentor_audio_duration + platform_tts_audio_duration + 2
        calculating_random_video_duration = VideoFileClip(random_video)  # can probably refactor this
        resource_video_duration = math.floor(calculating_random_video_duration.duration)

        point = random.randint(0, resource_video_duration - soundduration)

        music_track = AudioFileClip(resource_music_link).subclip(0, soundduration)
        music_track_adjusted = volumex(music_track, resource_music_volume)
        music_track_faded = audio_fadeout(music_track_adjusted, 5)

        tracks_mixed = CompositeAudioClip([narrator_audio,
                                           commentor_audio_adjusted.set_start(narrator_audio_duration),
                                           platform_tts_audio_adjusted.set_start(narrator_audio_duration + commentor_audio_duration),
                                           music_track_faded])

        tts_only = CompositeAudioClip([narrator_audio,
                                       commentor_audio_adjusted.set_start(narrator_audio_duration),
                                       platform_tts_audio_adjusted.set_start(narrator_audio_duration + commentor_audio_duration)])

        reddit_image = ImageClip(submission_image).set_duration(narrator_audio_duration)

    else:
        narrator_title_audio = AudioFileClip(narrator_title_track)
        narrator_content_audio = AudioFileClip(narrator_content_track)
        commentor_audio = AudioFileClip(commentor_track)
        platform_tts_audio = AudioFileClip(platform_tts_track)

        narrator_title_audio.set_start(0.35)
        narrator_title_audio.set_end(narrator_title_audio.duration - 0.35)

        narrator_content_audio.set_start(0.35)
        narrator_content_audio.set_end(narrator_content_audio.duration - 0.35)

        commentor_audio.set_start(0.35)
        commentor_audio.set_end(commentor_audio.duration - 0.35)
        commentor_audio_adjusted = volumex(commentor_audio, 1.4)

        platform_tts_audio.set_start(0.35)
        platform_tts_audio.set_end(platform_tts_audio.duration - 0.35)
        platform_tts_audio_adjusted = volumex(platform_tts_audio, 1.5)

        space_between_tts = 1

        narrator_title_audio_duration = math.floor(narrator_title_audio.duration + space_between_tts)
        narrator_content_audio_duration = math.floor(narrator_content_audio.duration + space_between_tts)
        commentor_audio_duration = math.floor(commentor_audio.duration + space_between_tts)
        platform_tts_audio_duration = math.floor(platform_tts_audio.duration)

        soundduration = narrator_title_audio_duration + narrator_content_audio_duration + commentor_audio_duration + platform_tts_audio_duration + 3
        calculating_random_video_duration = VideoFileClip(random_video)
        resource_video_duration = math.floor(calculating_random_video_duration.duration)

        point = random.randint(0, resource_video_duration - soundduration)

        music_track = AudioFileClip(resource_music_link).subclip(0, soundduration)
        music_track_adjusted = volumex(music_track, resource_music_volume)
        music_track_faded = audio_fadeout(music_track_adjusted, 5)

        tracks_mixed = CompositeAudioClip([narrator_title_audio,
                                           narrator_content_audio.set_start(narrator_title_audio_duration),
                                           commentor_audio_adjusted.set_start(narrator_title_audio_duration + narrator_content_audio_duration),
                                           platform_tts_audio_adjusted.set_start(narrator_title_audio_duration + narrator_content_audio_duration + commentor_audio_duration),
                                           music_track_faded])

        tts_only = CompositeAudioClip([narrator_title_audio,
                                       narrator_content_audio.set_start(narrator_title_audio_duration),
                                       commentor_audio_adjusted.set_start(narrator_title_audio_duration + narrator_content_audio_duration),
                                       platform_tts_audio_adjusted.set_start(narrator_title_audio_duration + narrator_content_audio_duration + commentor_audio_duration)])

        reddit_image = ImageClip(submission_image).set_duration(narrator_title_audio_duration)

    tts_only.write_audiofile(tts_combined, fps=44100)
    whisper_model = whisper_timestamped.load_model("tiny.en", device="cpu")
    track_mixed_transcribed = whisper_timestamped.transcribe(whisper_model, tts_combined, language="en", fp16=False)

    channel_watermark = TextClip("@HIDDEN Reddit", fontsize=10, color="white").set_position((360, 20)).set_duration(soundduration)

    reddit_image_resized = resize(reddit_image, 0.16)
    reddit_image_resized = reddit_image_resized.set_pos(("center", 200))

    resource_video_clipped = VideoFileClip(random_video).subclip(point, point + soundduration)
    (w, h) = resource_video_clipped.size
    resource_video_clipped = vfx.crop(resource_video_clipped, width=480, height=720, x_center=w/2, y_center=h/2)
    resource_video_clipped.audio = tracks_mixed

    subtitles = []
    subtitles.append(resource_video_clipped)
    subtitles.append(channel_watermark)
    subtitles.append(reddit_image_resized)
    font = "arialbd.ttf"

    for segment in track_mixed_transcribed["segments"]:
        for word in segment["words"]:
            subtitle_text = word["text"].upper()
            subtitle_start = word["start"]
            subtitle_end = word["end"]
            subtitle_duration = subtitle_end - subtitle_start
            subtitle_track = TextClip(txt=subtitle_text, fontsize=50, font=font, color="white")
            subtitle_track = subtitle_track.set_start(subtitle_start).set_duration(subtitle_duration).set_pos(("center", 550))
            subtitle_track_stroke = TextClip(txt=subtitle_text, fontsize=50, font=font, color="black", stroke_width=5, stroke_color="black")
            subtitle_track_stroke = subtitle_track_stroke.set_start(subtitle_start).set_duration(subtitle_duration).set_pos(("center", 548))

            subtitles.append(subtitle_track_stroke)
            subtitles.append(subtitle_track)

    resource_video_clipped = CompositeVideoClip(subtitles)
    resource_video_clipped_fx = fadeout(resource_video_clipped, 5)
    resource_video_clipped_fx.write_videofile(short_file_path, fps=30, codec="libx264", audio_codec="aac")

    if os.path.exists(narrator_title_track):
        os.remove(narrator_title_track)

    if os.path.exists(narrator_content_track):
        os.remove(narrator_content_track)

    if os.path.exists(commentor_track):
        os.remove(commentor_track)

    if os.path.exists(platform_tts_track):
        os.remove(platform_tts_track)

    if os.path.exists(tts_combined):
        os.remove(tts_combined)

    if os.path.exists(submission_image):
        os.remove(submission_image)

    return short_file_path
