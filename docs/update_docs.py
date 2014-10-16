__author__ = 'Nick'


import subprocess
from shutil import copy

copy('../.gitignore', './_build')
subprocess.call('python C://Anaconda/Scripts/ghp-import -n ./_build')
