import datetime
import os
import pickle
import random
import time

import httplib2
from apiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from shorts.config import _project_path

httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

SECRETS = f"{_project_path}/client_secrets.json"

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), SECRETS))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service():
    cred = None
    pickle_file = f'token_{_SERVICE_NAME}_{YOUTUBE_API_VERSION}.pickle'

    api_token = os.path.join(_project_path, pickle_file)
    if os.path.exists(api_token):
        with open(api_token, 'rb') as token:
            cred = pickle.load(token)

    scopes = [f'{YOUTUBE_UPLOAD_SCOPE}']

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SECRETS, scopes)
            cred = flow.run_local_server()

        with open(api_token, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=cred)
        print(_SERVICE_NAME, 'service created successfully')
        return service

    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None


def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt


def initialize_upload(
        youtube,
        youtube_short_file,
        short_video_title,
        video_description,
        video_category,
        video_keywords,
        video_privacy_status,
        notify_subs
):

    if video_keywords:
        tags = video_keywords

    else:
        tags = None

    body = dict(
        snippet=dict(
            title=short_video_title,
            description=video_description,
            tags=tags,
            categoryId=video_category
        ),
        status=dict(
            privacyStatus=video_privacy_status
        )
    )

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        notifySubscribers=notify_subs,
        media_body=MediaFileUpload(
            youtube_short_file,
            chunksize=-1,
            resumable=True
        ))

    resumable_upload(insert_request)


def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was uploaded." % response['id'])
                else:
                    exit("Upload failed. Unexpected response: %s" % response)

        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (
                    e.resp.status,
                    e.content
                )

            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)
