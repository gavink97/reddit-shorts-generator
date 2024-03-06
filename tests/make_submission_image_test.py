from reddit_shorts.make_submission_image import generate_reddit_story_image


def test_generate_reddit_story_image():
    submission_author = "gavink"
    submission_title = "This is a test"
    subreddit = "askreddit"
    submission_timestamp = 1703679574
    submission_score = 1
    submission_comments_int = 0

    generate_reddit_story_image(submission_author, submission_title, subreddit, submission_timestamp, submission_score, submission_comments_int)
