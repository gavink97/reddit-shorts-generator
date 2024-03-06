class Submission:
    pass


class Title(Submission):
    kind = "title"


class Text(Submission):
    kind = "text"


class Link(Submission):
    kind = "link"


class Image(Submission):
    kind = "image"


class Video(Submission):
    kind = "video"


def identify_post_type(submission_is_self: bool, submission_text: str, submission_url: str):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    video_extensions = ['.mp4', '.avi', '.mov']
    reddit_image_extensions = ['https://www.reddit.com/gallery/', 'https://i.redd.it/']
    reddit_video_extensions = ['https://v.redd.it/', 'https://youtube.com', 'https://youtu.be']

    if submission_is_self is True:

        if submission_text == "":
            return Title

        else:
            return Text

    if submission_is_self is False:

        if any(submission_url.endswith(ext) for ext in image_extensions):
            return Image

        elif any(submission_url.startswith(ext) for ext in reddit_image_extensions):
            return Image

        elif any(submission_url.endswith(ext) for ext in video_extensions):
            return Video

        elif any(submission_url.startswith(ext) for ext in reddit_video_extensions):
            return Video

        else:
            return Link
