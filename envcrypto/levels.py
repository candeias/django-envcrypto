"""LevelConfig to describe levels."""
import glob
import json
import os
from binascii import a2b_base64, b2a_base64
from enum import Enum

from cryptography.fernet import Fernet

# from socket import gethostbyname, gethostname


class NoEnvKeyFound(Exception):
    """An error in configuration."""
    pass


class NoEnvFileFound(Exception):
    pass


class NoVarFound(Exception):
    pass


class Encrypter(object):

    @classmethod
    def generate_key(cls):
        """Generate a random key."""
        return Fernet.generate_key()

    def __init__(self, key=None):
        self.fernet = Fernet(key)

    def encrypt(self, message):
        ciphertext = self.fernet.encrypt(message.encode("utf-8"))
        return b2a_base64(ciphertext).decode("utf-8").strip('\n')

    def decrypt(self, digest):
        ciphertext = a2b_base64(digest.encode("utf-8"))
        return self.fernet.decrypt(ciphertext).decode("utf-8")


class StateList(object):
    """Read a list of states."""

    def __init__(self, *args, key=None, **kwargs):
        """Read the list of states."""
        self.key = key
        self.encrypter = Encrypter(key=key)
        self.states = []
        self.active_state = None

        self.read_list()

    def read_list(self):
        """Read the list of files."""
        env_files = glob.glob('*.env')
        for i in range(len(env_files)):
            env_file = env_files[i]
            if self.process_env_file(env_file):
                self.active_state = i

    def process_env_file(self, filepath=None):
        """Process the filepath."""
        env_object = json.loads(open(filepath).read())
        self.states.append(env_object)

        # try to check if we can read this enviroment
        try:
            result = self.encrypter.decrypt(env_object['signed_name'])
        except:
            return False

        return result == env_object['name']

    def add_active(self, name, value):
        """Add the name value to the state."""
        self.states[self.active_state][name] = self.encrypter.encrypt(value)

    def remove_active(self, name):
        """Add the name value to the state."""
        del self.states[self.active_state][name]

    def save_active(self):
        """Save the active state."""
        with open('{}.env'.format(self.states[self.active_state]['name']), 'w') as f:
            f.write(json.dumps(
                self.states[self.active_state], indent=4, sort_keys=True))

    def get_names_from_active(self):
        """Return the names from the active."""
        result = list(self.states[self.active_state].keys())
        result.remove('name')
        result.remove('signed_name')

        return result

    def get_from_active(self, name):
        """Return a value from the active state."""
        if name not in self.states[self.active_state]:
            raise NoVarFound(
                "Variable {} not defined on enviroment {}.".format(name, self.name))

        return self.encrypter.decrypt(self.states[self.active_state][name])

    @property
    def name(self):
        """Return the current state."""
        return self.states[self.active_state]['name']


