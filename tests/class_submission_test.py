from reddit_shorts.class_submission import identify_post_type, Title


def test_identify_post_type():
    submission_is_self = True
    submission_text = ''
    submission_url = 'https://www.reddit.com/r/CasualConversation/comments/1ao0uaq/i_dont_know_how_it_respond_when_a_girl_calls_me/'
    assert identify_post_type(submission_is_self, submission_text, submission_url) == Title
