__author__ = 'nickroth'

from formulapy.core import Track, PitLane

class SpaPitLane(PitLane):
    def __init__(self, inlap_cost=5., outlap_cost=13.):
        super(SpaPitLane, self).__init__(inlap_cost, outlap_cost)


class Spa(Track):
    def __init__(self, name='Spa', laps=44, fuel_gain=0.12, sc_prob=0.1, dnf_factor=1, sc_laps=4,
                 sc_laptime=160, sc_follow=0.4, pit_window=10., drs_gain=0.4, drs_wear=0.1, follow=0.2,
                 defense_time=0.4, ot_thresh=1.0, ot_speed=0.02, start_sd=1.0, t_diff=1.3, rel_wear=0.5,
                 track_wear=15, pitlane=None):

        if pitlane is None:
            pitlane = SpaPitLane()

        super(Spa, self).__init__(name, laps, pitlane, fuel_gain, sc_prob, dnf_factor, sc_laps, sc_laptime,
                                  sc_follow, pit_window, drs_gain, drs_wear, follow, defense_time, ot_thresh,
                                  ot_speed, start_sd, t_diff, rel_wear, track_wear)