"""Cryptography module implement all supported crypto."""

from binascii import a2b_base64, b2a_base64

from cryptography.fernet import Fernet


class Encrypter(object):
    """Generate symetric keys and encrypt / decrypts them."""

    @classmethod
    def generate_key(cls):
        """Generate a random key."""
        return Fernet.generate_key()

    def __init__(self, key=None):
        """Initialize a Fernet Symmetric encryption."""
        self.fernet = Fernet(key)

    def encrypt(self, message):
        """Encrypt a message."""
        ciphertext = self.fernet.encrypt(message.encode("utf-8"))
        return b2a_base64(ciphertext).decode("utf-8").strip('\n')

    def decrypt(self, digest):
        """Decrypt a digest."""
        ciphertext = a2b_base64(digest.encode("utf-8"))
        return self.fernet.decrypt(ciphertext).decode("utf-8")
