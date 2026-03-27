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
SIMPLE_DIR = SITE_DIR / 'simple'


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

    PACKAGES_DIR.mkdir(parents=True)
    SIMPLE_DIR.mkdir(parents=True)

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
            str(SIMPLE_DIR),
            '--packages-url',
            '../../packages/',
        ],
        check=True,
    )

    root_simple = os.environ.get('GITHUB_PAGES_URL', '').rstrip('/') + '/simple/'
    with open(SITE_DIR / 'index.html', 'w') as f:
        f.write(f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SimulAVR Python package registry</title>
</head>
<body>
    <h1>SimulAVR Python package registry</h1>
    <p>This site hosts wheels and source distributions for this repository.</p>
    <p>Use it with pip like this:</p>
    <pre>python -m pip install --index-url {root_simple} PACKAGE_NAME</pre>
    <p>Browse available packages <a href="simple/">here</a>.</p>
</body>
""")

if __name__ == '__main__':
    main()

