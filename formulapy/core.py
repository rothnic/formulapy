__author__ = 'nickroth'

from atom.api import Atom, Unicode, Typed, Coerced, List, Bool, Property, Callable
import datetime
import pandas as pd
from lazy.lazy import lazy
from formulapy.data.core import API
from formulapy.utils import variablize


class DataGroup(object):
    """Enables dot notation into named members of a list."""

    def __init__(self, data_list):
        for data in data_list:
            setattr(self, str(data), data)
        self.data = data_list

    def __getitem__(self, i):
        return self.data[i]

    def __repr__(self):
        return str([str(data) for data in self.data])

    def __len__(self):
        return len(self.data)


class ApiRegistry(object):
    """Global registry for API calls, so each nested object doesn't need reference."""

    def __init__(self):
        self._api = None

    @property
    def api(self):
        return self._api

    def register(self, api):
        if self._api is None:
            self._api = api


# Create the global registry
registry = ApiRegistry()


class FormulaModel(Atom):
    """Base class to provide reference to the registered api."""

    api = Property()
    _api = Typed(API)

    def _get_api(self):
        if registry.api is not None:
            return registry.api
        else:
            raise EnvironmentError('API has not been registered.')

    def _set_api(self, api):
        self._api = api


class Location(Atom):
    country = Unicode()
    lat = Coerced(float)
    long = Coerced(float)
    locality = Unicode()


class Driver(FormulaModel):
    birth_date = Typed(datetime.datetime)
    driverId = Unicode()
    shortId = Coerced(str)
    last = Unicode()
    first = Unicode()
    country = Unicode()
    url = Unicode()
    number = Coerced(int)

    seasons = Property

    @classmethod
    def from_dict(cls, kwargs):
        if 'dateOfBirth' in kwargs.keys():
            dob = kwargs.pop('dateOfBirth')
            if dob:
                kwargs['birth_date'] = datetime.datetime.strptime(dob,
                                        '%Y-%m-%d')
        kwargs['last'] = kwargs.pop('familyName')
        kwargs['first'] = kwargs.pop('givenName')
        kwargs['country'] = kwargs.pop('nationality')

        if 'permanentNumber' in kwargs.keys():
            kwargs['number'] = kwargs.pop('permanentNumber')

        if 'code' in kwargs.keys():
            kwargs['shortId'] = kwargs.pop('code', None)

        return cls(**kwargs)


    def __str__(self):
        return str(self.driverId)

    def __repr__(self):
        return str(self.first + ' ' + self.last)


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
        dict_props = ['circuitId', 'circuitName', 'city', 'country', 'lat', 'long']
        return {k: getattr(self, k) for k in dict_props}


class Track(object):
    def __init__(self, name, laps, pitlane, fuel_gain, sc_prob, dnf_factor, sc_laps, sc_laptime, sc_follow, pit_window,
                 drs_gain, drs_wear, follow, defense_time, ot_thresh, ot_speed, start_sd, t_diff, rel_wear, track_wear):
        self.name = name
        self.laps = laps
        #ToDo: factor out Track performance aspects into separate components, so it isn't a massive single structure


class TrackLayout(object):
    def __init__(self, laps, lap_dist=None, sectors=None):
        assert(lap_dist is not sectors) # If list of sectors is not provided, then we need dist
        self.sectors = sectors
        self._distance = lap_dist

    @property
    def distance(self):
        if self.sectors is not None:
            return sum([sec.distance for sec in self.sectors])
        else:
            return self._distance


class DRS_Config(object):
    def __init__(self, drs_zones):
        self.drs_zones = drs_zones


class DRS_Zone(object):
    def __init__(self, detect_km, activate_km):
        self.detect_km = detect_km
        self.activate_km = activate_km


class Sector(object):
    def __init__(self, dist):
        self.distance = dist


class Corner(object):
    def __init__(self, speed_in, speed_out, angle, altitude):
        self.speed_in = speed_in
        self.speed_out = speed_out
    #ideally, we'd train a corner model based on in and exit speeds of past data
    #we may leave this here for now unused, since the matlab project only models at the lap level


class PitLane(object):
    def __init__(self, inlap_cost, outlap_cost):
        pass

    @classmethod
    def fromLength(cls, len, speed_limit):
        return cls #ToDo: allow creation of pitlane from length, speed limit, etc.


