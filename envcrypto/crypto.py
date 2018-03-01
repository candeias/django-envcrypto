"""LevelConfig to describe levels."""
import glob
import json
import os
import random
from binascii import a2b_base64, b2a_base64

from cryptography.fernet import Fernet

from .exceptions import (NoDeploymentLevelFound, NoEnvKeyFound,
                         NoValidKeyFound, NoVarFound)


class Encrypter(object):
    @classmethod
    def generate_key(cls):
        """Generate a random key."""
        return Fernet.generate_key()

    def __init__(self, key=None):
        self.fernet = Fernet(key)

    def encrypt(self, message):
        ciphertext = self.fernet.encrypt(message.encode("utf-8"))
        return b2a_base64(ciphertext).decode("utf-8").strip('\n')

    def decrypt(self, digest):
        ciphertext = a2b_base64(digest.encode("utf-8"))
        return self.fernet.decrypt(ciphertext).decode("utf-8")


class State(object):
    """A State object."""

    DJANG_SECRET_SIZE = 50

    def __init__(self, name):
        """Set the variables."""
        self.key = Encrypter.generate_key()
        self.name = name

    def save(self, prefix=""):
        """Save the State to disk."""
        encrypter = Encrypter(self.key)
        result = {}
        result['name'] = self.name
        result['signed_name'] = encrypter.encrypt(self.name)

        # set the django secret key
        secret_key = ''.join(random.SystemRandom().choice(
            'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
            for i in range(self.DJANG_SECRET_SIZE))
        result['SECRET_KEY'] = encrypter.encrypt(secret_key)

        with open('{}-{}.env'.format(prefix, self.name), 'w') as f:
            f.write(json.dumps(result, indent=4, sort_keys=True))


class StateList(object):
    """Read a list of states."""

    # the list of states that cannot be read from the outside
    NONREADABLE_STATES = {'name': 1, 'signed_name': 1}

    # the list of states that can't be copied to the outside
    PROTECTED_STATES = {'name': 1, 'signed_name': 1, 'SECRET_KEY': 1}

    def __init__(self, *args, key=None, read_from_env=True, **kwargs):
        """Read the list of states."""
        self.key = key
        if key is None and read_from_env:
            # We try to load the key from the environment
            self.key = self.read_env("KEY")

        try:
            self.encrypter = Encrypter(key=self.key)
        except:
            raise NoValidKeyFound(
                "The supplied key is not a valid key {}".format(key))

        self.states = []
        self.active_state = None

        self.read_list()

    def read_env(self, name):
        """Read a variable name from the environment."""
        result = os.environ.get(name, None)
        if result is None:
            raise NoEnvKeyFound(
                "The {} variable is not setup in the environment.\nIn order for django-envcrypto to work you should either supply a KEY in the environment variables or through the command line.".
                format(name))
        return result

    def read_list(self):
        """Read the list of files."""
        env_files = glob.glob('*.env')
        for i in range(len(env_files)):
            env_file = env_files[i]
            if self.process_env_file(env_file):
                self.active_state = i

    def process_env_file(self, filepath=None):
        """Process the filepath."""
        env_object = json.loads(open(filepath).read())
        self.states.append(env_object)

        # try to check if we can read this environment
        try:
            result = self.encrypter.decrypt(env_object['signed_name'])
        except:
            return False

        return result == env_object['name']

    def get_list_of_states(self):
        """Return the list of known states."""
        result = []

        for i in range(len(self.states)):
            result.append(self.states[i]['name'])

        return result

    def add_active(self, name, value):
        """Add the name value to the state."""
        self.states[self.active_state][name] = self.encrypter.encrypt(value)

    def remove_active(self, name):
        """Add the name value to the state."""
        del self.states[self.active_state][name]

    def save_active(self):
        """Save the active state."""
        with open('{}.env'.format(self.states[self.active_state]['name']),
                  'w') as f_file:
            f_file.write(
                json.dumps(
                    self.states[self.active_state], indent=4, sort_keys=True))

    def get_state_from_name(self, name):
        """Return the state for this name."""
        for i in range(len(self.states)):
            if self.states[i]['name'] == name:
                return self.states[i]

        # if we did not find the state raise an exception
        raise NoDeploymentLevelFound("Could not find {} state".format(name))

    def get_names_from_active(self):
        """Return the names from the active."""
        result = []

        for state in self.states[self.active_state].keys():
            if state not in self.PROTECTED_STATES:
                result.append(state)

        return result

    def get_from_active(self, name):
        """Return a value from the active state."""
        if name not in self.states[self.active_state]:
            raise NoVarFound(
                "Variable {} not defined on environment {}.".format(
                    name, self.name))

        return self.encrypter.decrypt(self.states[self.active_state][name])

    @property
    def name(self):
        """Return the current state."""
        return self.states[self.active_state]['name']
