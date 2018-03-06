"""Test the crypto module."""
import glob
import os

from ..crypto import Encrypter, State, StateList
from ..exceptions import EnvKeyNotFound, InvalidKey, VariableExists
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


class StateCreationTestCase(CommonTestCase):
    """Create and destroy unittests."""

    DEFAULT_LEVELS = [
        'unittest-debug', 'unittest-staging', 'unittest-production',
        'unittest-developer', 'unittest-microservice'
    ]

    VARKEY = "UNITTEST"
    VARVALUE = "value"

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

        super().tearDown()


class CryptoState(StateCreationTestCase):
    """Test operation of the State object."""

    def create_and_read_level(self):
        """Create and reads back a level."""
        key = self.create_levels(levels=[self.DEFAULT_LEVELS[0]])[0]
        return self.read_level(key)

    def read_level(self, key):
        """Read a level using a key."""
        return StateList(key=key).get()

    def test_create_new(self):
        """Create a new State."""
        state = self.create_and_read_level()

        self.assertEqual(state.name, self.DEFAULT_LEVELS[0],
                         "Env file created with a different name.")
        self.assertEqual(len(state.django_secret), State.DJANGO_SECRET_SIZE)

    def test_add_variable(self):
        """Add a variable."""
        # Add variable the first time
        state = self.create_and_read_level()
        state.add(self.VARKEY, self.VARVALUE)
        state.save()

        # check the variable is there
        new_state = StateList(key=state.key).get()
        self.assertIn(self.VARKEY, new_state.data)
        self.assertEqual(new_state.data[self.VARKEY], self.VARVALUE)

        # try to add the same variable and receive the exception
        with self.assertRaises(
                VariableExists,
                msg="Editing a variable without force was allowed"):
            new_state.add(self.VARKEY, self.VARVALUE)

        # now add the variable with the force parameter and check again if the
        # variable changed
        new_var = "{}-{}".format(self.VARVALUE, self.VARVALUE)

        new_state.add(self.VARKEY, new_var, force=True)
        new_state.save()

        # check the variable is there
        last_state = StateList(key=state.key).get()
        self.assertIn(self.VARKEY, last_state.data)
        self.assertEqual(last_state.data[self.VARKEY], new_var)

    def test_remove_variable(self):
        """Remove a variable from the State."""
        state = self.create_and_read_level()
        state.add(self.VARKEY, self.VARVALUE)
        state.save()

        new_state = StateList(key=state.key).get()
        new_state.remove(self.VARKEY)
        new_state.save()

        final_state = StateList(key=state.key).get()
        self.assertNotIn(self.VARKEY, final_state.data)


class CryptoStateList(StateCreationTestCase):
    """Test the state list module."""

    INVALID_KEY = 'thiskeyshouldnotwork'

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

    def test_transcode_variables(self):
        """Transcode an environment."""
        key_list = self.create_levels(self.DEFAULT_LEVELS[:2])

        # we read both environments
        state_a = StateList(key=key_list[0]).get()
        state_b = StateList(key=key_list[1]).get()

        # add a variable to state a
        state_a.add(self.VARKEY, self.VARVALUE)
        state_a.save()

        # we read state a again
        state_a = StateList(key=key_list[0]).get()

        for key, value in state_a:
            state_b.add(key, value)
        state_b.save()

        # read state b again
        state_b = StateList(key=key_list[1]).get()

        # check that they both have the same variables
        for key, value in state_a.get():
            if key == State.SECRET_KEY:
                # make sure the secret keys are different
                self.assertNotEqual(
                    value, state_b.django_secret,
                    "Django Secret Keys was copied to the transcoded envinroment."
                )

            else:
                self.assertIn(key, state_b.data)
                self.assertEqual(value, state_b.data[key])
