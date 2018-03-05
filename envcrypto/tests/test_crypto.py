"""Test the crypto module."""
import glob
import os

from ..crypto import Encrypter, State, StateList
from ..exceptions import EnvKeyNotFound, InvalidKey
from .tests import CommonTestCase


class CryptoEncrypter(CommonTestCase):
    """Test the encrypter module, generating and using keys."""

    MESSAGE = "engage!"

    def test_generate_key(self):
        """Encrypter should generate a len 44 string."""
        self.assertEqual(
            len(Encrypter.generate_key()), 44, "Can't create o proper key")

    def test_encrypt_message(self):
        """Encrypter should be able to encrypt a message."""
        encrypter = Encrypter(key=Encrypter.generate_key())
        self.assertNotEqual(
            len(encrypter.encrypt(CryptoEncrypter.MESSAGE)), 0,
            "Can't encrypt a message")

    def test_decrypt_message(self):
        """Encrypter should be able to encrypt a message."""
        encrypter = Encrypter(key=Encrypter.generate_key())

        digest = encrypter.encrypt(CryptoEncrypter.MESSAGE)

        self.assertEqual(
            encrypter.decrypt(digest), CryptoEncrypter.MESSAGE,
            "Decrypted messages are not the same")


class CryptoStateList(CommonTestCase):
    """Test the state list module."""

    DEFAULT_LEVELS = [
        'unittest-debug', 'unittest-staging', 'unittest-production',
        'unittest-developer', 'unittest-microservice'
    ]

    INVALID_KEY = 'thiskeyshouldnotwork'

    def create_levels(self, levels=None):
        """Create new levels, saving the required files."""
        if levels is None:
            levels = self.DEFAULT_LEVELS
        key_list = []
        for level in levels:
            state = State.new(level)
            key_list.append(state.key)

        return key_list

    def tearDown(self):
        """Delete all unittest files."""
        env_files = glob.glob("unittest-*.env")
        for unit_test_file in env_files:
            os.remove(unit_test_file)

    def test_invalid_key(self):
        """Invalid key should through an exception."""
        with self.assertRaises(
                InvalidKey, msg="An invalid key should raise a exception."):
            StateList(key=self.INVALID_KEY)

        self.assertTrue(
            StateList().get() is None,
            msg="A None KEY should raise an exception. Are we reading the key from the environment variables?"
        )

    def test_read_state_list(self):
        """Test that we can read a state list."""
        key_list = self.create_levels(self.DEFAULT_LEVELS)

        # now make sure we can read those
        for i in range(len(key_list)):
            key = key_list[i]
            state = StateList(key=key).get()
            self.assertEqual(state.name, self.DEFAULT_LEVELS[i],
                             'Could not read an environment from a key')
