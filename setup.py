#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import find_packages, setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `__version__.py`.
    """
    with open(os.path.join(package, "__version__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


def get_long_description():
    """
    Return the README.
    """
    with open("README.md", encoding="utf8") as f:
        return f.read()


setup(
    name="starlette-early-data",
    python_requires=">=3.6",
    version=get_version("starlette_early_data"),
    url="https://github.com/HarrySky/starlette-early-data",
    license="Unlicense",
    description="Middleware and decorator for processing TLSv1.3 early data requests in Starlette",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Igor Nehoroshev",
    author_email="mail@neigor.me",
    packages=["starlette_early_data"],
    data_files=[("", ["LICENSE"])],
    include_package_data=True,
    install_requires=["starlette>=0.12.11"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
