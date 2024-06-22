https://github.com/gavink97/reddit-shorts-generator/assets/78187175/d244555b-235b-4897-8c70-7009c6ba45ea

<h1 align="center">Reddit Shorts Generator</h1>
<p align="center" style="font-size: large;">Generate Short-form media from UGC
content from the worst website on the internet</p> <br>

## Table of contents
- [Why](#why-this-project)
- [Features](#features)
- [Installation](#installation)
    - [Optional](#optional)
- [Quick Start](#getting-started)
- [Customization](#making-it-your-own)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [Star History](#star-history)


## Why this project
I started this project after being inspired by this
[video](https://youtu.be/_BsgckzDeRI?si=p18GIlR5urz-Pues).

It was mid December and I had just gotten absolutely crushed
in my first technical interview, so I wanted to build
something simple to regain confidence.


## Features
- Create Short-form media from UGC content from the worst website on the
  internet.
- Upload videos directly to YouTube via the [YouTube
  API](https://developers.google.com/youtube/v3).
- Automatically generate captions for your videos using Open AI
  [Whisper](https://github.com/openai/whisper).
- Videos are highly customizable and render blazingly fast with FFMPEG.
- Utilizes SQLite to avoid creating duplicate content.


## Installation
Reddit Shorts can run independently but if you want to upload shorts
automatically to YouTube or TikTok you must install the [TikTok
Uploader](https://github.com/wkaisertexas/tiktok-uploader) and set up the
[YouTube Data API](https://developers.google.com/youtube/v3) respectively.

Additionally, install the reddit shorts repo in the root directory of the
project as shown in the file tree.

### File tree

```
├── client_secrets.json
├── cookies.txt
├── [reddit-shorts]
├── resources
│   ├── footage
│   └── music
├── tiktok-uploader
├── tiktok_tts.txt
└── youtube_tts.txt
```

### Optional
- [TikTok Uploader](https://github.com/wkaisertexas/tiktok-uploader) is required to upload shorts to TikTok.
- [YouTube Data API](https://developers.google.com/youtube/v3) is required to upload shorts to YouTube.

### Build source
Because OpenAi's [Whisper](https://github.com/openai/whisper) is only compatible
with Python 3.8 - 3.11 only use those versions of python.

```
mkdir reddit-shorts
gh repo clone gavink97/reddit-shorts-generator reddit-shorts
pip install -e reddit-shorts
```

### Install dependencies
This package requires `ffmpeg fonts-liberation` to be installed.

*This repository utilizes pillow to create reddit images, so make sure to
uninstall PIL if you have it installed*

### Config
If your music / footage directory is different from the file tree configure the
path inside `config.py`.

If you are creating videos for TikTok or YouTube and wish to have some custom
tts at the end of the video, make sure you
create `tiktok_tts.txt` or `youtube_tts.txt`.


## Getting Started
`shorts` is the command line interface for the project. 

Simply run `shorts -p platform` to generate a youtube short and automatically
upload it.

`shorts -p youtube`

*it should be noted that the only supported platform is youtube at
the moment*


## Making it your own
Customize your shorts with FFMPG inside `create_short.py`.


## Contributing
All contributions are welcome!

## Roadmap

- [ ] Standalone video exports
- [ ] TikTok Support

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=gavink97/reddit-shorts-generator&type=Date)](https://star-history.com/#gavink97/reddit-shorts-generator&Date)
