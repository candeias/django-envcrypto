"""LevelConfig to describe levels."""
import os
import sys
from enum import Enum

from .exceptions import DeploymentIsNotAEnum
from .state import StateList


class Deployment(Enum):
    """A basic run level based on the environment variables

    You can create your own deployment by creating a Enum with multiple deployment types
    """

    DEBUG = 'debug'
    STAGING = 'staging'
    PRODUCTION = 'production'


class DeployLevel(object):
    """Configuration for the several run levels."""

    def __init__(self, levels=None, key=None):
        """Set the level using the environment variable."""
        if levels is None:
            levels = Deployment
        else:
            if not isinstance(levels, Enum):
                raise DeploymentIsNotAEnum(
                    "Please pass a Enum as the run levels")

        self.levels = levels
        self.current_level = None

        self.parent = sys.modules[os.environ.get("DJANGO_SETTINGS_MODULE")]
        self.state_list = StateList(key=key)
        self.state = self.state_list.get()

        # use the name of the state to get the current level
        if self.state is None:
            return

        self.current_level = levels(self.state.name)
        self.state_list.check_variables()
        self.load_globals()

    def load_globals(self):
        """Load all environment variables into globals."""
        for key, value in self.state:
            setattr(self.parent, key, value)

    @property
    def LEVEL(self):
        return self.current_level

    def __str__(self):
        return "Deployment: {}".format(self.current_level)