class Race(FormulaModel):

    date = Typed(datetime.datetime)
    name = Unicode()
    round = Coerced(int)
    season = Coerced(int)
    url = Unicode()
    temp = Coerced(float)              #ToDo: should affect tires
    rain = Bool(default=False)         #ToDo: rain should affect prob wreck, safety car, car speeds

    circuit = Typed(Circuit)
    drivers = Property()
    _drivers = Typed(DataGroup)

    def _get_drivers(self):
        if not self._drivers:
            query = {'year': self.season,
                     'circuit_id': self.circuit.circuitId,
                     'query_type': 'drivers'}
            self.drivers = DataGroup(self.api.query(**query))
        return self._drivers

    def _set_drivers(self, races):
        self._drivers = DataGroup(races)

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
        dict_props = ['date', 'name', 'round', 'season', 'time']
        cir = self.circuit.to_row()
        return dict({k: getattr(self, k) for k in dict_props}.items() + cir.items())

    def __repr__(self):
        return ('%s-%s: %s') % (self.season, self.round, self.name)

    def __str__(self):
        name = variablize(self.name)
        return name + '_' + str(self.round)


class Season(FormulaModel):
    season = Coerced(int)
    races = Property()
    _races = Typed(DataGroup)

    def _get_races(self):
        if not self._races:
            self.races = DataGroup(self.api.races(year=self.season))
        return self._races

    def _set_races(self, races):
        self._races = DataGroup(races)

    @classmethod
    def from_dict(cls, kwargs):
        if 'races' in kwargs.keys():
            kwargs['races'] = [Race.from_dict(race) for race in kwargs.pop('races')]
        return cls(**kwargs)

    def to_rows(self):

        if self.races:
            rows = []
            for race in self.races:
                race_row = race.to_row()
                race_row['season'] = self.season
                rows.append(race_row)
        else:
            rows = {'season': self.season}
        return rows

    def to_df(self):
        return pd.DataFrame(self.to_rows())

    def __str__(self):
        return 's' + str(self.season)


class Car(object):
    def __init__(self, top_speed0, down_force0, max_fuel, setup=None, engine=None):
        pass
    #ToDo: incorporate a "baseline" setup that we can vary based on a specific setup
    # Initially, we may just interpolate between baseline cases and mods to that, while planning for higher fidelity
    # Example car/engine model in OpenMDAO: http://openmdao.org/releases/0.0.11/docs/user-guide/example.html
    # Speed, hp, weight: http://phors.locost7.info/phors06.htm


class CarSetup(object):
    def __init__(self, down_force, fuel):
        pass
    #ToDo: add more aspects, otherwise could just be a single input into Car


class Engine(object):
    def __init__(self, hp, fail_dist=None):
        self.fail_dist = fail_dist #ToDo: implement default distribution for failures


class Tire(object):
    def __init__(self, compound):
        self.compound = compound
        self.degradation = self.degradation_dist()

    def time_impact(self, lap):
        """
        Impact on time on the condition of the tire.

        :param lap: the lap the simulation is at
        :return: a factor of the time impact
        """
        pass #ToDO: implement distribution for impact on time based on lap and compound

    def degradation_dist(self):
        """
        Depends on driver and compound.

        :return:
        """
        pass #ToDo: implement distribution for when this instance of tire reaches degradation states (binomial?)


class Event(object):
    def __init__(self):
        pass


class Rain(Event):
    def __init__(self):
        super(Rain, self).__init__()


class Overtake(Event):
    def __init__(self):
        super(Overtake, self).__init__()


class Wreck(Event):
    def __init__(self):
        super(Wreck, self).__init__()


class Series(object):
    """The highest level component for accessing data for a racing series."""

    def __init__(self, api):
        self._api = api
        registry.register(api)

    @lazy
    def _seasons(self):
        return self._api.all_seasons

    @property
    def seasons(self):
        return DataGroup(self._seasons)

    @lazy
    def _drivers(self):
        return self._api.drivers

    @property
    def drivers(self):
        return DataGroup(self._drivers)

    def season(self, year='current'):
        if year == 'current':
            return self.seasons[-1]
        else:
            for season in self.seasons:
                if season.season == year:
                    return season


