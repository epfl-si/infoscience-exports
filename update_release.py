#!/usr/bin/python
"""Release manager script

This file should be used as post-commit in .git/hooks
It can be run with both python 2.7 and 3.6

Usage:
    commands.py [-q | -d]
    commands.py confirm [-q | -d]
    commands.py publish [-q | -d]
    commands.py check [--branch=BRANCH] [-q | -d]
    commands.py -h
    commands.py -v

Options:
    -h, --help       display this message and exit
    -v, --version    display version
    --branch=BRANCH  branch name to check for (default to master)
    -q, --quiet      set log level to WARNING (instead of INFO)
    -d, --debug      set log level to DEBUG (instead of INFO)
"""
import os
import json
import logging
import subprocess
import sys
import shutil

from docopt import docopt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR.endswith('hooks'):
    BASE_DIR = os.path.abspath(os.path.sep.join(
        [BASE_DIR, '..', '..']))
    sys.path.append(BASE_DIR)

from versions import __file__ as RELEASE_FILE  # noqa
from versions import _release, _build, _version  # noqa

COPY_PATH = os.path.sep.join([BASE_DIR, 'infoscience_exports', 'exports', 'versions.py'])


def set_logging_config(kwargs):
    """
    Set logging with the 'good' level

    Arguments keywords:
    kwargs -- list containing parameters passed to script
    """
    # set up level of logging
    level = logging.INFO
    if kwargs['--quiet']:
        level = logging.WARNING
    elif kwargs['--debug']:
        level = logging.DEBUG

    # set up logging to console
    logging.basicConfig(format='%(levelname)s - %(funcName)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(level)


def compute(**kwargs):
    logging.debug("Updating versions...")

    # compute version from release
    try:
        # get last release & version
        release_version = list(map(int, _release.split('-')[0].split('.')))
        candidate_version = list(map(int, _version.split('-')[0].split('.')))
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


try: input = raw_input
except: pass


def confirm(**kwargs):
    print("version currently set to {}".format(_version))
    answer = ""
    while answer not in ["y", "n"]:
        answer = input("OK to push to continue [Y/N]? ").lower()
    return answer == "y"


def publish(**kwargs):
    """ POST /repos/:owner/:repo/releases
        
        https://developer.github.com/v3/repos/releases/#create-a-release
    """
    # dynamic import to allow the other commands to run without requests
    import requests

    # get gihub config. If not set -> POST will fail, developer will understand
    github_owner = os.environ.get('GITHUB_OWNER')
    github_repo = os.environ.get('GITHUB_REPO')
    github_user = os.environ.get('GITHUB_USER')
    github_key = os.environ.get('GITHUB_KEY')

    # build request
    url = "https://api.github.com/repos/{}/{}/releases".format(github_owner, github_repo)
    post_args = {
        "tag_name": _version,
        "name": "Release {}".format(_version),
        "body": "See [CHANGELOG.md](./CHANGELOG.md) for all details",
        "draft": False,
        "prerelease": False
        }
    logging.debug("POST %s with data: %s", url, post_args)

    # make request and raise exception if we had an issue
    response = requests.post(url, data=json.dumps(post_args), auth=(github_user, github_key))
    response.raise_for_status()


def check_branch(**kwargs):
    try:
        expected = kwargs['--branch'] or 'master'
        current = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=BASE_DIR).decode('utf-8').strip()
        if current != expected:
            raise SystemExit("You are in {}, whereas expected branch is {}".format(current, expected))
        logging.info("You are in {}".format(current))
    except Exception as err:
        logging.warning("Git does not seem available: %s", err)
        raise SystemExit("This command requires git")


if __name__ == '__main__':
    kwargs = docopt(__doc__, version=_version)
    set_logging_config(kwargs)
    logging.debug(kwargs)
    if kwargs['confirm']:
        if not confirm(**kwargs):
            raise SystemExit("Please confirm version number to continue")
    elif kwargs['check']:
        check_branch(**kwargs)
    elif kwargs['publish']:
        publish(**kwargs)
    else:
        compute(**kwargs)
