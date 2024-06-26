import os
import ssl

from dotenv import load_dotenv

from reddit_shorts.config import project_path
from reddit_shorts.tiktok_tts import tts
from reddit_shorts.utils import tts_for_platform


ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
tiktok_session_id = os.environ['TIKTOK_SESSION_ID_TTS']


# rewrite to ignore platform_tts if video
# update tiktok_tts module
def generate_tiktok_tts(**kwargs) -> dict:
    submission_author = kwargs.get('author')
    submission_title = kwargs.get('title')
    submission_text = kwargs.get('text')
    top_comment_author = kwargs.get('top_comment_author')
    top_comment_body = kwargs.get('top_comment_body')
    (platform_tts_path, platform_tts) = tts_for_platform(**kwargs)

    # check tiktok_tts.py for a full list of tts voice options
    tiktok_narrator = "en_male_narration"
    tiktok_commentor = "en_us_009"
    my_tts = "en_us_007"

    tts_character_limit = 200

    narrator_title_track = f"{project_path}/temp/ttsoutput/{submission_author}_title.mp3"
    narrator_content_track = f"{project_path}/temp/ttsoutput/{submission_author}_content.mp3"
    commentor_track = f"{project_path}/temp/ttsoutput/{top_comment_author}.mp3"
    platform_tts_track = f"{project_path}/temp/ttsoutput/youtube.mp3"

    submission_title_path = f'{project_path}/temp/ttsoutput/texts/{submission_author}_title.txt'
    submission_text_path = f'{project_path}/temp/ttsoutput/texts/{submission_author}_content.txt'
    top_comment_body_path = f'{project_path}/temp/ttsoutput/texts/{top_comment_author}.txt'

    # Platform TTS
    if len(platform_tts) >= tts_character_limit:
        tts(session_id=tiktok_session_id, text_speaker=my_tts,
            file=platform_tts_path, filename=platform_tts_track)

    else:
        tts(session_id=tiktok_session_id, text_speaker=my_tts,
            req_text=platform_tts, filename=platform_tts_track)

    # Submission Title TTS
    if len(submission_title) >= tts_character_limit:
        tts(session_id=tiktok_session_id, text_speaker=tiktok_narrator,
            file=submission_title_path, filename=narrator_title_track)

    else:
        tts(session_id=tiktok_session_id, text_speaker=tiktok_narrator,
            req_text=submission_title, filename=narrator_title_track)

    # Submission Text TTS
    if submission_text == " ":
        submission_text.strip()

    if submission_text != "":
        if len(submission_text) >= tts_character_limit:
            tts(session_id=tiktok_session_id, text_speaker=tiktok_narrator,
                file=submission_text_path, filename=narrator_content_track)

        else:
            tts(session_id=tiktok_session_id, text_speaker=tiktok_narrator,
                req_text=submission_text, filename=narrator_content_track)

    # Top Comment Body TTS
    if len(top_comment_body) >= tts_character_limit:
        tts(session_id=tiktok_session_id, text_speaker=tiktok_commentor,
            file=top_comment_body_path, filename=commentor_track)

    else:
        tts(session_id=tiktok_session_id, text_speaker=tiktok_commentor,
            req_text=top_comment_body, filename=commentor_track)

    if os.path.exists(submission_title_path):
        os.remove(submission_title_path)

    if os.path.exists(submission_text_path):
        os.remove(submission_text_path)

    if os.path.exists(top_comment_body_path):
        os.remove(top_comment_body_path)

    return {
        'title_track': narrator_title_track,
        'content_track': narrator_content_track,
        'commentor_track': commentor_track,
        'platform_track': platform_tts_track
    }
