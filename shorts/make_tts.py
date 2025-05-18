import os

from shorts.config import _project_path, _temp_path
from shorts.tiktok_tts import tts
from shorts.utils import _clean_up
from contextlib import ExitStack


def _tts(submission, **kwargs) -> dict:
    if kwargs.get('input') != '':
        return _input_tts(**kwargs)

    else:
        return _submission_tts(submission, **kwargs)


def _input_tts(**kwargs) -> dict:
    session_id = os.environ['TIKTOK_SESSION_ID_TTS']
    platform = kwargs.get("platform")
    user_input = kwargs.get("input")

    # check tiktok_tts.py for a full list of tts voice options
    input_tts = "en_male_narration"
    platform_tts = "en_us_007"
    custom_user_input = False

    ttsout = os.path.join(_temp_path, 'ttsoutput')
    tts_texts = os.path.join(ttsout, 'texts')

    input_track = os.path.join(ttsout, 'custom_input.mp3')
    platform_track = os.path.join(ttsout, 'platform.mp3')

    if os.path.isfile(user_input):
        input_text = user_input

    else:
        input_text = os.path.join(tts_texts, 'custom_input.txt')
        custom_user_input = True

        with open(input_text, 'w', encoding='utf-8') as file:
            file.write(user_input)

    match platform:
        case "tiktok":
            platform_text = os.path.join(_project_path, "tiktok_tts.txt")

        case "youtube":
            platform_text = os.path.join(_project_path, "youtube_tts.txt")

        case "video" | _:
            platform_track = ''

    with ExitStack() as stack:
        if custom_user_input:
            stack.callback(_clean_up, input_text)

        tts(session_id=session_id, text_speaker=input_tts,
            file=input_text, filename=input_track)

        if platform != 'video':
            tts(session_id=session_id, text_speaker=platform_tts,
                file=platform_text, filename=platform_track)

    return {
        'input_track': input_track,
        'platform_track': platform_track
    }


def _submission_tts(submission, **kwargs) -> dict:
    session_id = os.environ['TIKTOK_SESSION_ID_TTS']

    platform = kwargs.get("platform")

    author = submission.get('author')
    content = submission.get('text')
    comment_author = submission.get('top_comment_author')

    # check tiktok_tts.py for a full list of tts voice options
    tiktok_narrator = "en_male_narration"
    tiktok_commentor = "en_us_009"
    my_tts = "en_us_007"

    ttsout = os.path.join(_temp_path, 'ttsoutput')
    tts_texts = os.path.join(ttsout, 'texts')

    title_track = os.path.join(ttsout, f'{author}_title.mp3')
    content_track = os.path.join(ttsout, f'{author}_content.mp3')
    comment_track = os.path.join(ttsout, f'{comment_author}.mp3')
    platform_track = os.path.join(ttsout, 'platform.mp3')

    title_text = os.path.join(tts_texts, f'{author}_title.txt')
    content_text = os.path.join(tts_texts, f'{author}_content.txt')
    comment_text = os.path.join(tts_texts, f'{comment_author}.txt')

    match platform:
        case "tiktok":
            platform_text = os.path.join(_project_path, "tiktok_tts.txt")

        case "youtube":
            platform_text = os.path.join(_project_path, "youtube_tts.txt")

        case "video" | _:
            platform_track = ''

    with ExitStack() as stack:
        stack.callback(_clean_up, [
            title_text,
            content_text,
            comment_text
        ])

        tts(session_id=session_id, text_speaker=tiktok_narrator,
            file=title_text, filename=title_track)

        tts(session_id=session_id, text_speaker=tiktok_commentor,
            file=comment_text, filename=comment_track)

        if content != "":
            tts(session_id=session_id, text_speaker=tiktok_narrator,
                file=content_text, filename=content_track)
        else:
            content_track = ''

        if platform != 'video':
            tts(session_id=session_id, text_speaker=my_tts,
                file=platform_text, filename=platform_track)

    return {
        'title_track': title_track,
        'content_track': content_track,
        'comment_track': comment_track,
        'platform_track': platform_track
    }
