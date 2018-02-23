import os
import subprocess

__version__ = '0.1.1'

# sensible synonym
VERSION = __version__

# setting build number from git (if available)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    __release__ = subprocess.check_output(
        ["git", "describe", "--tags"], cwd=BASE_DIR).decode('utf-8').strip()
    __build__ = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=BASE_DIR).decode('utf-8').strip()
except Exception:
    __release__ = __version__ + " ?"
    __build__ = __version__ + " ?"
