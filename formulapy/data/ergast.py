__author__ = 'nickroth'

from formulapy.core import Season, Series
from formulapy.data.core import API
import pandas as pd
import slumber
import json

ERGAST_URL = 'http://ergast.com/api/'

class ErgastApi(API):

    base_url = ERGAST_URL

    def __init__(self, series):
        assert series == 'f1' or series == 'fe'
        self.series = series
        self.api = slumber.API(self.base_url, append_slash=False)


    def races(self, year=None):
        if year is not None:
            season = self.season(year=year)
            return season.races


    @property
    def seasons(self):
        options = {'?limit=1000': '?limit=1000'}
        return self.season(year=None, extra_options=options)

    def season(self, year=None, circuitId=None, driverId=None, constructorId=None,
               grid_pos=None, result_pos=None, fastest_rank=None, statusId=None,
               extra_options=None):

        options = {'circuits': circuitId,
                   'drivers': driverId,
                   'constructors': constructorId,
                   'grid': grid_pos,
                   'results': result_pos,
                   'fastest': fastest_rank,
                   'status': statusId}

        if year is None:
            options['seasons'] = 'seasons'

        if extra_options is not None:
            options = dict(options.items() + extra_options.items())

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

    def _validate(self, url):
        return True


class Formula1(Series):
    def __init__(self):
        super(Formula1, self).__init__(api=ErgastApi(series='f1'))


class FormulaE(Series):
    def __init__(self):
        super(FormulaE, self).__init__(api=ErgastApi(series='fe'))



if __name__ == '__main__':

    erg = ErgastApi(series='f1')
    ssn = erg.season(2012)
    print(ssn.to_df())

    print(pd.DataFrame([season.to_rows() for season in erg.seasons]))