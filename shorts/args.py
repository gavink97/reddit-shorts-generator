import argparse
import os

_PLATFORM_CHOICES = ("tiktok", "youtube", "all", "video")
_STRATEGIES = ("hot", "random")


def _parse_args() -> dict:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-p",
        "--platform",
        choices=_PLATFORM_CHOICES,
        default=_PLATFORM_CHOICES[3],
        help="Choose a platform:"
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str.lower,
        action='store',
        default='',
        help="text or text file path"
    )

    parser.add_argument(
        "-t",
        "--title",
        type=str.lower,
        action='store',
        default='',
        help="video title"
    )

    parser.add_argument(
        "-k",
        "--keywords",
        type=str.lower,
        action='store',
        default='',
        help="keywords or hashtags",
        dest="keywords",
    )

    parser.add_argument(
        "-v",
        "--video",
        type=str.lower,
        action='append',
        default=[],
        help="video path or 2 paths for split screen"
    )

    parser.add_argument(
        "-m",
        "--music",
        type=str.lower,
        action='store',
        default='',
        help="music file path"
    )

    parser.add_argument(
        "-pf",
        "--filter",
        action="store_true",
        default=False,
        help="Profanity filter"
    )

    parser.add_argument(
        "-s",
        "--split",
        action="store_true",
        default=False,
        help="split screen video"
    )

    parser.add_argument(
        "--strategy",
        choices=_STRATEGIES,
        default=_STRATEGIES[0],
        help="Choose a content gathering strategy"
    )

    args = parser.parse_args()

    split = args.split
    keywords = args.keywords

    input_value = ""

    title = args.title

    if args.input != '':
        if os.path.isfile(args.input):
            with open(args.input, 'r', encoding='utf-8') as file:
                input_value = str(file.read())

        else:
            input_value = args.input

        if args.platform != 'video':
            while not title.strip():
                title = input(
                    "A title is required to upload. Please enter a title:\n"
                )

            if keywords == '':
                keywords = input(
                    "Would you like to add some keywords?\n"
                )

    if args.video != []:
        if len(args.video) > 2:
            raise Exception(
                "A maximum of two video inputs are allowed."
                f" {len(args.video)} are provided."
            )

        if len(args.video) == 2:
            split = True

        for v in args.video:
            if not os.path.isfile(v):
                raise Exception(f"Invalid video path provided: {v}")

        if len(args.video) == 1 & split:
            raise Exception(
                "Invalid number of video inputs."
                f" {len(args.video)} are provided."
            )

    if args.music != '':
        if not os.path.isfile(args.music):
            raise Exception(f"Invalid music file path provided: {args.music}")

    return {
        'platform': args.platform,
        'filter': args.filter,
        'input': input_value,
        'video': args.video,
        'music': args.music,
        'strategy': args.strategy,
        'title': title,
        'keywords': keywords,
        'split': split
    }
