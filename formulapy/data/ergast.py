__author__ = 'nickroth'

import slumber
import json
import datetime
import pandas as pd

from atom.api import Atom, Unicode,Typed, Coerced, List

ERGAST_URL = 'http://ergast.com/api/'


class Location(Atom):

    country = Unicode()
    lat = Coerced(float)
    long = Coerced(float)
    locality = Unicode()


class Circuit(Atom):

    circuitId = Unicode()
    circuitName = Unicode()
    url = Unicode()
    location = Typed(Location)

    @classmethod
    def from_dict(cls, kwargs):
        location = kwargs.pop('Location')
        kwargs['location'] = Location(**location)
        return cls(**kwargs)

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


class Race(Atom):

    date = Typed(datetime.datetime)
    name = Unicode()
    round = Coerced(int)
    season = Coerced(int)
    url = Unicode()
    circuit = Typed(Circuit)

    @classmethod
    def from_dict(cls, kwargs):
        date = kwargs.pop('date')
        race_time = kwargs.pop('time')
        kwargs['date'] = datetime.datetime.strptime(date + ' ' + race_time[:-1],
                                   '%Y-%m-%d %H:%M:%S')
        kwargs['circuit'] = Circuit.from_dict(kwargs.pop('Circuit'))
        kwargs['name'] = kwargs.pop('raceName')
        return cls(**kwargs)

    @property
    def time(self):
        return self.date.time()

    def to_row(self):
        dict_props = ['date', 'name', 'round', 'season', 'time', 'url']
        cir = self.circuit.to_row()
        return dict({k: getattr(self, k) for k in dict_props}.items() + cir.items())


class Season(Atom):
    season = Coerced(int)
    races = List(Typed(Race))

    @classmethod
    def from_dict(cls, kwargs):
        kwargs['races'] = [Race.from_dict(race) for race in kwargs['races']]
        return cls(**kwargs)

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
        return Season.from_dict({'season': data['season'], 'races': data['Races']})

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