"""LevelConfig to describe levels."""
import glob
import json
import logging
import os
import random

from .crypto import Encrypter
from .exceptions import (DeploymentLevelNotFound, EnvKeyNotFound,
                         FileWriteError, InvalidEnvFile, InvalidKey,
                         VariableExists, VariableMissing, VariableNotFound)


def read_env(name):
    """Read a variable name from the environment."""
    result = os.environ.get(name, None)
    if result is None:
        raise EnvKeyNotFound(
            "The {} variable is not setup in the environment.\nIn order for django-envcrypto to work you should either supply a KEY in the environment variables or through the command line.".
            format(name))
    return result


class State(object):
    """A State object."""

    FILE_EXTENSION = "env"
    DJANGO_SECRET_SIZE = 50
    CHAR_LIST = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

    NAME = 'name'
    SIGNED_NAME = 'signed_name'
    SECRET_KEY = 'SECRET_KEY'
    KEY = 'KEY'

    CRYPTO_TYPE = 'cryto_family'
    CRYPTO_ALGORITHM = 'crypto_algorithm'

    VERSION = 'version'

    CURRENT_VERSION = '0.8.4'

    CONTROLED_VOCABULARY = [
        NAME, SIGNED_NAME, SECRET_KEY, CRYPTO_ALGORITHM, CRYPTO_TYPE, VERSION
    ]
    REQUIRED_VOCABULARY = [NAME, SIGNED_NAME, SECRET_KEY]

    @classmethod
    def new(cls, name):
        """Read a State from a file."""
        key = Encrypter.generate_key()
        encrypter = Encrypter(key)
        result = {}
        result[cls.NAME] = name
        result[cls.CRYPTO_TYPE] = 'symmetric'
        result[cls.CRYPTO_ALGORITHM] = 'fernet'
        result[cls.VERSION] = cls.CURRENT_VERSION
        result[cls.SIGNED_NAME] = encrypter.encrypt(name)

        # set the django secret key
        secret_key = ''.join(random.SystemRandom().choice(cls.CHAR_LIST)
                             for i in range(cls.DJANGO_SECRET_SIZE))
        result['SECRET_KEY'] = encrypter.encrypt(secret_key)

        final_filename = '{}.{}'.format(name, cls.FILE_EXTENSION)
        with open(final_filename, 'w') as env_file:
            env_file.write(json.dumps(result, indent=4, sort_keys=True))

        # we read a new state object
        state = State(final_filename, key=key)

        return state

    def __init__(self,
                 filename,
                 *args,
                 key=None,
                 read_from_env=True,
                 read_empty=False,
                 **kwargs):
        """Set the variables."""
        self.filename = filename
        self.name = None
        self.crypto_type = None
        self.crypto_algorithm = None
        self.version = None
        self.django_secret = None
        self.data = {}
        self.key = key
        self.decrypted = False

        if key is None and read_from_env:
            self.key = read_env(self.KEY)

        try:
            self.encrypter = Encrypter(key=self.key)
        except:
            raise InvalidKey(
                "The supplied key is not a valid key {}".format(key))

        self.load(read_empty=read_empty)

    def read_file(self):
        """Read the file and check that it is valid."""
        # read the json file
        try:
            env_object = json.loads(open(self.filename).read())
        except:
            raise InvalidEnvFile

        # Check that the required vocabulary is available
        for vocabulary in self.REQUIRED_VOCABULARY:
            if vocabulary not in env_object:
                raise InvalidEnvFile

        return env_object

    def process_file_update(self, env_object):
        """Process any required update to the file format."""
        # read the self properties
        do_version_update = False
        try:
            self.crypto_type = env_object[self.CRYPTO_TYPE]
        except:
            self.crypto_type = 'symmetric'
            do_version_update = True
        try:
            self.crypto_algorithm = env_object[self.CRYPTO_ALGORITHM]
        except:
            self.crypto_algorithm = 'fernet'
            do_version_update = True

        try:
            self.version = env_object[self.VERSION]
        except:
            self.version = self.CURRENT_VERSION
            do_version_update = True

        return do_version_update

    def load_and_decrypt_data(self, env_object):
        """We decrypt the data."""
        self.django_secret = self.encrypter.decrypt(
            env_object[self.SECRET_KEY])

        # read the remaing variables
        for k in env_object:
            if k not in self.CONTROLED_VOCABULARY:
                try:
                    self.data[k] = self.encrypter.decrypt(env_object[k])
                except:
                    raise InvalidKey

    def load_data(self, env_object):
        """We only load the data."""
        for k in env_object:
            if k not in self.CONTROLED_VOCABULARY:
                self.data[k] = None

    def load(self, read_empty=False):
        """Load a file and process it."""
        env_object = self.read_file()
        self.name = env_object[self.NAME]

        # can we decrypt the state?
        if read_empty:
            self.load_data(env_object)
            return

        try:
            self.encrypter.decrypt(env_object[self.SIGNED_NAME])

        except:
            # we do nothing if the can decrypt the state
            raise InvalidKey

        self.decrypted = True
        self.load_and_decrypt_data(env_object)
        do_version_update = self.process_file_update(env_object)

        # only decrypt the objects if we have the right key
        if self.decrypted and do_version_update:
            self.update()

    def check_decrypted(self):
        """Check that the state is decrypted and raise an exception otherwise."""
        # if we haven't been able to decrypt the state we raise and exception
        if not self.decrypted:
            raise InvalidKey

    def update(self):
        """Update the file to the current version."""
        logging.warning("Updating your environment file")
        self.save()

    def save(self):
        """Save the State to disk."""
        self.check_decrypted()
        result = {}
        result[self.NAME] = self.name
        result[self.SIGNED_NAME] = self.encrypter.encrypt(self.name)
        result[self.CRYPTO_TYPE] = self.crypto_type
        result[self.CRYPTO_ALGORITHM] = self.crypto_algorithm
        result[self.VERSION] = self.version

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

    def __iter__(self):
        """Return each of the data values."""
        yield (self.SECRET_KEY, self.django_secret)
        for k in self.data:
            yield (k, self.data[k])

    def __contains__(self, key):
        """Check if the state contains a variable."""
        return key == self.SECRET_KEY or key in self.data

    def get(self):
        """Return a collection of the data."""
        for k in self.data:
            yield (k, self.data[k])

    def remove(self, key):
        """Remove variable by name."""
        key = key.upper()
        if key not in self.data:
            raise VariableNotFound

        del self.data[key]


