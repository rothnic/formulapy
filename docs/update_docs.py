__author__ = 'Nick'


import subprocess
from shutil import copy

# copy .gitignore to build directory, so git ignores .idea files
copy('../.gitignore', './_build')

# call ghp-import on build directory, which overwrites build to gh-pages branch
subprocess.call('python C://Anaconda/Scripts/ghp-import -n ./_build')
