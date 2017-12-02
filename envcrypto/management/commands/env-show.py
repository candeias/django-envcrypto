"""Creates a new enviroment stage."""
from django.core.management.base import BaseCommand

from ...crypto import StateList


class Command(BaseCommand):
    help = 'Add a enviroment variable using a key'

    def add_arguments(self, parser):
        parser.add_argument('-k', '--key', type=str)
        parser.add_argument('-n', '--name', type=str)

    def handle(self, *args, name=None, key=None, ** options):
        """Create a new enviroment file with the name and a new KEY."""
        stl = StateList(key=key)

        # we are going to either show a variable or all of the variables from the enviroment
        print("Active enviroment:", stl.name)
        list_of_names = [name]
        if name is None:
            list_of_names = stl.get_names_from_active()

        # we show all
        for name in list_of_names:
            print(name, stl.get_from_active(name))
