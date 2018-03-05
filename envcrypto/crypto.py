"""LevelConfig to describe levels."""
import glob
import json
import os
import random
from binascii import a2b_base64, b2a_base64

from cryptography.fernet import Fernet

from .exceptions import (DeploymentLevelNotFound, EnvKeyNotFound,
                         FileWriteError, InvalidEnvFile, InvalidKey,
                         VariableExists, VariableNotFound)


class Encrypter(object):
    """Generate symetric keys and encrypt / decrypts them."""

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

    DJANGO_SECRET_SIZE = 50
    CHAR_LIST = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

    NAME = 'name'
    SIGNED_NAME = 'signed_name'
    SECRET_KEY = 'secret_key'
    KEY = 'KEY'

    def read_env(self, name):
        """Read a variable name from the environment."""
        result = os.environ.get(name, None)
        if result is None:
            raise EnvKeyNotFound(
                "The {} variable is not setup in the environment.\nIn order for django-envcrypto to work you should either supply a KEY in the environment variables or through the command line.".
                format(name))
        return result

    @classmethod
    def new(cls, name, filename, prefix=''):
        """Read a State from a file."""
        key = Encrypter.generate_key()
        encrypter = Encrypter(key)
        result = {}
        result[cls.NAME] = name
        result[cls.SIGNED_NAME] = encrypter.encrypt(name)

        # set the django secret key
        secret_key = ''.join(random.SystemRandom().choice(cls.CHAR_LIST)
                             for i in range(cls.DJANGO_SECRET_SIZE))
        result['SECRET_KEY'] = encrypter.encrypt(secret_key)

        with open('{}-{}.env'.format(prefix, name), 'w') as env_file:
            env_file.write(json.dumps(result, indent=4, sort_keys=True))

        return key

    def __init__(self, filename, *args, key=None, read_from_env=True,
                 **kwargs):
        """Set the variables."""
        self.filename = filename
        self.name = None
        self.django_secret = None
        self.data = {}
        self.key = key

        if key is None and read_from_env:
            self.key = self.read_env(self.KEY)

        try:
            self.encrypter = Encrypter(key=self.key)
        except:
            raise InvalidKey(
                "The supplied key is not a valid key {}".format(key))

        self.load()

    def load(self):
        # read the json file
        try:
            env_object = json.loads(open(self.filename).read())
        except:
            raise InvalidEnvFile

        # try to decrypt the signed name, if we can't we issue a exception
        if self.SIGNED_NAME not in env_object or self.NAME not in env_object or self.SECRET_KEY not in env_object:
            raise InvalidEnvFile
        try:
            self.encrypter.decrypt(env_object[self.SIGNED_NAME])
        except:
            raise InvalidKey

        self.name = env_object[self.NAME]

        # read the remaing variables
        for k in env_object:
            if k not in [self.NAME, self.SIGNED_NAME]:
                try:
                    self.data[k] = self.encrypter.decrypt(env_object[k])
                except:
                    raise InvalidKey

    def save(self):
        """Save the State to disk."""
        result = {}
        result[self.NAME] = self.name
        result[self.SIGNED_NAME] = self.encrypter.encrypt(self.signed_name)
        result[self.SECRET_KEY] = self.encrypter.encrypt(self.django_secret)

        for k in self.data:
            result[k] = self.encrypter.encrypt(self.data[k])

        try:
            with open(self.filename, 'w') as f_file:
                f_file.write(json.dumps(result, indent=4, sort_keys=True))
        except:
            raise FileWriteError

    def add(self, key, value, force=False):
        """Add a variable to the data."""
        # should we prevent rewriting?
        key = key.upper()
        if force:
            self.data[key] = value
            return

        if key in self.data:
            raise VariableExists

        self.data[key] = value

    def remove(self, key):
        """Remove variable by name."""
        if key not in self.data:
            raise VariableNotFound

        del self.data[key]


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
            raise InvalidKey(
                "The supplied key is not a valid key {}".format(key))

        self.states = []
        self.active_state = None

        self.read_list()

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
        raise DeploymentLevelNotFound("Could not find {} state".format(name))

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
            raise VariableNotFound(
                "Variable {} not defined on environment {}.".format(
                    name, self.name))

        return self.encrypter.decrypt(self.states[self.active_state][name])

    @property
    def name(self):
        """Return the current state."""
        return self.states[self.active_state]['name']
