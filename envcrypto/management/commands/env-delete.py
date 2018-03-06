"""Creates a new environment stage."""
from django.core.management.base import BaseCommand

from ...crypto import StateList


class Command(BaseCommand):
    help = 'Add a environment variable using a key'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('-k', '--key', type=str)

    def handle(self, *args, name=None, value=None, key=None, **options):
        """Create a new environment file with the name and a new KEY."""
        state = StateList(key=key, raise_error_on_key=True).get()
        print("Deleting variable from environment", state.name)
        state.remove(name)
        state.save()
