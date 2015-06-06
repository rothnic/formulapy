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

def time_box_plot(data, time_field, id_field, pit_laps=True, std=3, title=''):
    """A generalized box plot that supports generic formatted dataframe with time and id fields."""

    # sort laps by finish order, where not all finish on the last lap
    def add_min(group):
        group['min_time'] = group[time_field].min()
        return group

    data = data.groupby(id_field).apply(add_min)
    time_order = data.sort(['min_time']).name.unique()

    x_label = LAP_TIME_LABEL
    if not pit_laps:
        data = filter_pit_laps(data, time_field=time_field, id_field=id_field, n_std=std)
        x_label += ' (pit laps/outliers filtered)'

    ids = reversed(list(time_order))
    ids = [str(item) for item in ids]

    ax = sns.boxplot(data[time_field], data[id_field], names=ids, order=ids, vert=False)
    plt.title(title)
    plt.ylabel('Driver (sorted by min lap time)')
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