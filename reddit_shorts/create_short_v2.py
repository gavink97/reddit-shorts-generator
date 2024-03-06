import os
import whisper
import math
import random
import ffmpeg

from whisper.utils import get_writer

from reddit_shorts.config import project_path
from reddit_shorts.utils import random_choice_music


def get_audio_duration(track: ffmpeg.Stream) -> float:
    probe = ffmpeg.probe(track)
    audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    duration = float(audio_info['duration'])
    return duration


def get_video_duration(track: ffmpeg.Stream) -> float:
    probe = ffmpeg.probe(track)
    video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    duration = float(video_info['duration'])
    return duration


def create_short_video(footage: list, music: list, submission_author: str, submission_text: str, narrator_title_track, narrator_content_track, commentor_track, platform_tts_track, subreddit_music_type) -> str:
    # rewrite into smaller functions
    # figure out problem with inputs (ffmpeg)
    # figure out how to make ffmpeg write to a log instead of printing
    submission_image = f"{project_path}/temp/images/{submission_author}.png"
    short_file_path = f"{project_path}/temp/uploads/{submission_author}.mp4"
    tts_combined = f"{project_path}/temp/ttsoutput/combined.mp3"
    music_looped = f"{project_path}/temp/music_looped.mp3"
    processed_music = f"{project_path}/temp/music_processed.mp3"
    mixed_audio_file = f'{project_path}/temp/mixed_audio.mp3'
    tts_combined_srt = f"{project_path}/temp/ttsoutput/combined.srt"
    tts_combined_dir = f"{project_path}/temp/ttsoutput/"

    random_video = random.choice(footage)
    # resource_music_link = music[2][0]
    # resource_music_volume = music[2][1]

    resource_music_link, resource_music_volume = random_choice_music(music, subreddit_music_type)

    if submission_text == "":
        narrator_title = ffmpeg.input(narrator_title_track)
        commentor_audio = ffmpeg.input(commentor_track)
        platform_tts_audio = ffmpeg.input(platform_tts_track)

        commentor_audio = commentor_audio.audio.filter('volume', 1.4)
        platform_tts_audio = platform_tts_audio.filter('volume', 1.5)

        space_between_tts = .5

        narrator_title_duration = float(get_audio_duration(narrator_title_track))
        commentor_audio_duration = float(get_audio_duration(commentor_track))
        platform_tts_audio_duration = float(get_audio_duration(platform_tts_track))
        resource_video_duration = float(get_video_duration(random_video))

        narrator_title_duration_floor = math.floor(narrator_title_duration + space_between_tts)
        commentor_audio_duration_floor = math.floor(commentor_audio_duration + space_between_tts)
        platform_tts_audio_duration_floor = math.floor(platform_tts_audio_duration)
        resource_video_duration_floor = math.floor(resource_video_duration)

        soundduration = narrator_title_duration_floor + commentor_audio_duration_floor + platform_tts_audio_duration_floor + 2
        point = random.randint(0, resource_video_duration_floor - soundduration)

        silent_audio = ffmpeg.input('aevalsrc=0:d={}'.format(space_between_tts), f='lavfi')

        merged_audio, _ = (
            ffmpeg
            .concat(narrator_title,
                    silent_audio,
                    commentor_audio,
                    silent_audio,
                    platform_tts_audio,
                    n=5,
                    v=0,
                    a=1
                    )
            .output(tts_combined)
            .run(overwrite_output=True)
        )

    else:
        narrator_title = ffmpeg.input(narrator_title_track)
        narrator_content = ffmpeg.input(narrator_content_track)
        commentor_audio = ffmpeg.input(commentor_track)
        platform_tts_audio = ffmpeg.input(platform_tts_track)

        commentor_audio = commentor_audio.audio.filter('volume', 1.4)
        platform_tts_audio = platform_tts_audio.filter('volume', 1.5)

        space_between_tts = .5

        narrator_title_duration = float(get_audio_duration(narrator_title_track))
        narrator_content_duration = float(get_audio_duration(narrator_content_track))
        commentor_audio_duration = float(get_audio_duration(commentor_track))
        platform_tts_audio_duration = float(get_audio_duration(platform_tts_track))
        resource_video_duration = float(get_video_duration(random_video))

        narrator_title_duration = math.floor(narrator_title_duration + space_between_tts)
        narrator_content_duration = math.floor(narrator_content_duration + space_between_tts)
        commentor_audio_duration = math.floor(commentor_audio_duration + space_between_tts)
        platform_tts_audio_duration = math.floor(platform_tts_audio_duration)
        resource_video_duration_floor = math.floor(resource_video_duration)

        soundduration = narrator_title_duration + narrator_content_duration + commentor_audio_duration + platform_tts_audio_duration + 2
        point = random.randint(0, resource_video_duration_floor - soundduration)

        silent_audio = ffmpeg.input('aevalsrc=0:d={}'.format(space_between_tts), f='lavfi')

        merged_audio, _ = (
            ffmpeg
            .concat(
                narrator_title,
                silent_audio,
                narrator_content,
                silent_audio,
                commentor_audio,
                silent_audio,
                platform_tts_audio,
                n=7,
                v=0,
                a=1
                )
            .output(tts_combined)
            .run(overwrite_output=True)
        )

    writer_options = {
        "max_line_count": 1,
        "max_words_per_line": 1
    }

    whisper_model = whisper.load_model("tiny.en", device="cpu")
    tts_combined_transcribed = whisper_model.transcribe(tts_combined, language="en", fp16=False, word_timestamps=True, task="transcribe")
    writer = get_writer("srt", tts_combined_dir)
    writer(tts_combined_transcribed, tts_combined, writer_options)

    music_track = ffmpeg.input(resource_music_link)
    music_duration = float(get_audio_duration(resource_music_link))

    if music_duration < soundduration:
        loops = int(soundduration / music_duration) + 1
        crossfade_duration = 10

        inputs = []
        for n in range(loops):
            inputs.append(ffmpeg.input(resource_music_link))

        output = ffmpeg.filter(
            inputs,
            'acrossfade',
            d=crossfade_duration,
            c1='tri',
            c2='tri'
            ).output(music_looped)

        ffmpeg.run(output, overwrite_output=True)

        (
            ffmpeg
            .input(music_looped)
            .filter('atrim', start=0, end=soundduration)
            .filter('volume', resource_music_volume)
            .filter('afade', t='out', st=soundduration-5, d=5)
            .output(processed_music)
            .run(overwrite_output=True)
            )

    else:
        (
            music_track
            .filter('atrim', start=0, end=soundduration)
            .filter('volume', resource_music_volume)
            .filter('afade', t='out', st=soundduration-5, d=5)
            .output(processed_music)
            .run(overwrite_output=True)
            )

    background_music = ffmpeg.input(processed_music)
    concatenated_audio = ffmpeg.input(tts_combined)

    font = "Liberation Sans"

    mixed_audio, _ = (
        ffmpeg
        .filter([concatenated_audio, background_music], 'amix', inputs=2)
        .output(mixed_audio_file)
        .run(overwrite_output=True)
        )

    reddit_image = (
        ffmpeg
        .input(submission_image)
        .filter('scale', '960', '-1')
        )

    resource_video_clipped = (
        ffmpeg
        .input(random_video)
        .filter('crop', 'ih*9/16', 'ih', '(iw-ih*9/16)/2', 0)
        .filter('scale', '1080', '1920')
        .trim(start=point, end=point+soundduration)
        .filter('setpts', 'PTS-STARTPTS')
        )

    mixed_audio_stream = ffmpeg.input(mixed_audio_file)

    combined_video, _ = (
        ffmpeg
        .concat(
            resource_video_clipped,
            mixed_audio_stream,
            v=1,
            a=1
            )
        .filter('fade', type='out', start_time=soundduration-5, duration=5)
        .overlay(reddit_image, x='(W-w)/2', y='(H-h)/2', enable=f'between(t,0,{narrator_title_duration})')
        .drawtext(
            text="@HIDDEN Reddit Shorts",
            fontfile=font,
            fontsize=22,
            fontcolor="white",
            x=700,
            y=180,
            borderw=2,
            bordercolor="black"
        )
        .filter(
            'subtitles',
            f'{tts_combined_srt}',
            force_style=f'''
            MarginV=40,
            Bold=-1,
            Fontname={font},
            Fontsize=50,
            OutlineColour=&H100000000,
            BorderStyle=1,
            Outline=3,
            Shadow=3
            '''
        )
        .output(
            short_file_path,
            t=soundduration)
        .run(overwrite_output=True)
    )

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

    if os.path.exists(tts_combined_srt):
        os.remove(tts_combined_srt)

    if os.path.exists(processed_music):
        os.remove(processed_music)

    if os.path.exists(music_looped):
        os.remove(music_looped)

    if os.path.exists(mixed_audio_file):
        os.remove(mixed_audio_file)

    if os.path.exists(submission_image):
        os.remove(submission_image)

    return short_file_path
