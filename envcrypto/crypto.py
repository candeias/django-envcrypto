"""LevelConfig to describe levels."""
import glob
import json
import os
from binascii import a2b_base64, b2a_base64
from enum import Enum

from cryptography.fernet import Fernet


# from socket import gethostbyname, gethostname


class NoEnvKeyFound(Exception):
    """An error in configuration."""
    pass


class NoEnvFileFound(Exception):
    pass


class NoVarFound(Exception):
    pass


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


class StateList(object):
    """Read a list of states."""

    def __init__(self, *args, key=None, **kwargs):
        """Read the list of states."""
        self.key = key
        if key is None:
            # We try to load the key from the enviroment
            self.key = self.read_env("KEY")

        self.encrypter = Encrypter(key=self.key)
        self.states = []
        self.active_state = None

        self.read_list()

    def read_env(self, name):
        """Read a variable name from the enviroment."""
        result = os.environ.get(name, None)
        if result is None:
            raise NoEnvKeyFound(
                "The {} variable is not setup in the enviroment".format(name))
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

        # try to check if we can read this enviroment
        try:
            result = self.encrypter.decrypt(env_object['signed_name'])
        except:
            return False

        return result == env_object['name']

    def add_active(self, name, value):
        """Add the name value to the state."""
        self.states[self.active_state][name] = self.encrypter.encrypt(value)

    def remove_active(self, name):
        """Add the name value to the state."""
        del self.states[self.active_state][name]

    def save_active(self):
        """Save the active state."""
        with open('{}.env'.format(self.states[self.active_state]['name']), 'w') as f:
            f.write(json.dumps(
                self.states[self.active_state], indent=4, sort_keys=True))

    def get_names_from_active(self):
        """Return the names from the active."""
        result = list(self.states[self.active_state].keys())
        result.remove('name')
        result.remove('signed_name')

        return result

    def get_from_active(self, name):
        """Return a value from the active state."""
        if name not in self.states[self.active_state]:
            raise NoVarFound(
                "Variable {} not defined on enviroment {}.".format(name, self.name))

        return self.encrypter.decrypt(self.states[self.active_state][name])

    @property
    def name(self):
        """Return the current state."""
        return self.states[self.active_state]['name']
