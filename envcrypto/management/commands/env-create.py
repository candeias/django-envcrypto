"""Creates a new environment stage."""
from django.core.management.base import BaseCommand

from ...crypto import State


class Command(BaseCommand):
    help = 'Create a new environment, with a .env file and a new KEY'

    def add_arguments(self, parser):
        parser.add_argument('environment_name', type=str)

    def handle(self, *args, environment_name=None, **options):
        """Create a new environment file with the name and a new KEY."""
        print("Creating a new environment file", environment_name)
        state = State.new(environment_name)

        print()
        print(
            "WARNING - Make sure you save the following key, as you will not be able to recover it."
        )
        print(environment_name, '=', state.key.decode())
        print()
        print("You can add our key to your local environment using:")
        print("export KEY='{}'".format(state.key.decode()))
