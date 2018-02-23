# get release from git-release.py, auto updated by git pre-commit hook
from .versions import _release, _build, _version

__release__ = _release
__version__ = _version

# sensible synonym
VERSION = __version__

# build number is actually from the previous commit
__build__ = '++{}'.format(_build)


def format_version(label):
    if label == 'build':
        return __build__
    elif label == 'release':
        return __release__
    elif label == 'all':
        return "release {}, build {}, RC.version {}".format(
            __release__, __build__, __version__
        )
    else:
        return __version__
