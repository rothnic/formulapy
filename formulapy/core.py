__author__ = 'nickroth'

from atom.api import Atom, Unicode, Typed, Coerced, List, Bool, Property, Callable, ForwardInstance
import datetime
import pandas as pd
from lazy.lazy import lazy

from formulapy.utils import variablize
from formulapy.collections import DataGroup, Drivers, Laps, Races, Seasons
from formulapy.mixins import registry, FormulaModel

pd.set_option('display.notebook_repr_html', True)

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

    seasons = Property()
    _seasons = Typed(Seasons)

    def _get_seasons(self):
        if not self._seasons:
            self.seasons = Seasons(self.api.query(driver_id=self.driverId,
                                                  query_type='seasons'))
        return self._seasons

    def _set_seasons(self, seasons):
        self._seasons = seasons

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

    def to_row(self):
        return {'birth_date': self.birth_date,
                'driverId': self.driverId,
                'shortId': self.shortId,
                'last': self.last,
                'first': self.first,
                'country': self.country,
                'number': self.number,
                'object': self}


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


class LapTiming(FormulaModel):
    driverId = Unicode()
    position = Coerced(int)
    time = Typed(datetime.timedelta)

    @staticmethod
    def parse_time(time_string):
        """Parses a lap timing, assumed to be minutes:seconds.ms"""
        assert isinstance(time_string, unicode)
        time_string = str(time_string)

        if ':' in time_string:
            minutes, seconds = time_string.split(':')
        else:
            minutes = 0
            seconds = time_string

        if '.' in seconds:
            seconds, ms = seconds.split('.')
        else:
            ms = 0

        minutes, seconds, ms = (int(t) for t in [minutes, seconds, ms])
        return datetime.timedelta(minutes=minutes, seconds=seconds,
                                  milliseconds=ms)

    @classmethod
    def from_dict(cls, kwargs):
        kwargs['time'] = cls.parse_time(kwargs.pop('time'))
        return cls(**kwargs)

    def to_row(self):
        dict_props = ['driverId', 'position', 'time']
        row = {k: getattr(self, k) for k in dict_props}
        row['seconds'] = row['time'].total_seconds()
        return row

    def __str__(self):
        return str(self.driverId)

    def __repr__(self):
        return '%s - %s: %s' % (self.position, self.driverId, self.time)


class Lap(FormulaModel):
    number = Coerced(int)
    timings = Typed(DataGroup)

    @classmethod
    def from_dict(cls, kwargs):
        times = [LapTiming.from_dict(timing) for timing in kwargs.pop('Timings')]
        kwargs['timings'] = DataGroup(times)
        return cls(**kwargs)

    def __str__(self):
        return 'lap' + str(self.number)

    def to_row(self):
        time_rows = [dict({'lap_number': self.number}.items() + this_time.to_row().items())
                     for this_time in self.timings]
        return time_rows


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
    _drivers = Typed(Drivers)

    laps = Property()
    _laps = Typed(Laps)

    def _get_drivers(self):
        if not self._drivers:
            query = {'year': self.season,
                     'circuit_id': self.circuit.circuitId,
                     'query_type': 'drivers'}
            self.drivers = self.api.query(**query)
        return self._drivers

    def _set_drivers(self, races):
        self._drivers = DataGroup(races)

    def _get_laps(self):
        if not self._laps:
            query = {'year': self.season,
                     'race_num': str(self.round),
                     'query_type': 'laps'}
            tmp_season = self.api.query(**query)
            self.laps = tmp_season.races[0].laps

        return self._laps

    def _set_laps(self, laps):
        if not isinstance(laps, Laps):
            laps = Laps(laps, race=self)
        self._laps = laps

    @classmethod
    def from_dict(cls, kwargs):
        date = kwargs.pop('date')
        if 'time' in kwargs.keys():
            race_time = kwargs.pop('time')
            kwargs['date'] = datetime.datetime.strptime(date + ' ' + race_time[:-1],
                                    '%Y-%m-%d %H:%M:%S')
        else:
            kwargs['date'] = datetime.datetime.strptime(date, '%Y-%m-%d')

        kwargs['circuit'] = Circuit.from_dict(kwargs.pop('Circuit'))
        kwargs['name'] = kwargs.pop('raceName')
        if 'Laps' in kwargs:
            kwargs['laps'] = [Lap.from_dict(lap) for lap in kwargs.pop('Laps')]
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
    _races = Typed(Races)

    drivers = Property()
    _drivers = Typed(Drivers)

    def _get_races(self):
        if not self._races:
            self.races = self.api.races(year=self.season)
        return self._races

    def _set_races(self, races):
        if not isinstance(races, Races):
            self._races = Races(races)
        else:
            self._races = races

    def _get_drivers(self):
        if not self._drivers:
            self.drivers = self.api.query(year=self.season, query_type='drivers')
        return self._drivers

    def _set_drivers(self, drivers):
        if not isinstance(drivers, Drivers):
            self._drivers = Drivers(drivers)
        else:
            self._drivers = drivers

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

    def to_row(self):
        return {'season': self.season}

    def to_df(self):
        return pd.DataFrame(self.to_rows())

    def __repr__(self):
        return self.__id__

    @property
    def __id__(self):
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
        return Seasons(items=self._seasons)

    @lazy
    def _drivers(self):
        return self._api.all_drivers

    @property
    def drivers(self):
        return Drivers(self._drivers)

    def season(self, year='current'):
        if year == 'current':
            return self.seasons[-1]
        else:
            for season in self.seasons:
                if season.season == year:
                    return season
