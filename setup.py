"""Setup script for YDL"""

from setuptools import setup


setup(
    name="ydl-ipc",
    packages=["ydl"],
    version="0.1.0",
    description="Simple inter-process communication",
    long_description="Read the README at https://github.com/sberkun/ydl",
    url="https://github.com/sberkun/ydl",
    author="Samuel Berkun",
    author_email="sberkun@berkeley.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    install_requires=["typeguard"],
)
