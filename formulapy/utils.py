__author__ = 'nickroth'

import re

def variablize(s):

   # Remove invalid characters
   s = re.sub('[^0-9a-zA-Z_]', '', s)

   # Remove leading characters until we find a letter or underscore
   s = re.sub('^[^a-zA-Z_]+', '', s)

   return s

def urljoin(*args):
    """Joins given arguments into a url.
    Trailing but not leading slashes are stripped for each argument.
    """
    return "/".join(map(lambda x: str(x).rstrip('/'), args))