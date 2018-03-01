"""Test the crypto module."""
import glob
import os

from ..crypto import Encrypter, State, StateList
from ..exceptions import NoEnvKeyFound, NoValidKeyFound
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

    PREFIX = "unittest"

    def create_levels(self, levels=['debug', 'staging', 'production']):
        """Create new levels, saving the required files."""
        key_list = []
        for level in levels:
            state = State(level)
            state.save(prefix=self.PREFIX)

            key_list.append(state.key)

        return key_list

    def tearDown(self):
        """Delete all unittest files."""
        env_files = glob.glob("{}-*.env".format(self.PREFIX))
        for unit_test_file in env_files:
            os.remove(unit_test_file)

    def test_invalid_key(self):
        """Invalid key should through an exception."""
        with self.assertRaises(
                NoValidKeyFound, msg="A None KEY should raise an exception"):
            StateList(read_from_env=False)

        with self.assertRaises(
                NoEnvKeyFound,
                msg="We are reading the key from the environment variables, you should remove it."
        ):
            StateList(read_from_env=True)

    def test_read_state_list(self):
        """Test that we can read a state list."""
        list_of_levels = [
            'debug', 'staging', 'developer', 'production', 'microservice'
        ]
        key_list = self.create_levels(list_of_levels)

        # now make sure we can read those
        for i in range(len(key_list)):
            key = key_list[i]
            state_list = StateList(key=key)
            self.assertEqual(state_list.name, list_of_levels[i],
                             'Could not read an environment from a key')
