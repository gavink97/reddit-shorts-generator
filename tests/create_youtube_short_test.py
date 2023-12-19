import create_youtube_short
import pytest

# use command pytest path_to_py -v for verbose tests


def test_get_story():
    assert create_youtube_short.get_story_from_reddit()
