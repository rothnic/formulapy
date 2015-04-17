__author__ = 'nickroth'


def urljoin(*args):
    """Joins given arguments into a url.
    Trailing but not leading slashes are stripped for each argument.
    """
    return "/".join(map(lambda x: str(x).rstrip('/'), args))