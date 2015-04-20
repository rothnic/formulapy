__author__ = 'nickroth'

from formulapy.core import Season, Series, Driver
from formulapy.data.core import API
import slumber
import json

# constants
ERGAST_URL = 'http://ergast.com/api/'
ALL_DATA = {'?limit=1000': '?limit=1000'}


class ErgastApi(API):

    base_url = ERGAST_URL

    def __init__(self, series):
        assert series == 'f1' or series == 'fe'
        self.series = series
        self.api = slumber.API(self.base_url, append_slash=False)

    def races(self, year=None):
        if year is not None:
            season = self.query(year=year)
            return season.races

    @property
    def all_drivers(self):
        return self.query(year=None, query_type='drivers')

    def driver(self, driver_id=None, year=None, circuit_id=None, constructor_id=None,
               grid_pos=None, result_pos=None, fastest_rank=None, status_id=None):
        pass

    @property
    def all_seasons(self):
        return self.query(year=None, query_type='seasons')

    def get_extra_options(self, query_type):
        if query_type == 'drivers':
            query_type_dict = {'drivers': 'drivers'}
        elif query_type == 'seasons':
            query_type_dict = {'seasons': 'seasons'}
        else:
            return None

        return self.combine_dicts(query_type_dict, ALL_DATA)

    @staticmethod
    def combine_dicts(a, b):
        return dict(a.items() + b.items())

    def query(self, year=None, circuit_id=None, driver_id=None, constructor_id=None,
              grid_pos=None, result_pos=None, fastest_rank=None, status_id=None,
              query_type=None):

        options = {'circuits': circuit_id,
                   'drivers': driver_id,
                   'constructors': constructor_id,
                   'grid': grid_pos,
                   'results': result_pos,
                   'fastest': fastest_rank,
                   'status': status_id}

        if query_type is not None:
            options = self.get_extra_options(query_type=query_type)

        query = self._get_base_query(year)
        query = self._add_query_options(query, options)
        response = self._execute_query(query)
        data, query_data = self._parse_header(response)
        return self._parse_data(data)

    @staticmethod
    def _parse_header(response):
        if isinstance(response, str):
            response = json.loads(response)
        query_keys = ['xmlns', 'url', 'series', 'limit', 'offset', 'total']
        mrdata = response['MRData']

        # Find the key piece of information that was returned for the query as a string
        result_key = set(mrdata.keys()).difference(query_keys)
        result_key = str(list(result_key)[0])

        data = mrdata[result_key]
        query_data = {query_key: mrdata[query_key] for query_key in query_keys}
        return data, query_data

    def _parse_data(self, data):
        assert isinstance(data, dict)

        seasons = data.pop('Seasons', None)
        if seasons:
            return [self._parse_season(season) for season in seasons]

        drivers = data.pop('Drivers', None)
        if drivers:
            return [Driver.from_dict(driver) for driver in drivers]

        if 'season' in data.keys():
            return self._parse_season(data)

    @staticmethod
    def _parse_season(data):
        season = {'season': data['season']}
        if 'Races' in data.keys():
            season['races'] = data['Races']
        return Season.from_dict(season)

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
            if v == k:
                query = getattr(query, k)
            elif v is not None:
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

    @staticmethod
    def _validate(url):
        return True


class Formula1(Series):
    def __init__(self):
        super(Formula1, self).__init__(api=ErgastApi(series='f1'))


class FormulaE(Series):
    def __init__(self):
        super(FormulaE, self).__init__(api=ErgastApi(series='fe'))



if __name__ == '__main__':

    f1 = Formula1()
    f1