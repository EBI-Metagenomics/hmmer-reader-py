#!/usr/bin/env python

from setuptools import setup

if __name__ == "__main__":
    setup(
        entry_points={"console_scripts": ["hmmer-show = hmmer_reader:cli"]},
        cffi_modules="build_ext.py:ffibuilder",
    )
