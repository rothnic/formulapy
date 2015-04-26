__author__ = 'Nick'

import matplotlib.pyplot as plt
import seaborn as sns
sns.mpl.rcParams['figure.figsize'] = (16, 10)

from formulapy.data_utils import filter_pit_laps


LAP_TIME_LABEL = 'Lap Time(s)'

CONSTRUCTORS_COLORS = {
    'red bull': 'purple',
    'mercedes': 'teal',
    'ferrari': 'red',
    'lotus': 'gold',
    'mclaren': 'grey',
    'force india': 'orange',
    'toro rosso': 'dark blue',
    'sauber': 'blue',
    'williams': 'white',
    'manor': 'dark orange'
}

def lap_box_plot(laps, pit_laps=True, title=''):

    # sort laps by finish order, where not all finish on the last lap
    finish_order = laps.sort(['lap_number', 'position']).groupby(['driverId'],
                                                               as_index=False).last()
    finish_order = finish_order.sort(['lap_number', 'position'], ascending=[False, True])

    x_label = LAP_TIME_LABEL
    if not pit_laps:
        laps = filter_pit_laps(laps)
        x_label += ' (pit laps/outliers filtered)'

    ids = reversed(finish_order.driverId.values)
    ids = [str(item) for item in ids]

    ax = sns.boxplot(laps.seconds, laps.driverId, names=ids, order=ids, vert=False)
    plt.title(title)
    plt.ylabel('Driver (sorted by finish order)')
    plt.xlabel(x_label)

    return ax


def lap_dist_plot(laps, drivers, pit_laps=True, title=''):

    if not pit_laps:
        laps = filter_pit_laps(laps)

    for driver in drivers:
        ax = sns.distplot(laps.ix[laps.driverId == driver, 'seconds'])

    ax.legend(drivers)
    plt.title(title)
    plt.xlabel(LAP_TIME_LABEL)

    return ax