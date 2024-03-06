from __future__ import annotations

from setuptools import find_packages
from setuptools import setup

setup(
    name="reddit_shorts",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["shorts=reddit_shorts.main:main"],
    },
)
