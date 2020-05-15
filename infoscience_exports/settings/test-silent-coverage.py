from .test import *


NOSE_ARGS = [
    BASE_DIR,
    '--nologcapture',
    '--with-progressive',
    '--cover-package={}'.format(BASE_DIR)
]
