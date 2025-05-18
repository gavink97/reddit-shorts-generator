import random
import re
import ffmpeg
import os

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