class StateList(object):
    """Read a list of states."""

    def __init__(self,
                 *args,
                 key=None,
                 raise_error_on_key=False,
                 load_filter='*',
                 **kwargs):
        """Read the list of states."""
        self.key = key
        self.load_filter = load_filter
        self.list_of_states = []
        self.current_state_index = None

        if self.key is None:
            try:
                self.key = read_env("KEY")
            except:
                if raise_error_on_key:
                    logging.warning(
                        "Django-Envcrypto can't find a KEY in the environment. It will continue without injecting any variable."
                    )
                    raise EnvKeyNotFound
                return

        try:
            self.encrypter = Encrypter(key=self.key)
        except:
            raise InvalidKey(
                "The supplied key is not a valid key {}".format(key))

        self.read_list()

        if self.current_state_index is None:
            # we could find any decryptable state, so we raise an Exception
            raise DeploymentLevelNotFound

    def get(self):
        """Return the active state."""
        if self.current_state_index is None:
            return None

        return self.list_of_states[self.current_state_index]

    def read_list(self):
        """Read the list of files."""
        env_files = glob.glob('{}.{}'.format(self.load_filter,
                                             State.FILE_EXTENSION))
        for i in range(len(env_files)):
            try:
                state = State(env_files[i], key=self.key)
                self.current_state_index = i
            except InvalidKey:
                # still add this tate to
                state = State(env_files[i], key=self.key, read_empty=True)

            self.list_of_states.append(state)

    def check_variables(self, raise_on_warning=False):
        """Check that all files have the same variables."""
        # first create a dictionary of all variables in all states
        missing = {}
        for state in self.list_of_states:
            for key, value in state:
                if key not in missing:
                    missing[key] = []

        # now for each state check what variables do exist there
        for key in missing:
            temp = []
            for state in self.list_of_states:
                if key not in state:
                    temp.append(state.name)
            missing[key] = temp

        # finally output any missing variable in a state
        # (the iteration is done again for code clarity)
        for key in missing:
            if missing[key]:
                logging.warning('Variable {} missing in states {}'.format(
                    key, missing[key]))
                if raise_on_warning:
                    raise VariableMissing

    @property
    def name(self):
        """Return the current state."""
        return self.current_state.name