class LevelConfig(object):
    """Configuration for the several run levels."""

    class RunLevel(Enum):
        """A run level based on the enviroment variables."""

        DEBUG = 'debug'
        STAGING = 'staging'
        PRODUCTION = 'production'

    def __init__(self):
        """Set the level using the enviroment variable."""
        self.fernet = Fernet(self.read_env('KEY'))

        # figure out the run level, using the key
        # self.find_runlevel()

    def find_runlevel(self):
        """Find the RunLevel from the encrypted files."""
        # get a list of the .env files on the root
        env_files = glob.glob('../*.env')

        if len(env_files) == 0:
            raise NoEnvFileFound(
                "We could not find any enviroment files (.env) on the django root folder.")
        print(env_files)
        print(me)

        self.run_level = LevelConfig.RunLevel(self.read_env('ENV'))

        if self.run_level is LevelConfig.RunLevel.DEBUG:
            self.__class__ = DebugConfig
        if self.run_level is LevelConfig.RunLevel.STAGING:
            self.__class__ = StagingConfig
        if self.run_level is LevelConfig.RunLevel.PRODUCTION:
            self.__class__ = ProductionConfig

    # def decrypt(self, digest):
    #     ciphertext = a2b_base64(digest.encode("utf-8"))
    #     return self.fernet.decrypt(ciphertext).decode("utf-8")
    #
    # def debug(self):
    #     """Return the DEBUG mode."""
    #     return True
    #
    # def secret_key(self):
    #     """Return the secret key."""
    #     return self.read('DJANGO_SECRET')
    #
    def read_env(self, name):
        """Read a variable name from the enviroment."""
        result = os.environ.get(name, None)
        if result is None:
            raise NoEnvKeyFound(
                "The {} variable is not setup in the enviroment".format(name))
        return result
    #
    # def read(self, name):
    #     """Read a variable name from the enviroment."""
    #     attribute = getattr(self, name, None)
    #
    #     if attribute is None:
    #         raise NoEnvKeyFound(
    #             "The {} variable is not defined".format(name))
    #
    #     try:
    #         result = self.decrypt(attribute)
    #     except Exception:
    #         raise NoEnvKeyFound(
    #             "The {} variable cannot be decrypted".format(name))
    #
    #     return result
    #
    # def allowed_hosts(self):
    #     """Return the allowed hosts."""
    #     return ['127.0.0.1', 'localhost', '10.0.2.2']
    #
    # def auth_user_model(self):
    #     """Return the auth user model."""
    #     return 'user.User'
    #
    # def installed_apps(self):
    #     """Return the installed apps."""
    #     return [
    #         'django.contrib.admin',
    #         'django.contrib.auth',
    #         'django.contrib.contenttypes',
    #         'django.contrib.sessions',
    #         'django.contrib.messages',
    #         'django.contrib.staticfiles',
    #         'rest_framework',
    #         'corsheaders',
    #         'user',
    #         'common',
    #         'saltedge',
    #         'bank',
    #         'report',
    #         'util',
    #         'tax',
    #         'yodlee'
    #     ]
    #
    # def middleware(self):
    #     """Return the middleware."""
    #     return [
    #         'corsheaders.middleware.CorsMiddleware',
    #         'django.middleware.security.SecurityMiddleware',
    #         'django.contrib.sessions.middleware.SessionMiddleware',
    #         'django.middleware.common.CommonMiddleware',
    #         'django.middleware.csrf.CsrfViewMiddleware',
    #         'django.contrib.auth.middleware.AuthenticationMiddleware',
    #         'django.contrib.messages.middleware.MessageMiddleware',
    #         'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #     ]
    #
    # def email_backend(self):
    #     """Return the email backend."""
    #     # return "django.core.mail.backends.console.EmailBackend"
    #     return "django_ses.SESBackend"
    #
    # def root_urlconf(self):
    #     """Return the root urlconf."""
    #     return 'banksy.urls'
    #
    # def templates(self):
    #     """Return the templates."""
    #     return [
    #         {
    #             'BACKEND': 'django.template.backends.django.DjangoTemplates',
    #             'DIRS': [],
    #             'APP_DIRS': True,
    #             'OPTIONS': {
    #                 'context_processors': [
    #                     'django.template.context_processors.debug',
    #                     'django.template.context_processors.request',
    #                     'django.contrib.auth.context_processors.auth',
    #                     'django.contrib.messages.context_processors.messages',
    #                 ],
    #             },
    #         },
    #     ]
    #
    # def wsgi_application(self):
    #     """Return the wsgi_application."""
    #     return 'banksy.wsgi.application'
    #
    # def databases(self):
    #     """Return the databases."""
    #     return {
    #         'default': {
    #             'ENGINE': 'django.db.backends.postgresql',
    #             'NAME': self.read('DB_NAME'),
    #             'USER': self.read('DB_USER'),
    #             'PASSWORD': self.read('DB_PASSWORD'),
    #             'HOST': self.read('DB_HOST'),
    #             'PORT': self.read('DB_PORT'),
    #         }
    #     }
    #
    # def auth_pass_validators(self):
    #     """Return auth pass validators."""
    #     return [
    #         {
    #             'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    #         },
    #         {
    #             'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    #             'OPTIONS': {
    #                 'min_length': 6
    #             }
    #         },
    #         {
    #             'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    #         }
    #     ]
    #
    # def rest_framework(self):
    #     """Return the configuration for the rest framework."""
    #     return {
    #         # Use Django's standard `django.contrib.auth` permissions,
    #         # or allow read-only access for unauthenticated users.
    #         'DEFAULT_PERMISSION_CLASSES': [
    #             'rest_framework.permissions.IsAuthenticated',
    #         ],
    #         'DEFAULT_AUTHENTICATION_CLASSES': (
    #             'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    #         ),
    #     }
    #
    # def jwt_auth(self, days=30):
    #     """Return the jwt auth."""
    #     return {
    #         'JWT_ALGORITHM': 'HS256',
    #         'JWT_VERIFY': True,
    #         'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    #         'JWT_SECRET_KEY': self.read('JWT_SECRET_KEY'),
    #         'JWT_EXPIRATION_DELTA':  timedelta(days=days),
    #         # 'JWT_RESPONSE_PAYLOAD_HANDLER': 'user.views.jwt_response_payload_handler'
    #     }
    #
    # def cors_origin_whitelist(self):
    #     """Set the cors whitelist."""
    #     return ('localhost:3000', '127.0.0.1:3000')
    #
    # def mailgun_api_url(self):
    #     """Return the mailgun api url."""
    #     return self.read("MAILGUN_API_URL")
    #
    # def mailgun_api_key(self):
    #     """Return the mailgun api url."""
    #     return self.read("MAILGUN_API_KEY")
    #
    # def root_url(self):
    #     """Return the root url."""
    #     return "http://localhost:3000"
    #
    # def api_url(self):
    #     """Return the root url."""
    #     return "https://api-staging.banksyme.com"
    #
    # def s3_data_bucket(self):
    #     """Return the data bucket."""
    #     return self.read("S3_DATA_BUCKET")
    #
    # def aws_access_key_id(self):
    #     """Return the data bucket."""
    #     return self.read("AWS_ACCESS_KEY_ID")
    #
    # def aws_secret_access_key(self):
    #     """Return the data bucket."""
    #     return self.read("AWS_SECRET_ACCESS_KEY")
    #
    # def saltedge_client_id(self):
    #     """Return the saltedge client id."""
    #     return self.read("SALTEDGE_CLIENT_ID")
    #
    # def saltedge_service_secret(self):
    #     """Return the saltedge client id."""
    #     return self.read("SALTEDGE_SERVICE_SECRET")
    #
    # def saltedge_private_key(self):
    #     """Return the saltedge private key."""
    #     return self.read("SALTEDGE_PRIVATE_KEY")
    #
    # def onesignal_appid(self):
    #     """Return the saltedge private key."""
    #     return self.read("ONESIGNAL_APPID")
    #
    # def onesignal_key(self):
    #     """Return the saltedge private key."""
    #     return self.read("ONESIGNAL_KEY")
    #
    # def yodlee_login(self):
    #     """Return the yodlee email."""
    #     return self.read("YODLEE_LOGIN")
    #
    # def yodlee_password(self):
    #     """Return the yodlee password."""
    #     return self.read("YODLEE_PASSWORD")
    #
    # def yodlee_url(self):
    #     """Return the yodlee url."""
    #     return self.read("YODLEE_URL")
    #
    # def yodlee_cobrand_id(self):
    #     """Return the yodlee cobrand_id."""
    #     return self.read("YODLEE_COBRAND_ID")
    #
    # def __str__(self):
    #     return "LevelConfig: {}".format(self.run_level)
