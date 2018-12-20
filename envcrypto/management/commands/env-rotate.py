"""Rotate the key on an enviroment."""
from django.core.management.base import BaseCommand

from ...crypto import Encrypter
from ...exceptions import VariableExists
from ...state import StateList


class Command(BaseCommand):
    help = 'Rotate the key on the envinroment'

    def add_arguments(self, parser):
        parser.add_argument('-k', '--key', type=str)

    def handle(self,
               *args,
               key=None,
               transcode_key=None,
               force=False,
               **options):
        """Create a new environment file with the name and a new KEY."""
        state = StateList(key=key, raise_error_on_key=True).get()

        # create new key
        new_key = Encrypter.generate_key()
        print("New KEY", new_key)
        state.set_key(new_key)
        state.save()
