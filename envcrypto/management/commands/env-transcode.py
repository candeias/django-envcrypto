"""Transcode an environment stage to a new one, with the supplied keys."""
from django.core.management.base import BaseCommand

from ...crypto import StateList
from ...exceptions import VariableExists


class Command(BaseCommand):
    help = 'Transcode settings to another state'

    def add_arguments(self, parser):
        parser.add_argument('-k', '--key', type=str)
        parser.add_argument('-t', '--transcode-key', type=str, required=True)
        parser.add_argument(
            '-f', '--force', action='store_true', default=False)

    def handle(self,
               *args,
               key=None,
               transcode_key=None,
               force=False,
               **options):
        """Create a new environment file with the name and a new KEY."""
        old_state = StateList(key=key, raise_error_on_key=True).get()
        new_state = StateList(key=transcode_key, raise_error_on_key=True).get()

        # we iterate the list of states on the current one to the new
        for key_var, value in old_state.get():
            try:
                new_state.add(key_var, value, force=force)
            except VariableExists:
                print(
                    "{} variable is already defined.\nIn order to force overwriting the value use the -f parameter.".
                    format(key_var))

        new_state.save()
