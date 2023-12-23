def create_video_title(submission_title, subreddit):
    youtube_title_limit = 100

    youtube_hashtags = "#reddit #minecraft"

    truncation_limit = youtube_title_limit - len(youtube_hashtags) - 4

    if len(submission_title) >= truncation_limit:
        truncated_youtube_title = submission_title[:truncation_limit]
        if truncated_youtube_title.endswith(' '):
            truncated_youtube_title = truncated_youtube_title[:-1]

        short_video_title = f"{truncated_youtube_title}... {youtube_hashtags}"
    else:
        short_video_title = f"{submission_title} {youtube_hashtags}"

    print(short_video_title)
    return short_video_title
