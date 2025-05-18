from contextlib import ExitStack
from apiclient.errors import HttpError
import os
from shorts.config import _launch_path
from shorts.make_tts import _tts
from shorts.create_short import _create_video
from shorts.get_reddit_stories import _get_content
from shorts.make_submission_image import _generate_reddit_image
from shorts.metadata import _title_video, _video_keywords
from shorts.youtube import initialize_upload, get_authenticated_service
from shorts.utils import _clean_up


def _create_short(**kwargs) -> None or list:
    submission = None

    if kwargs.get('input') == '':
        submission = _get_content(**kwargs)
        _generate_reddit_image(submission, **kwargs)

    tts_tracks = _tts(submission, **kwargs)
    file_path = _create_video(submission, tts_tracks, **kwargs)

    if kwargs.get('platform') == 'video':
        print(f"Video complete at {file_path}")
        return

    else:
        return file_path, submission


def _tiktok(**kwargs) -> None:
    try:
        from tiktok_uploader.upload import upload_video

    except ImportError:
        raise Exception("Tiktok Uploader is unavailable")

    file_path, submission = _create_short(**kwargs)

    if kwargs.get('title') != '':
        video_title = kwargs.get('title')
    else:
        video_title = _title_video(submission, **kwargs)

    max_retrys = 5
    retry_count = 0

    with ExitStack() as stack:
        stack.callback(_clean_up, file_path)

        while retry_count < max_retrys:
            try:
                upload_video(
                    file_path,
                    description=video_title,
                    cookies=os.path.join(_launch_path, 'cookies.txt'),
                    browser='firefox',
                    headless=False
                )

                break

            except Exception as e:
                print(f"Upload failed: {e}. Retrying... Attempt {retry_count + 1} of {max_retrys}")
                retry_count += 1

                if retry_count == max_retrys:
                    print("Failed to upload a video to tiktok.")
                    break


def _youtube(**kwargs) -> None:
    file_path, submission = _create_short(**kwargs)
    keys = kwargs.get('keywords')

    if kwargs.get('title') != '':
        video_title = kwargs.get('title')
    else:
        video_title = _title_video(submission, **kwargs)

    if keys != '':
        video_keywords = str(keys).split(' ')

    else:
        title = submission.get('title')
        subreddit = submission.get('subreddit')

        keywords = ','.join([
            'hidden reddit',
            'hidden',
            'reddit',
            'minecraft',
            'gaming'
        ])

        video_keywords = _video_keywords(title, subreddit, keywords)

    video_description = ""
    video_category = "20"  # Gaming
    video_privacy_status = "public"
    notify_subs = False

    with ExitStack() as stack:
        stack.callback(_clean_up, file_path)

        youtube = get_authenticated_service()

        try:
            initialize_upload(
                youtube,
                file_path,
                video_title,
                video_description,
                video_category,
                video_keywords,
                video_privacy_status,
                notify_subs
            )

        except HttpError as e:
            raise Exception(
                "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            )
