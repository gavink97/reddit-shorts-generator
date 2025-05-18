import os
import whisper
from contextlib import ExitStack
import math
import random
import ffmpeg

from shorts.audio import _audio
from whisper.utils import get_writer

from shorts.config import _footage, _music, _CHANNEL_NAME, _temp_path
from shorts.utils import random_choice_music, _clean_up, _get_audio_duration, _get_video_duration

# write a function to measure the loudness of an audio file to properly setup loudness of music / voice over


# split video func, write verify files func
def _create_video(submission: dict, tts_tracks: dict, **kwargs) -> str:
    FONT = "Liberation Sans"

    _uploads = os.path.join(_temp_path, 'uploads')

    #split = kwargs.get('split')
    split = False
    user_video = kwargs.get('video')
    user_input = kwargs.get('input')
    if user_input == '':
        author = submission.get('author')
        title_track = tts_tracks.get('title_track')
        title_duration = float(_get_audio_duration(title_track))
        image = os.path.join(_temp_path, 'images', f'{author}.png')
        short_file_path = os.path.join(_uploads, f'{author}.mp4')
        music_type = submission.get('music_type', 'general')

    else:
        short_file_path = os.path.join(_uploads, 'custom_input.mp4')
        music_type = 'general'
        title_track = ''
        image = ''

    music_looped = os.path.join(_temp_path, 'music_looped.mp3')
    processed_music = os.path.join(_temp_path, 'music_processed.mp3')
    mixed_track = os.path.join(_temp_path, 'mixed_audio.mp3')

    ttsoutput_dir = os.path.join(_temp_path, 'ttsoutput')
    tts_combined = os.path.join(ttsoutput_dir, 'combined.mp3')
    combined_srt = os.path.join(ttsoutput_dir, 'combined.srt')

    temp_files = [
        title_track,
        image,
        tts_combined,
        music_looped,
        processed_music,
        combined_srt,
        mixed_track
    ]

    _audio(submission, tts_tracks, **kwargs)
    tts_duration = math.floor(_get_audio_duration(tts_combined)) + 1

    if kwargs.get('music') == '':
        music, music_volume = random_choice_music(_music, music_type)
    else:
        music = kwargs.get('music')
        music_volume = 0.4

    playhead = 0

    # start here
    match f"{split}-{user_video != []}":
        # split screen + customer user video
        case 'true-true':
            footage = user_video  # array of len 2 max
            # two video clips will require two video durations for playhead

        # split screen default video
        case 'true-false':
            return

        # single screen custom user video
        case 'false-true':
            footage = user_video[0]
            video_duration = math.floor(_get_video_duration(footage)) + 1
            if video_duration < tts_duration:
                # this should probably do something else
                raise Exception(f"Video is too short tss: {tts_duration}")

            playhead = random.randint(0, video_duration - tts_duration)

        # single screen default video
        case 'false-false' | _:
            footage = random.choice(_footage)
            if not os.path.exists(footage):
                raise ValueError(f"video source does not exist: {footage}")

            video_duration = math.floor(_get_video_duration(footage)) + 1
            if video_duration < tts_duration:
                while video_duration < tts_duration:
                    footage = random.choice(_footage)
                    video_duration = math.floor(_get_video_duration(footage)) + 1

            playhead = random.randint(0, video_duration - tts_duration)

    writer_options = {
        "max_line_count": 1,
        "max_words_per_line": 1
    }

    whisper_model = whisper.load_model("tiny.en", device="cpu")
    tts_transcribed = whisper_model.transcribe(
        tts_combined,
        language="en",
        fp16=False,
        word_timestamps=True,
        task="transcribe"
    )

    fade = 5

    music_duration = math.floor(_get_audio_duration(music)) + 1
    if tts_duration < fade:
        tts_duration = tts_duration + (fade - tts_duration)

    #
    #
    # verify files here
    if not os.path.exists(tts_combined):
        raise ValueError(f"Missing combined track: {tts_combined}")

    with ExitStack() as stack:
        stack.callback(_clean_up, temp_files)

        writer = get_writer("srt", ttsoutput_dir)
        writer(tts_transcribed, tts_combined, writer_options)

        music_track = ffmpeg.input(music)

        if music_duration < tts_duration:
            loops = int(tts_duration / music_duration) + 1
            crossfade_duration = 10

            inputs = [ffmpeg.input(music) for _ in range(loops)]

            chain = inputs[0]
            for next_input in inputs[1:]:
                chain = ffmpeg.filter(
                    [chain, next_input],
                    'acrossfade',
                    d=crossfade_duration,
                    c1='tri',
                    c2='tri'
                )
            (
                ffmpeg
                .output(chain, music_looped)
                .run(overwrite_output=True)
            )

            music_track = ffmpeg.input(music_looped)

        (
            music_track
            .filter('atrim', start=0, end=tts_duration)
            .filter('volume', music_volume)
            .filter('afade', t='out', st=tts_duration-fade, d=fade)
            .output(processed_music)
            .run(overwrite_output=True)
        )

        if not os.path.exists(processed_music):
            raise ValueError(f"Missing music track: {processed_music}")

        background_music = ffmpeg.input(processed_music)
        tts = ffmpeg.input(tts_combined)

        (
            ffmpeg
            .filter([tts, background_music], 'amix', inputs=2)
            .output(mixed_track)
            .run(overwrite_output=True)
        )

        if not os.path.exists(mixed_track):
            raise ValueError(f"Missing mixed_track: {mixed_track}")

        mixed_audio = ffmpeg.input(mixed_track)

        # start here
        if not split:
            clipped_footage = (
                ffmpeg
                .input(footage)
                .filter('crop', 'ih*9/16', 'ih', '(iw-ih*9/16)/2', 0)
                .filter('scale', '1080', '1920')
                .trim(start=playhead, end=playhead+tts_duration)
                .filter('setpts', 'PTS-STARTPTS')
            )
        else:
            # have a second piece of footage
            # have a second playhead
            clipped_footage = (
                ffmpeg
                .input(footage)
                .filter('crop', 'ih*9/16', 'ih', '(iw-ih*9/16)/2', 0)
                .filter('scale', '1080', '1920')
                .trim(start=playhead, end=playhead+tts_duration)
                .filter('setpts', 'PTS-STARTPTS')
            )

        master = ffmpeg.concat(
                clipped_footage,
                mixed_audio,
                v=1,
                a=1
            )

        master = master.filter(
                'fade',
                type='out',
                start_time=tts_duration-fade,
                duration=fade
            )

        if user_input == '':
            reddit_image = (
                ffmpeg
                .input(image)
                .filter('scale', '960', '-1')
            )

            master = master.overlay(
                reddit_image,
                x='(W-w)/2',
                y='(H-h)/2',
                enable=f'between(t,0,{title_duration})'
            )

        master = master.drawtext(
                text=_CHANNEL_NAME,
                fontfile=FONT,
                fontsize=22,
                fontcolor="white",
                x=700,
                y=180,
                borderw=2,
                bordercolor="black"
            )
        master = master.filter(
                'subtitles',
                combined_srt,
                force_style=f'''
                    MarginV=40,
                    Bold=-1,
                    Fontname={FONT},
                    Fontsize=50,
                    OutlineColour=&H100000000,
                    BorderStyle=1,
                    Outline=3,
                    Shadow=3
                '''
            )

        master.output(
            short_file_path,
            t=tts_duration
        ).run(overwrite_output=True)

    return short_file_path
