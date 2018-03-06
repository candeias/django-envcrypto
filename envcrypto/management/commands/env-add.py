"""Creates a new environment stage."""
from django.core.management.base import BaseCommand

from ...crypto import StateList
from ...exceptions import VariableExists


class Command(BaseCommand):
    help = 'Add a environment variable using a key'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('value', type=str)
        parser.add_argument('-k', '--key', type=str)
        parser.add_argument(
            '-f', '--force', action='store_true', default=False)

    def handle(self,
               *args,
               name=None,
               value=None,
               key=None,
               force=False,
               **options):
        """Create a new environment file with the name and a new KEY."""
        state = StateList(key=key, raise_error_on_key=True).get()
        print("Adding to variable to environment", state.name)
        try:
            state.add(name, value, force=force)
            state.save()
        except VariableExists:
            print(
                "{} variable is already defined.\nIn order to force overwriting the value use the -f parameter.".
                format(name))
