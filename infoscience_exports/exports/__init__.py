# get release from git-release.py, auto updated by git pre-commit hook
from .versions import _version


__version__ = _version

# sensible synonym
VERSION = __version__

def format_version(label=None):
    # default value
    label = label or 'version'
    # define valid matches
    result = {
        'version': __version__,
        'all': "version {}".format(
             __version__
        )
    }
    # multiple values asked
    if type(label) in [list, tuple]:
        items = [result.get(item) for item in label if item]
        return ', '.join(items)
    # one label only
    return result.get(label, __version__)
