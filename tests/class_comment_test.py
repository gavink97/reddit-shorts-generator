from reddit_shorts.class_comment import Comment


def test_process_comment():
    author = 'submission_author'
    data = {
        'author': 'gavin',
        'body': 'Hey I hope you enjoy my shorts generator',
        'id': 1
    }

    Comment.process_comment(data, author)
