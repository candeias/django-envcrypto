"""Creates a new enviroment stage."""
from django.core.management.base import BaseCommand

from ...crypto import StateList


class Command(BaseCommand):
    help = 'Transcode settings to another state'

    def add_arguments(self, parser):
        parser.add_argument('-k', '--key', type=str)
        parser.add_argument('-t', '--transcode-key', type=str, required=True)

    def handle(self, *args, name=None,  value=None, key=None, transcode_key=None, ** options):
        """Create a new enviroment file with the name and a new KEY."""
        stl = StateList(key=key)
        new_state = StateList(key=transcode_key)

        # we iterate the list of states on the current one to the new
        for name in stl.get_names_from_active():
            new_state.add_active(name, stl.get_from_active(name))

        new_state.save_active()
