import os

_project_path = os.path.expanduser('~/projects/reddit-shorts/pyapp')
if not os.path.isdir(_project_path):
    _project_path = '/pyapp'

_temp_path = os.path.join(_project_path, 'temp')
_resources = os.path.join(_project_path, 'resources')

_video_resources = os.path.join(_resources, 'footage')
_game_resources = os.path.join(_resources, 'gaming')
_music_resources = os.path.join(_resources, 'music')

_CHANNEL_NAME = "@yourchannel"

_footage = []
for file in os.listdir(_video_resources):
    file_path = os.path.join(_video_resources, file)
    if not file.startswith('.DS_Store'):
        _footage.append(file_path)

_gaming_footage = []
for file in os.listdir(_game_resources):
    file_path = os.path.join(_game_resources, file)
    if not file.startswith('.DS_Store'):
        _gaming_footage.append(file_path)

_music = []
for file in os.listdir(_music_resources):
    file_path = os.path.join(_music_resources, file)
    if not file.startswith('.DS_Store'):
        _music.append(file_path)

# subreddit allows_random
_subreddits = [
    # Asking Questions
    ("askreddit", True),
    ("askmen", True),
    ("askuk", True),
    ("nostupidquestions", True),

    # Opinions
    ("unpopularopinion", True),
    ("legaladvice", False),

    # Random thoughts
    ("showerthoughts", True),

    # Today I learned
    ("todayilearned", True),
    ("explainlikeimfive", True),

    # Stories
    ("stories", True),
    ("talesfromtechsupport", True),
    ("talesfromretail", True),
    ("offmychest", False),
    ("relationships", False),
    ("casualconversation", True),

    # Creepy stuff
    ("letsnotmeet", True),
    ("shortscarystories", True),
    ("truescarystories", True),
    ("creepyencounters", True),
    ("thetruthishere", False)
]

bad_words_list = [
    "porn",
    "pornography",
    "fuck",
    "fucking"
]
