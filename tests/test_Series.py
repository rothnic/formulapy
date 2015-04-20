__author__ = 'Nick'

import pytest
from formulapy.data.ergast import Formula1
from formulapy.core import DataGroup, Race, Driver
from utils import is_list_of


@pytest.fixture
def f1():
    return Formula1()


@pytest.fixture
def s2012(f1):
    return f1.season(2012)


@pytest.fixture
def races(s2012):
    return s2012.races


@pytest.fixture
def sample_race(races):
    return races[0]


def test_Series(f1):
    assert(f1 is not None)
    assert len(f1.seasons) > 0


def test_Series_Season(s2012):
    assert s2012.season == 2012


def test_Series_Season_Races(races):
    assert isinstance(races, DataGroup)
    assert is_list_of(races, Race)


def test_Races(sample_race):
    assert isinstance(sample_race.name, unicode)
    assert isinstance(str(sample_race), str)
    print(sample_race)


def test_Races_Drivers(sample_race):
    drivers = sample_race.drivers
    assert is_list_of(drivers, Driver)


if __name__ == '__main__':
    f1 = f1()
    s2012 = s2012(f1)
    test_Series(f1)
    test_Races(s2012)