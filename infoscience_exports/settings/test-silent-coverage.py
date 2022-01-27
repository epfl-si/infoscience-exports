from .test import *


NOSE_ARGS = [
    BASE_DIR,
    '--nologcapture',
    '--cover-package={}'.format(BASE_DIR)
]
