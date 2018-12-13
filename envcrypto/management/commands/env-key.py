"""Create a KEY."""
from django.core.management.base import BaseCommand

from ...crypto import Encrypter


class Command(BaseCommand):
    help = 'Outputs a new KEY.'

    def handle(self, *args, **options):
        """Create a new Key"""
        print("New KEY", Encrypter.generate_key())
