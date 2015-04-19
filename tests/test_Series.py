__author__ = 'Nick'

import pytest
from formulapy.data.ergast import Formula1


@pytest.fixture
def f1():
    return Formula1()

def test_Series(f1):
    assert(f1 is not None)
    assert len(f1.seasons) > 0
    assert isinstance(f1.seasons, list)

def test_Series_Season(f1):
    s2012 = f1.season(2012)
    assert s2012.season == 2012

if __name__ == '__main__':
    test_Series()