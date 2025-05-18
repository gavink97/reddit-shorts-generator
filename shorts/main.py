import os

from dotenv import load_dotenv

from shorts.args import _parse_args
from shorts.config import _project_path
from shorts.query_db import create_tables
from shorts.platforms import _tiktok, _youtube, _create_short


def _main(**kwargs) -> None:
    if not os.path.isfile(f'{_project_path}/reddit-shorts/shorts.db'):
        create_tables()

    platform = kwargs.get("platform")

    match platform:
        case "tiktok":
            _tiktok(**kwargs)

        case "youtube":
            _youtube(**kwargs)
        case "all":
            kwargs.__setitem__('platform', 'tiktok')
            _tiktok(**kwargs)

            kwargs.__setitem__('platform', 'youtube')
            _youtube(**kwargs)

        case "video" | _:
            _create_short(**kwargs)


def _run_main() -> None:
    load_dotenv()
    args = _parse_args()
    _main(**args)


if __name__ == "__main__":
    _run_main()
