
"""Creates a new enviroment stage."""
import json
import random

from django.core.management.base import BaseCommand

from ...crypto import Encrypter


class Command(BaseCommand):
    help = 'Create a new enviroment, with a .env file and a new KEY'

    def add_arguments(self, parser):
        parser.add_argument('enviroment_name', type=str)
        parser.add_argument('--parent', type=str)

    def handle(self, *args, enviroment_name=None, parent=False, **options):
        """Create a new enviroment file with the name and a new KEY."""
        print("Creating a new enviroment file", enviroment_name)
        new_key = Encrypter.generate_key()
        encrypter = Encrypter(new_key)
        result = {}
        result['name'] = enviroment_name
        result['signed_name'] = encrypter.encrypt(enviroment_name)

        # set the django secret key
        secret_key = ''.join(random.SystemRandom().choice(
            'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))
        result['SECRET_KEY'] = encrypter.encrypt(secret_key)

        if parent:
            result['parent'] = parent

        with open('{}.env'.format(enviroment_name), 'w') as f:
            f.write(json.dumps(result, indent=4, sort_keys=True))

        print()
        print("WARNING - Make sure you save the following key, as you will not be able to recover it.")
        print(enviroment_name, '=', new_key.decode())
        print()
        print("You can add our key to your local enviroment using:")
        print("export KEY='{}'".format(new_key.decode()))
