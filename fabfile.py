import os
import random
import string

from fabric.api import env, local
from fabric.colors import cyan
from fabric.context_managers import shell_env

current_dir = os.getcwd()
env.project_name = 'infoscience_exports'
env.branch = 'master'
env.environments = ['dev',
                    'qa',
                    'prod']


def migrate():
    with shell_env(DATABASE_PASSWORD='django'):
        local('python {}/manage.py migrate'.format(env.project_name))


def serve():
    with shell_env(DATABASE_PASSWORD='django'):
        local('python {}/manage.py runserver'.format(env.project_name))


def test():
    """
    Runs nose test suite
    """
    with shell_env(DATABASE_PASSWORD='django'):
        local('flake8 {}'.format(env.project_name))
        print(cyan('flake8 passed!', bold=True))
        local('python {}/manage.py test'.format(env.project_name))


def create_secret_key():
    """
    Creates a random string of letters and numbers
    """
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(30))


def dev():
    """fab dev [command]"""
    env.environment = 'dev'
    env.branch = 'master'


def qa():
    """fab staging [command]"""
    env.environment = 'qa'
    env.branch = 'qa'


def prod():
    """fab prod [command]"""
    env.environment = 'prod'
    env.branch = 'prod'
