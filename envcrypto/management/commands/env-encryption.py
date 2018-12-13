"""E."""
from django.core.management.base import BaseCommand

from ...crypto import Encrypter
from ...exceptions import VariableExists
from ...state import read_env


class Command(BaseCommand):
    help = 'Encrypt or decrypt a value using a key.'

    def add_arguments(self, parser):
        parser.add_argument('value', type=str)
        parser.add_argument('-k', '--key', type=str)
        parser.add_argument(
            '-e', '--encrypt', action='store_true', default=False)
        parser.add_argument(
            '-d', '--decrypt', action='store_true', default=False)

    def handle(self,
               *args,
               value=None,
               key=None,
               encrypt=False,
               decrypt=False,
               **options):
        """Encrypt or Decrypts a value from the command line using the supplied key."""
        if key is None:
            key = read_env("KEY")
        encrypter = Encrypter(key=key)

        if encrypt:
            # encrypt the digest
            print("Encrypting message:", value)
            print("Digest")
            print(encrypter.encrypt(value))

        if decrypt:
            print("Decrypting digest:", value)
            print("Message")
            print(encrypter.decrypt(value))
