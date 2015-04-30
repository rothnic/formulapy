__author__ = 'Nick'


from atom.api import Atom, Unicode, Typed, Coerced, List, Bool, Property, Callable, ForwardInstance
from formulapy.data.core import API


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

    @property
    def __id__(self):
        return str(self)