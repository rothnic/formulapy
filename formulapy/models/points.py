__author__ = 'nickroth'

_points_2010_present = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
_points_2003_2009 = [10, 8, 6, 5, 4, 3, 2, 1]
_points_2000_2002 = [10, 6, 4, 3, 2, 1]


def get_point_scale(year):
    """Returns the points awarded, ordered by finish place, for given year."""

    if 2009 < year:
        return _points_2010_present
    elif 2002 < year <= 2009:
        return _points_2003_2009
    elif 1999 < year <= 2002:
        return _points_2000_2002
    else:
        raise NotImplementedError


def update_points(drivers, year):
    """Updates each driver's points, based on the given year."""

    for driver, points in zip(drivers, get_point_scale(year)):
        driver.points += points


if __name__ == '__main__':

    class TestDriver:
        def __init__(self, name, points):
            self.name = name
            self.points = points

    test_drivers = [TestDriver(name='Bob', points=0), TestDriver(name='Fred', points=15)]

    update_points(test_drivers, 2015)
    update_points(test_drivers, 2015)
    update_points(test_drivers, 2015)

    for test_driver in test_drivers:
        print('driver: %s points: %s ' % (test_driver.name, test_driver.points))