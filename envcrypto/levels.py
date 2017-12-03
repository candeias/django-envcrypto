"""LevelConfig to describe levels."""
import os
import sys

from .crypto import StateList

# from socket import gethostbyname, gethostname


class NoEnvFileFound(Exception):
    pass


class DeployLevel(object):
    """Configuration for the several run levels."""

    def __init__(self, levels=None):
        """Set the level using the enviroment variable."""
        self.parent = sys.modules[os.environ.get("DJANGO_SETTINGS_MODULE")]
        self.stl = StateList()
        self.levels = levels
        self.current_level = None

        # figure out the run level, using the key
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
