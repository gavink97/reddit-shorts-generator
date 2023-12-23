import os
import ssl
from dotenv import load_dotenv
from scripts.tiktok_tts import tts
from config import launcher_path

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
tiktok_session_id = os.environ['TIKTOK_SESSION_ID_TTS']


def generate_tiktok_tts(submission_title, submission_author, submission_text, top_comment_body, top_comment_author):
    # try using other TTSs to see if there are better results
    # make reading tts file into a seperate function to handle tiktok or youtube tts

    youtube_tts_path = os.path.join(launcher_path, "youtube_tts.txt")

    try:
        with open(youtube_tts_path, 'r') as file:
            youtube_tts = file.read()

    except FileNotFoundError:
        print(f"File {youtube_tts_path} not found.")

    tiktok_narrator = "en_us_001"
    tiktok_commentor = "en_us_006"
    my_tts = "en_us_007"

    tts_character_limit = 200

    narrator_title_track = f"{launcher_path}/temp/ttsoutput/{submission_author}_title.mp3"
    narrator_content_track = f"{launcher_path}/temp/ttsoutput/{submission_author}_content.mp3"
    commentor_track = f"{launcher_path}/temp/ttsoutput/{top_comment_author}.mp3"
    youtube_track = f"{launcher_path}/temp/ttsoutput/youtube.mp3"

    submission_title_path = f'{launcher_path}/temp/ttsoutput/texts/{submission_author}_title.txt'
    top_comment_body_path = f'{launcher_path}/temp/ttsoutput/texts/{top_comment_author}.txt'
    submission_text_path = f'{launcher_path}/temp/ttsoutput/texts/{submission_author}_content.txt'

    # YouTube Only TTS
    if len(youtube_tts) > tts_character_limit:
        tts(session_id=tiktok_session_id, text_speaker=my_tts,
            file=youtube_tts_path, filename=youtube_track)

    else:
        tts(session_id=tiktok_session_id, text_speaker=my_tts,
            req_text=youtube_tts, filename=youtube_track)

    # Submission Title TTS
    if len(submission_title) > tts_character_limit:
        tts(session_id=tiktok_session_id, text_speaker=tiktok_narrator,
            file=submission_title_path, filename=narrator_title_track)

    else:
        tts(session_id=tiktok_session_id, text_speaker=tiktok_narrator,
            req_text=submission_title, filename=narrator_title_track)

    # Submission Text TTS
    if submission_text != "":
        if len(submission_text) > tts_character_limit:
            tts(session_id=tiktok_session_id, text_speaker=tiktok_narrator,
                file=submission_text_path, filename=narrator_content_track)

        else:
            tts(session_id=tiktok_session_id, text_speaker=tiktok_narrator,
                req_text=submission_text, filename=narrator_content_track)

    # Top Comment Body TTS
    if len(top_comment_body) > tts_character_limit:
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

    return (narrator_title_track,
            narrator_content_track,
            commentor_track,
            youtube_track)
