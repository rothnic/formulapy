__author__ = 'nickroth'


class Driver(object):
    def __init__(self, name, num, car, seq_wins=0):
        self.name = name
        self.number = num
        self.car = car
        self.seq_wins = seq_wins


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


class Race(object):
    def __init__(self, drivers, track, temp, rain=False):
        self.temp = temp #ToDo: should affect tires
        self.rain = rain #ToDo: rain should affect prob wreck, safety car, car speeds

    def sim(self):
        pass #ToDo: implement initial sim framework


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


