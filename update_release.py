#!/usr/bin/python
# this file should be used as post-commit in .git/hooks
# it can be run with both python 2.7 and 3.6
import os
import logging
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR.endswith('hooks'):
    BASE_DIR = os.path.abspath(os.path.sep.join(
        [BASE_DIR, '..', '..']))
    sys.path.append(BASE_DIR)

from versions import __file__ as REALEASE_FILE  # noqa
from versions import _release, _build, _version  # noqa


def main():

    # compute version from release
    try:
        # get version of last release
        version = _release.split('-')[0]
        # get integers
        major, minor, patch = map(int, version.split('.'))
        # increment and convert back in strings
        major, minor, patch = map(str, [major, minor, patch+1])
        # build version
        version = '.'.join([major, minor, patch])
        logging.debug("got version %s", version)
    except Exception:
        version = _version + " ?"

    # get build and release numbers from git
    try:
        release = subprocess.check_output(
            ["git", "describe", "--tags"], cwd=BASE_DIR).decode('utf-8').strip()
        logging.debug("got release %s", release)
        build = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=BASE_DIR).decode('utf-8').strip()
        logging.debug("got build %s", build)
    except Exception:
        release = _release + " ?"
        build = _build + " ?"

    # update file
    with open(REALEASE_FILE, 'w') as output:
        content = """# This file is autognerated by post-commit hook

_release = '{0}'
_version = '{1}'

# the build number will generate conflicts on each PR merge
# just keep yours every time
_build = '{2}'
        """.format(release, version, build)
        output.write(content)
        logging.info(content)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.debug("updating versions")
    main()
