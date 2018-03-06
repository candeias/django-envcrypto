"""Creates a new environment stage."""
from django.core.management.base import BaseCommand

from ...crypto import StateList


class Command(BaseCommand):
    help = 'Add a environment variable using a key'

    def add_arguments(self, parser):
        parser.add_argument('-k', '--key', type=str)
        parser.add_argument('-n', '--name', type=str)

    def handle(self, *args, name=None, key=None, **options):
        """Create a new environment file with the name and a new KEY."""
        state = StateList(key=key, raise_error_on_key=True).get()

        # we are going to either show a variable or all of the variables from
        # the environment
        print("Active environment:", state.name)
        for key, value in state:
            print(key, value)
