import os
import random
import re

import ffmpeg

from shorts.config import bad_words_list


def random_choice_music(music: list, subreddit_music_type: str):
    available_music = [(link, volume) for link, volume, music_type in music if music_type == subreddit_music_type]

    if available_music:
        random_song = random.choice(available_music)
        resource_music_link = random_song[0]
        resource_music_volume = random_song[1]
        return resource_music_link, resource_music_volume

    else:
        return None, None


def contains_bad_words(text: str, bad_words: list = bad_words_list) -> bool:
    text = text.lower()
    bad_words_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(word) for word in bad_words) + r')\b', re.IGNORECASE)

    if bad_words_pattern.search(text):
        return True
    return False


def _get_audio_duration(track: ffmpeg.Stream) -> float:
    probe = ffmpeg.probe(track)
    info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    duration = float(info['duration'])
    return duration


def _get_video_duration(track: ffmpeg.Stream) -> float:
    probe = ffmpeg.probe(track)
    info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    duration = float(info['duration'])
    return duration


def _clean_up(files: list | str) -> None:
    if isinstance(files, str):
        try:
            os.remove(files)
        except Exception:
            return

    else:
        for path in files:
            try:
                os.remove(path)
            except Exception:
                pass


def _measure_loudness(track: ffmpeg.Stream) -> dict:
    try:
        _, err = (
            ffmpeg
            .filter(
                track,
                'loudnorm',
                I=-16,
                dual_mono=True,
                TP=-1.5,
                LRA=11,
                print_format='summary')
            .output('pipe:', format="null")
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise Exception(e.stderr.decode())

    out = err.decode().split('\n')

    loudness = {
        'input_integrated': None,
        'input_true_peak': None,
        'input_lra': None,
        'input_threshold': None,
    }

    for line in out:
        if 'Input Integrated' in line:
            loudness['input_integrated'] = line.split()[-2]
        elif 'Input True Peak' in line:
            loudness['input_true_peak'] = line.split()[-2]
        elif 'Input LRA' in line:
            loudness['input_lra'] = line.split()[-2]
        elif 'Input Threshold' in line:
            loudness['input_threshold'] = line.split()[-2]

    return loudness


def _normalize(track: ffmpeg.Stream, target: int = -16) -> ffmpeg.Stream:
    if target > 0:
        raise Exception("target must be a negative number")

    return track.filter(
        'loudnorm',
        I=target,
        dual_mono=True,
        TP=-1.5,
        LRA=11
    )
