__author__ = 'Nick'


import pandas as pd
from copy import copy

from formulapy.plots import lap_box_plot, lap_dist_plot


class DataGroup(object):
    """Enables dot notation into named members of a list."""

    def __init__(self, items):
        if not isinstance(items, list):
            items = [items]
        elif isinstance(items, DataGroup):
            items = items._items

        for item in items:
            setattr(self, item.__id__, item)

        self._items = items
        rows = self.to_row()
        self.df = pd.DataFrame(rows)

    def _make_slice(self, items):
        return self.__class__(items)

    def to_row(self):
        rows = []
        for item in self._items:
            row = item.to_row()

            if isinstance(row, list):
                rows.extend(row)
            else:
                rows.append(row)
        return rows

    def __getattr__(self, attr):
        """Default to passing calls to dataframe."""
        try:
            return getattr(self.df, attr)
        except AttributeError:
            return object.__getattribute__(self, attr)

    def __len__(self):
        return len(self.df)

    def __repr__(self):
        return repr(self.df)

    def __getitem__(self, i):
        if isinstance(i, slice):
            tmp = copy(self._items)
            return self._make_slice(tmp[i])
        else:
            return self._items[i]


class Drivers(DataGroup):
    pass


class Seasons(DataGroup):
    pass


class Races(DataGroup):
    pass


class Constructors(DataGroup):
    pass


class Standings(DataGroup):
    pass


class Laps(DataGroup):

    def __init__(self, items, race):
        super(Laps, self).__init__(items)
        self.race = race

    def driver_box_plot(self, **kwargs):
        if not kwargs.pop('title', None):
            kwargs['title'] = repr(self.race)
        return lap_box_plot(self.df, **kwargs)

    def driver_dist_plot(self, **kwargs):
        if not kwargs.pop('title', None):
            kwargs['title'] = repr(self.race)
        return lap_dist_plot(self.df, **kwargs)

