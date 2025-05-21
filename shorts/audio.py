import os
from contextlib import ExitStack

import ffmpeg

from shorts.config import _temp_path
from shorts.utils import _clean_up


def _audio(submission: dict, tts_tracks: dict, **kwargs) -> None:
    title_track = tts_tracks.get('title_track', '')
    comment_track = tts_tracks.get('comment_track', '')
    content_track = tts_tracks.get('content_track', '')
    input_track = tts_tracks.get('input_track', '')
    platform_track = tts_tracks.get('platform_track', '')

    tts_combined = os.path.join(_temp_path, 'ttsoutput', 'combined.mp3')

    tracks = []

    for key, path in tts_tracks.items():
        if path == '' or path is None:
            continue

        if not os.path.exists(path):
            raise ValueError(f"track does not exist: {path}")

    with ExitStack() as stack:
        stack.callback(_clean_up, [
            input_track,
            comment_track,
            content_track,
            platform_track
        ])

        silent_audio = ffmpeg.input(
            'aevalsrc=0:d={}'.format(.5), f='lavfi'
        )

        if kwargs.get('input') != '':
            custom_input = ffmpeg.input(input_track)
            tracks.append(custom_input)

        else:
            title_input = ffmpeg.input(title_track)
            tracks.append(title_input)

            comment_input = ffmpeg.input(comment_track)
            # comment_audio = comment_input.audio.filter('volume', 1.4)

            if submission.get('text') != '':
                content_input = ffmpeg.input(content_track)
                tracks.append(silent_audio)
                tracks.append(content_input)

            tracks.append(silent_audio)
            tracks.append(comment_input)

        if kwargs.get('platform') != 'video':
            platform_input = ffmpeg.input(platform_track)
            # platform_audio = platform_input.audio.filter('volume', 1.5)
            tracks.append(silent_audio)
            tracks.append(platform_input)

        (
            ffmpeg
            .concat(
                *tracks,
                n=len(tracks),
                v=0,
                a=1
            )
            .output(tts_combined)
            .run(overwrite_output=True)
        )

    return
