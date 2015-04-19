__author__ = 'nickroth'

from atom.api import Atom, Unicode,Typed, Coerced, List, Bool
import datetime
import pandas as pd
from lazy.lazy import lazy


class Location(Atom):

    country = Unicode()
    lat = Coerced(float)
    long = Coerced(float)
    locality = Unicode()


class Driver(object):
    def __init__(self, name, num, car, seq_wins=0):
        self.name = name
        self.number = num
        self.car = car
        self.seq_wins = seq_wins


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


class Race(Atom):

    date = Typed(datetime.datetime)
    name = Unicode()
    round = Coerced(int)
    season = Coerced(int)
    url = Unicode()
    temp = Coerced(float)              #ToDo: should affect tires
    rain = Bool(default=False)         #ToDo: rain should affect prob wreck, safety car, car speeds

    circuit = Typed(Circuit)
    drivers = List(Typed(Driver))

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


class Season(Atom):
    season = Coerced(int)
    races = List(Typed(Race))

    @classmethod
    def from_dict(cls, kwargs):
        if 'races' in kwargs.keys():
            kwargs['races'] = [Race.from_dict(race) for race in kwargs['races']]
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
    def __init__(self, api):
        self._api = api

    @lazy
    def seasons(self):
        return self._api.seasons

    def season(self, year='current'):
        if year == 'current':
            return self.seasons[-1]
        else:
            for season in self.seasons:
                if season.season == year:
                    return season


