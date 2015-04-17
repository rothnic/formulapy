__author__ = 'nickroth'

import slumber
from restorm.clients.jsonclient import JSONClient
from restorm.resource import Resource
from formulapy.core import Race
import json
import datetime
import pandas as pd

ERGAST_URL = 'http://ergast.com/api/'
ergast_client = JSONClient(root_uri=ERGAST_URL)

BASE = r'^f1/'
JSON = '.json$'


class ErgastParser(object):

    def __init__(self, kwargs):
        for k, v in kwargs.iteritems():
            print k

        self.set(**kwargs)


class Location(object):

    def __init__(self, country, lat, long, locality):
        self.country = country
        self.lat = float(lat)
        self.long = float(long)
        self.locality = locality

    @classmethod
    def from_dict(cls, kwargs):
        country = kwargs.pop('country')
        lat = kwargs.pop('lat')
        long = kwargs.pop('long')
        locality = kwargs.pop('locality')
        return cls(country, lat, long, locality)


class Circuit(object):
    def __init__(self, circuitId, circuitName, url, location):
        self.circuitId = circuitId
        self.circuitName = circuitName
        self.url = url
        self.location = Location.from_dict(location)

    @classmethod
    def from_dict(cls, kwargs):
        circuitId = kwargs.pop('circuitId')
        circuitName = kwargs.pop('circuitName')
        url = kwargs.pop('url')
        return cls(circuitId, circuitName, url, kwargs['Location'])

    @property
    def country(self):
        return self.location.country

    @property
    def lat(self):
        return self.location.lat

    @property
    def long(self):
        return self.location.long

    @property
    def city(self):
        return self.location.locality

    def to_row(self):
        dict_props = ['circuitId', 'circuitName', 'city', 'country', 'lat', 'long', 'url']
        return {k: getattr(self, k) for k in dict_props}


class Race(object):
    def __init__(self, date, raceName, round, season, race_time, url, circuit):
        self.date = datetime.datetime.strptime(date + ' ' + race_time[:-1],
                                               '%Y-%m-%d %H:%M:%S')
        self.name = raceName
        self.round = int(round)
        self.season = int(season)
        self.time = self.date.time()
        self.url = url
        self.circuit = Circuit.from_dict(circuit)

    @classmethod
    def from_dict(cls, kwargs):
        date = kwargs.pop('date')
        raceName = kwargs.pop('raceName')
        round = kwargs.pop('round')
        season = kwargs.pop('season')
        race_time = kwargs.pop('time')
        url = kwargs.pop('url')
        return cls(date, raceName, round, season, race_time, url, kwargs['Circuit'])

    def to_row(self):
        dict_props = ['date', 'name', 'round', 'season', 'time', 'url']
        cir = self.circuit.to_row()
        return dict({k: getattr(self, k) for k in dict_props}.items() + cir.items())


class Season(object):
    def __init__(self, season, races):
        self.season = int(season)
        self.races = [Race.from_dict(race) for race in races]

    def to_rows(self):
        rows = []
        for race in self.races:
            rows.append(race.to_row())
        return rows

    def to_df(self):
        return pd.DataFrame(self.to_rows())


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
        data, query_data = self._parse_header(response)
        return self._parse_data(data)

    @staticmethod
    def _parse_header(response):
        data = json.loads(response)
        query_keys = ['xmlns', 'url', 'series', 'limit', 'offset', 'total']
        mrdata = data['MRData']

        # Find the key piece of information that was returned for the query as a string
        result_key = set(mrdata.keys()).difference(query_keys)
        result_key = str(list(result_key)[0])

        data = mrdata[result_key]
        query_data = {query_key: mrdata[query_key] for query_key in query_keys}
        return data, query_data

    @staticmethod
    def _parse_data(data):
        return Season(data['season'], data['Races'])

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


if __name__ == '__main__':

    erg = ErgastApi(series='f1')
    ssn = erg.season(2012)
    print(ssn.to_df())