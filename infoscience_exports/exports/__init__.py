# get release from git-release.py, auto updated by git pre-commit hook
from .versions import _release, _build, _version

__release__ = _release
__version__ = _version

# sensible synonym
VERSION = __version__

# build number is actually from the previous commit
__build__ = '++{}'.format(_build)


def format_version(label=None):
    # default value
    label = label or 'version'
    # define valid matches
    result = {
        'build': __build__,
        'release': __release__,
        'version': __version__,
        'all': "release {}, build {}, version {}".format(
            __release__, __build__, __version__
        )
    }
    # multiple values asked
    if type(label) in [list, tuple]:
        items = [result.get(item) for item in label if item]
        return ', '.join(items)
    # one label only
    return result.get(label, __version__)
