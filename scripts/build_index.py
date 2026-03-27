#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from packaging.utils import canonicalize_name, parse_sdist_filename, parse_wheel_filename


DIST_DIR = Path('dist')
SITE_DIR = Path('site')
PACKAGES_DIR = SITE_DIR / 'packages'


def detect_package_name(filename: str) -> str:
    if filename.endswith('.whl'):
        name, _, _, _ = parse_wheel_filename(filename)
        return canonicalize_name(str(name))
    if filename.endswith('.tar.gz') or filename.endswith('.zip'):
        name, _ = parse_sdist_filename(filename)
        return canonicalize_name(str(name))
    raise ValueError(f'Unsupported distribution file: {filename}')


def main() -> None:
    artifacts = sorted(
        path
        for path in DIST_DIR.iterdir()
        if path.is_file() and (
            path.name.endswith('.whl')
            or path.name.endswith('.tar.gz')
            or path.name.endswith('.zip')
        )
    )
    if not artifacts:
        raise SystemExit('No distribution artifacts found in dist/')

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)

    SITE_DIR.mkdir(parents=True)
    PACKAGES_DIR.mkdir(parents=True)

    for artifact in artifacts:
        shutil.copy2(artifact, PACKAGES_DIR / artifact.name)

    package_names = sorted({detect_package_name(path.name) for path in artifacts})

    package_list = SITE_DIR / 'package-list.txt'
    package_list.write_text(
        ''.join(f'{artifact.name}\n' for artifact in artifacts),
        encoding='utf-8',
    )

    subprocess.run(
        [
            'dumb-pypi',
            '--title=SimulAVR Python packages',
            '--package-list',
            str(package_list),
            '--output-dir',
            str(SITE_DIR),
            '--packages-url',
            '../../packages/',
        ],
        check=True,
    )

if __name__ == '__main__':
    main()

