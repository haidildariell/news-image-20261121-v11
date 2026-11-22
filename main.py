#!/usr/bin/env python3
"""Entrypoint for the news-image-20261121 harness.

The front page is rendered ahead of time by build_image.py into the
entry.png that sits beside this file. The harness sandbox is
stdlib-only (no PIL), so this entrypoint does no drawing at all: it
copies the pre-rendered PNG to the output path the harness reads.
"""

import os
import shutil
from pathlib import Path


def main():
    src = Path(__file__).resolve().parent / "entry.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, out_dir / "entry.png")


if __name__ == "__main__":
    main()
