"""Test the crypto module."""
from ..crypto import Encrypter
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
