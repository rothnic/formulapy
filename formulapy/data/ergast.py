__author__ = 'nickroth'


from restorm.clients.jsonclient import JSONClient
from restorm.resource import Resource
from formulapy.core import Race

ergast_client = JSONClient(root_uri='http://ergast.com/api/')


class ErgastSeason(Resource):
    """Configures the Ergast API for retrieving Seasons."""
    class Meta:
        list = r'^f1/.json$'
        item = r'^f1/(?P<year>).json$'


def strip_header(payload):
    mrdata = payload.data['MRData']
    return mrdata


def get_races_from_season(season):
    """Strips off extra header data and just returns an array of races."""

    mrdata = strip_header(season)
    season = mrdata['RaceTable']
    races = season['Races']
    return races


def get_races(year):
    """Get list of races for the given year."""

    ssn = ErgastSeason.objects.get(year=year, client=ergast_client)
    json_races = get_races_from_season(ssn)

    races = []
    for race in json_races:
        circuit = race['Circuit']
        races.append(Race(track=circuit['circuitId'], date=race['date']))

    return races


if __name__ == '__main__':
    races = get_races(2012)

    for race in races:
        print('Circuit: %s, Date: %s' % (race.track, race.date))