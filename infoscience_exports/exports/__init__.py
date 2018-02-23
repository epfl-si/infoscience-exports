# get release from git-release.py, auto updated by git pre-commit hook
from .versions import _release, _build, _version

__release__ = _release
__version__ = _version

# sensible synonym
VERSION = __version__

# build number is actually from the previous commit
__build__ = '++{}'.format(_build)
