import os

launcher_path = os.path.dirname(os.path.abspath(__file__))

video_resources_path = f'{launcher_path}/resources/footage'
video_resources = os.listdir(video_resources_path)

music_resources_path = f'{launcher_path}/resources/music'
music_resources = os.listdir(music_resources_path)

footage = []
for file in video_resources:
    file_path = os.path.join(video_resources_path, file)
    if not file.startswith('.DS_Store'):
        footage.append(file_path)

# CHECK MUSIC FOR COPYRIGHTS ON TIKTOK BEFORE USING
# music_path, volumex float, music_type
music = [
        # General
        (f"{music_resources_path}/lakey_better_days.mp3", 0.2, "general"),
        (f"{music_resources_path}/fredji_flying_high.mp3", 0.2, "general"),
        (f"{music_resources_path}/lakey_inspired_blue_boi.mp3", 0.15, "general"),
        (f"{music_resources_path}/mona_wonderlick_golden.mp3", 0.2, "general"),
        (f"{music_resources_path}/roa_music_lights.mp3", 0.16, "general"),

        # Storytime
        (f"{music_resources_path}/keysofmoonmusic_lonesome_journey.mp3", 0.4, "storytime"),
        (f"{music_resources_path}/scott_buckley_filaments.mp3", 0.32, "storytime"),
        (f"{music_resources_path}/scott_buckley_signal_to_noise.mp3", 0.28, "storytime"),
        (f"{music_resources_path}/sappheiros_falling.mp3", 0.38, "storytime"),
        (f"{music_resources_path}/josh_lippi_st_francis.mp3", 0.4, "storytime"),

        # Creepy
        (f"{music_resources_path}/willex_dolorem_sad_song.mp3", 0.4, "creepy"),
        (f"{music_resources_path}/miguel_johnson_2184.mp3", 0.4, "creepy"),
        (f"{music_resources_path}/realize_flowing_into_the_darkness.mp3", 0.45, "creepy"),
        (f"{music_resources_path}/mehul_sharma_curse.mp3", 0.4, "creepy"),
        (f"{music_resources_path}/scott_buckley_balefire.mp3", 0.41, "creepy"),
        (f"{music_resources_path}/horror_mehul_sharma.mp3", 0.39, "creepy")
        ]

# subreddit, music_type, allows_random
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
