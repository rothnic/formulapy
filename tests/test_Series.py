__author__ = 'Nick'

import pytest
from formulapy.data.ergast import Formula1
from formulapy.core import Race


@pytest.fixture
def f1():
    return Formula1()

@pytest.fixture
def s2012(f1):
    return f1.season(2012)

def test_Series(f1):
    assert(f1 is not None)
    assert len(f1.seasons) > 0
    assert isinstance(f1.seasons, list)

def test_Series_Season(s2012):
    assert s2012.season == 2012

def test_Series_Season_Races(s2012):
    assert isinstance(s2012.races, list)
    assert all([isinstance(race, Race) for race in s2012.races])

def test_Races(s2012):
    race0 = s2012.races[0]
    assert isinstance(race0.name, unicode)

if __name__ == '__main__':
    test_Series()