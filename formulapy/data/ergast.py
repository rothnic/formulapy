__author__ = 'nickroth'

import slumber
from restorm.clients.jsonclient import JSONClient
from restorm.resource import Resource
from formulapy.core import Race

ERGAST_URL = 'http://ergast.com/api/'
ergast_client = JSONClient(root_uri=ERGAST_URL)

BASE = r'^f1/'
JSON = '.json$'


class ErgastApi(object):

    base_url = ERGAST_URL

    def __init__(self, series):
        assert series == 'f1' or series == 'fr'
        self.series = series
        self.api = slumber.API(self.base_url, append_slash=False)

    def season(self, year='current', circuitId=None, driverId=None, constructorId=None,
               grid_pos=None, result_pos=None, fastest_rank=None, statusId=None):

        options = {'circuits': circuitId,
                   'drivers': driverId,
                   'constructors': constructorId,
                   'grid': grid_pos,
                   'results': result_pos,
                   'fastest': fastest_rank,
                   'status': statusId}

        query = self._get_base_query(year)
        query = self._add_query_options(query, options)
        response = self._execute_query(query)
        return self._parse_response(response)

    @staticmethod
    def _parse_response(response):
        x = response

    def _get_base_query(self, year=None):
        """Returns the base query, which can optionally include a year."""
        if year is None:
            return getattr(self.api, self.series)
        else:
            return getattr(self.api, self.series)(year)

    @staticmethod
    def _add_query_options(query, options):
        """Adds key value query options, if the provided value is not Null."""
        for k, v in options.iteritems():
            if v is not None:
                query = getattr(query, k)(v)
        return query

    def _execute_query(self, query, format='json', validate=None):
        """Implements common query execution functionality."""
        if validate is not None:
            val = validate(query.url())
        else:
            val = self._validate(query.url())

        if val:
            query = getattr(query, '.' + format)
            return query.get()
        else:
            raise ValueError

    def _validate(self, url):
        return True





class ErgastSeason(Resource):
    """Configures the Ergast API for retrieving Seasons."""
    class Meta:
        list = BASE + JSON
        item = BASE + '(?P<year>)' + JSON


def strip_header(payload):
    mrdata = payload.data['MRData']
    return mrdata


def get_races_from_season(season):
    """Strips off extra header data and just returns an array of races."""

    mrdata = strip_header(season)
    season = mrdata['RaceTable']
    races = season['Races']
    return races


def get_races(year):
    """Get list of races for the given year."""

    ssn = ErgastSeason.objects.get(year=year, client=ergast_client)
    json_races = get_races_from_season(ssn)

    races = []
    for race in json_races:
        circuit = race['Circuit']
        races.append(Race(track=circuit['circuitId'], date=race['date']))

    return races


if __name__ == '__main__':
    # races = get_races(2012)
    #
    # for race in races:
    #     print('Circuit: %s, Date: %s' % (race.track, race.date))

    erg = ErgastApi(series='f1')
    ssn = erg.season(2012)