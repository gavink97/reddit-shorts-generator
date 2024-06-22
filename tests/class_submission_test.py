from reddit_shorts.class_submission import identify_post_type, Title, qualify_submission, Submission
import pytest
from reddit_shorts.config import subreddits
import random
from praw.models.comment_forest import CommentForest
from datetime import datetime, timezone


@pytest.fixture
def submission_sample():
    current_time_utc = datetime.now(timezone.utc)

    comments = (
        CommentForest({
            'author': 'gavin-kondrath',
            'body': 'Bro if you dont like my program why dont you go ahead and send a pull request to make it better or write your own. Besides, no ones gonna watch your reddit bot youtube shorts anyways',
            'id': 2
        })
    )

    data = {
        'title': 'How do you know this works? This just seems like some shitty code you copied from ChatGPT',
        'selftext': 'Seriously I dont know how anyone here is expected to use this to make money off of youtube. Like come on I dont have the youtube api key',
        'author': 'random-man',
        'created_utc': current_time_utc.timestamp(),
        'id': 1,
        'is_self': True,
        'score': 69,
        'url': 'https://www.reddit.com/r/CasualConversation/comments/1ao0uaq/i_dont_know_how_it_respond_when_a_girl_calls_me/',
        'comments': comments,
        'num_comments': 1
    }

    return data


@pytest.fixture
def kwargs_sample():
    kwargs = {
        'platform': 'tiktok',
        'filter': True
    }

    return kwargs


def test_identify_post_type(submission_sample):
    assert identify_post_type(submission_sample) == Title


def test_process_submission(submission_sample, kwargs=kwargs_sample):
    subreddit = random.choice(subreddits)
    Submission.process_submission(subreddit, submission_sample, **kwargs)


def test_qualify_submission(submission_sample, kwargs=kwargs_sample):
    qualify_submission(submission_sample, **kwargs)
