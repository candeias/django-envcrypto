"""Creates a new environment stage."""
from django.core.management.base import BaseCommand

from ...crypto import StateList


class Command(BaseCommand):
    help = 'Transcode settings to another state'

    def add_arguments(self, parser):
        parser.add_argument('-k', '--key', type=str)
        parser.add_argument('-t', '--transcode-key', type=str, required=True)

    def handle(self, *args, key=None, transcode_key=None, **options):
        """Create a new environment file with the name and a new KEY."""
        old_state = StateList(key=key).get()
        new_state = StateList(key=transcode_key).get()

        # we iterate the list of states on the current one to the new
        for key_var, value in old_state:
            new_state.add(key_var, value)

        new_state.save()
