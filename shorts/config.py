import os

# launcher_path = os.path.abspath(os.path.dirname(__file__))
# project_path = os.path.join(launcher_path, os.pardir)

source_dir = 'reddit-shorts/reddit_shorts'
_project_path = os.path.expanduser('~/projects/reddit-shorts/pyapp')
_launch_path = os.path.join(_project_path, source_dir)
_temp_path = os.path.join(_project_path, 'temp')
_resources = os.path.join(_project_path, 'resources')

_video_resources = os.path.join(_resources, 'footage')
_music_resources = os.path.join(_resources, 'music')

_CHANNEL_NAME = "@your_channel"

# Subject to change
_footage = []
for file in os.listdir(_video_resources):
    file_path = os.path.join(_video_resources, file)
    if not file.startswith('.DS_Store'):
        _footage.append(file_path)

# CHECK MUSIC FOR COPYRIGHT BEFORE USING
# music_path str, volumex float float, music_type str
_music = [
        # General
        (f"{_music_resources}/lakey_better_days.mp3", 0.2, "general"),
        (f"{_music_resources}/fredji_flying_high.mp3", 0.2, "general"),
        (f"{_music_resources}/lakey_inspired_blue_boi.mp3", 0.15, "general"),
        (f"{_music_resources}/mona_wonderlick_golden.mp3", 0.2, "general"),
        (f"{_music_resources}/roa_music_lights.mp3", 0.16, "general"),

        # Storytime
        (f"{_music_resources}/keysofmoonmusic_lonesome_journey.mp3", 0.4, "storytime"),
        (f"{_music_resources}/scott_buckley_filaments.mp3", 0.32, "storytime"),
        (f"{_music_resources}/scott_buckley_signal_to_noise.mp3", 0.28, "storytime"),
        (f"{_music_resources}/sappheiros_falling.mp3", 0.38, "storytime"),
        (f"{_music_resources}/josh_lippi_st_francis.mp3", 0.4, "storytime"),

        # Creepy
        (f"{_music_resources}/willex_dolorem_sad_song.mp3", 0.4, "creepy"),
        (f"{_music_resources}/miguel_johnson_2184.mp3", 0.4, "creepy"),
        (f"{_music_resources}/realize_flowing_into_the_darkness.mp3", 0.45, "creepy"),
        (f"{_music_resources}/mehul_sharma_curse.mp3", 0.4, "creepy"),
        (f"{_music_resources}/scott_buckley_balefire.mp3", 0.41, "creepy"),
        (f"{_music_resources}/horror_mehul_sharma.mp3", 0.39, "creepy")
        ]

# subreddit str, music_type str, allows_random, bool
subreddits = [
        # Asking Questions
        ("askreddit", "general", True),
        ("askmen", "general", True),
        ("askuk", "general", True),
        ("nostupidquestions", "general", True),

        # Opinions
        ("unpopularopinion", "general", True),
        ("legaladvice", "storytime", False),

        # Random thoughts
        ("showerthoughts", "general", True),

        # Today I learned
        ("todayilearned", "storytime", True),
        ("explainlikeimfive", "general", True),

        # Stories
        ("stories", "storytime", True),
        ("talesfromtechsupport", "storytime", True),
        ("talesfromretail", "storytime", True),
        ("offmychest", "storytime", False),
        ("relationships", "storytime", False),
        ("casualconversation", "general", True),

        # Creepy stuff
        ("letsnotmeet", "creepy", True),
        ("shortscarystories", "creepy", True),
        ("truescarystories", "creepy", True),
        ("creepyencounters", "creepy", True),
        ("thetruthishere", "creepy", False)
        ]

bad_words_list = [
    "porn",
    "fuck",
    "fucking"
]
