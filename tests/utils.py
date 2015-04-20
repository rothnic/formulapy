__author__ = 'nickroth'


def is_list_of(items, the_type):
    """Performs type comparison for each item in a list of items."""
    return all([isinstance(item, the_type) for item in items])