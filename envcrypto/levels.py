"""LevelConfig to describe levels."""
import os
import sys
from enum import Enum

from .crypto import NoEnvKeyFound, StateList


# from socket import gethostbyname, gethostname


class Deployment(Enum):
    """A basic run level based on the enviroment variables

    You can create your own deployment by creating a Enum with multiple deployment types
    """

    DEBUG = 'debug'
    STAGING = 'staging'
    PRODUCTION = 'production'


class NoEnvFileFound(Exception):
    """Warns the user that we haven't defined any enviroment class."""

    pass


class DeployLevel(object):
    """Configuration for the several run levels."""

    def __init__(self, levels=None):
        """Set the level using the enviroment variable."""
        if levels is None:
            levels = Deployment
        assert not isinstance(
            levels, Enum), "Pleace pass a Enum as the run levels"

        self.parent = sys.modules[os.environ.get("DJANGO_SETTINGS_MODULE")]
        try:
            self.stl = StateList()
        except NoEnvKeyFound as err:
            self.stl = None
            print("Warning - You haven't setup your enviroment KEY.")

        self.levels = levels
        self.current_level = None

        # figure out the run level, using the key
        if self.stl is not None:
            self.find_current_level()
            self.load_globals()

    def find_current_level(self):
        """Find the current level."""

        for level in self.levels:
            if level.value == self.stl.name:
                self.current_level = level

        if self.current_level is None:
            # we could not find a env level for this level
            raise NoEnvFileFound(
                "Could not find encrypted env for the level {}".format(self.stl.name))

    def load_globals(self):
        """Load all enviroment variables into globals."""
        for name in self.stl.get_names_from_active():
            setattr(self.parent, name, self.stl.get_from_active(name))

    @property
    def LEVEL(self):
        return self.current_level

    def __str__(self):
        return "Deployment: {}".format(self.current_level)
