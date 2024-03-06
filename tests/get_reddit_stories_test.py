from reddit_shorts.get_reddit_stories import connect_to_reddit, get_story_from_reddit
from reddit_shorts.config import subreddits
import praw
import os
from dotenv import load_dotenv
import pytest
from reddit_shorts.utils import tts_for_platform


@pytest.fixture
def load_credentials():
    load_dotenv()
    reddit_client_id = os.environ['REDDIT_CLIENT_ID']
    reddit_client_secret = os.environ['REDDIT_CLIENT_SECRET']
    return reddit_client_id, reddit_client_secret


def test_connect_to_reddit(load_credentials):
    reddit_client_id, reddit_client_secret = load_credentials
    reddit_instance = connect_to_reddit(reddit_client_id, reddit_client_secret)

    assert isinstance(reddit_instance, praw.Reddit)


def test_get_story_from_reddit(load_credentials):
    reddit = None
    platform = 'youtube'
    (platform_tts_path, platform_tts) = tts_for_platform(platform)

    get_story_from_reddit(subreddits, platform_tts, reddit, platform)
