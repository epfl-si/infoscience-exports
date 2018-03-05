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
import argparse
from pprint import pprint

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR.endswith('hooks'):
    BASE_DIR = os.path.abspath(os.path.sep.join(
        [BASE_DIR, '..', '..']))
    sys.path.append(BASE_DIR)

from versions import __file__ as RELEASE_FILE  # noqa
from versions import _release, _build, _version  # noqa

COPY_PATH = os.path.sep.join([BASE_DIR, 'infoscience_exports', 'exports', 'versions.py'])


def set_logging_config(quiet=False, debug=False):
    """
    Set logging with the 'good' level

    Arguments keywords:
    kwargs -- list containing parameters passed to script
    """
    # set up level of logging
    level = logging.INFO
    if quiet:
        level = logging.WARNING
    elif debug:
        level = logging.DEBUG

    # set up logging to console
    logging.basicConfig(format='%(levelname)s - %(funcName)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(level)


def compute():
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
            ["git", "describe", "--tags", "--match", "[0-9]*"], cwd=BASE_DIR).decode('utf-8').strip()
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


def confirm_release():
    print("version currently set to {}".format(_version))
    answer = ""
    while answer not in ["y", "n"]:
        answer = input("OK to push to continue [Y/N]? ").lower()
    if answer != "y":
        raise SystemExit("Please confirm version number to continue")


def confirm_push():
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=BASE_DIR).decode('utf-8').strip()
        print("\nYou are on branch '{}'".format(branch))
        print("on version        '{}'".format(_version))
        print("\nType [y] to comfirm push".format(branch))
        answer = input("or any other key to abort:").lower()
        if answer != "y":
            raise SystemExit("Push aborted...")
    except Exception as err:
        logging.warning("Git does not seem available: %s", err)
        raise SystemExit("This command requires git")


def publish(dry_run=False):
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
    changelog_url = "https://github.com/{}/{}/blob/release-{}/CHANGELOG.md".format(github_owner, github_repo, _version)
    post_args = {
        "tag_name": _version,
        "name": "Release {}".format(_version),
        "body": "See [CHANGELOG.md]({}) for all details".format(changelog_url),
        "draft": False,
        "prerelease": False
        }
    logging.debug("POST %s with data: %s", url, post_args)

    # make request and raise exception if we had an issue
    if not dry_run:
        response = requests.post(url, data=json.dumps(post_args), auth=(github_user, github_key))
        response.raise_for_status()
    else:
        print("POST {}".format(url))
        print("auth({}, xxx)".format(github_user))
        pprint(post_args)



def check_branch(expected='master'):
    try:
        current = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=BASE_DIR).decode('utf-8').strip()
        if current != expected:
            raise SystemExit("You are in {}, whereas expected branch is {}".format(current, expected))
        logging.info("You are in {}".format(current))
    except Exception as err:
        logging.warning("Git does not seem available: %s", err)
        raise SystemExit("This command requires git")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        usage="""Release manager script

This file should be used as post-commit in .git/hooks
It can be run with both python 2.7 and 3.6""")
    parser.add_argument("command", nargs='?', help="[confirm|publish|check]")
    parser.add_argument('--prod', action='store_true', help="used with command confirm")
    parser.add_argument('--dry-run', action='store_true', help="used with command publish")
    parser.add_argument('--branch', help="used with command check_branch")
    parser.add_argument('-v', '--version', action='version', version=_version)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()

    set_logging_config(quiet=args.quiet, debug=args.debug)
    logging.debug(args)

    if args.command == 'confirm':
        if args.prod:
            confirm_push()
        else:
            confirm_release()
    elif args.command == 'check':
        check_branch(expected=args.branch)
    elif args.command == 'publish':
        publish(dry_run=args.dry_run)
    else:
        compute()
