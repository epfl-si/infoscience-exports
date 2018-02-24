#!/usr/bin/python
# this file should be used as post-commit in .git/hooks
# it can be run with both python 2.7 and 3.6
import os
import logging
import subprocess
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR.endswith('hooks'):
    BASE_DIR = os.path.abspath(os.path.sep.join(
        [BASE_DIR, '..', '..']))
    sys.path.append(BASE_DIR)

from versions import __file__ as RELEASE_FILE  # noqa
from versions import _release, _build, _version  # noqa

COPY_PATH = os.path.sep.join([BASE_DIR, 'infoscience_exports', 'exports', 'versions.py'])


def main():

    # compute version from release
    try:
        # get last release & version
        release_version = map(int, _release.split('-')[0].split('.'))
        candidate_version = map(int, _version.split('-')[0].split('.'))
        # nothing to do if candidate_version is already more than release
        if candidate_version > release_version:
            logging.debug("version already set to %s. not changing it", candidate_version)
            version = _version
        # increment and convert back in strings, with suffic -rc
        else:
            logging.debug("incrementint version from release %s", release_version)
            major, minor, patch = release_version
            version = '.'.join(map(str, [major, minor, patch+1])) + "-rc"
    except Exception as err:
        logging.error("Exception occured while trying to generate new version: %s", err)
        version = _version

    logging.info("will set _version=%s", version)

    # get build and release numbers from git
    try:
        build = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=BASE_DIR).decode('utf-8').strip()

        release = subprocess.check_output(
            ["git", "describe", "--tags"], cwd=BASE_DIR).decode('utf-8').strip()
    except Exception as err:
        logging.warning("Using previous build & release, since git does not seem available: %s", err)
        release = _release
        build = _build

    logging.info("will set _build=%s", build)
    logging.info("will set _release=%s", release)

    # update file
    with open(RELEASE_FILE, 'w') as output:
        content = """# flake8: noqa
# This file is autognerated by post-commit hook

# the release comes from git and should not be modified
# => read-only
_release = '{0}'

# you can set the next version number manually
# if you do not, the system will make sure that version > release
# => read-write, >_release
_version = '{1}'

# the build number will generate conflicts on each PR merge
# just keep yours every time
# => read-only
_build = '{2}'""".format(release, version, build)
        output.write(content)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.debug("updating versions")
    main()
