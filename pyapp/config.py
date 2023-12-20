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

music = []
for file in music_resources:
    file_path = os.path.join(music_resources_path, file)
    if not file.startswith('.DS_Store'):
        music.append(file_path)
