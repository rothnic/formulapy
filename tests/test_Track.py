__author__ = 'nickroth'

from formulapy.models.tracks import Spa

def test_Spa():
    spa  = Spa()
    assert(spa.laps > 0)
    print spa.laps

if __name__ == '__main__':
    test_Spa()