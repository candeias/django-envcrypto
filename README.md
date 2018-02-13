# Why use Django-Envcrypto

Django-Envcrypto allows you to safely store your environment variables in your code repository. Furthermore, you can have different sets of variables for multiple deployment levels. It's easy to use and comes with great command line tools.

<!-- * [Technology](#technology)
  * [Infrastructure](#infrastructure)
  * [Dependencies](#dependencies)
* [Environment setup](#setup)
  * [Setup Virtualenv](#setup-virtualenv)
  * [Install Dependencies](#install-dependencies)
  * [Setup Database](#setup-database)
  * [Setup Environment Variables](#setup-environment-variables)
* [How to run](#how-to-run)
  * [Migrations](#migrations) -->

## Installation

You can easly install django-envcrypto with pip by running:

```bash
pip install django-envcrypto
```

## Setup

After you install django-envcrypto all you need to do is to add it to your Djano INSTALLED_APPS variable on your settings.py file

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'envcrypto'
]
```

Next you can use it to create your first deploy level

```bash
./manage.py env-create debug
```

This will create a debug.env file in the root of your Django project with a new django SECRET_KEY. It also outputs the key for this deploy level. Make sure you save that key, as you will never be able to recover it.

You SHOULD commit this .env file in your code repository. It's perfectly save, has it's contents are encrypted.

At this state you can export this key to your environment, as django-envcrypto can read it from the KEY variable.

Lastly, add Django-Envcrypto variables to your django project

```python
from envcrypto import DeployLevel

# Please add a placeholder for your SECRET_KEY, as Django will raise an exception if it is not defined on the settings.py file
SECRET_KEY = None

DEPLOY = DeployLevel()
```

## Usage

### Variable Management

#### Create a Environment

```bash
./manage.py env-create envname
```

Creates a new environment file, with a new django SECRET_KEY. There is a default Deployment list, but be sure to create your own if you are creating environments other then ['debug', 'staging', 'production']. For instance:

```python
from enum import Enum
class MyCustomDeployment(Enum):

    DEBUG = 'debug'
    MULTIVERSE = 'staging'
    ENVNAME = 'envname'
```

and pass it to your DeployLevel.

```python
DEPLOY = DeployLevel(levels=MyCustomDeployment)
```

#### Add a Variable

```bash
./manage.py env-add -k ENVKEY VAR1 value1
```

Adds a variable and it value to the environment specified with ENVKEY. If you omit the -k parameter django-envcrypto will read it from your environment.

#### Delete a Variable

```bash
./manage.py env-delete -k ENVKEY VAR1
```

Deletes VAR1 from the specified environment. If you omit the -k parameter django-envcrypto will read it from your environment.

#### Show all variables

```bash
./manage.py env-show -k ENVKEY
```

Show all the variables to that environment. If you omit the -k parameter django-envcrypto will read it from your environment.

#### Transcode to another environment

```bash
./manage.py env-show -k ENVKEY -t NEWENVKEY
```

Transcodes all the current ENVKEY variables to the new NEWENVKEY. Django-envcrypto will overwrite any variable that already exists on the new NEWENVKEY (except for the internal variables like SECRET_KEY). If you omit the -k parameter django-envcrypto will read it from your environment.

### Level Management

When Django initializes, django-envproject reads the .env files and determines in with deployment level it currently is. You can read that level from your DEPLOY variable:

```python
if DEPLOY.LEVEL is Deployment.DEBUG:
    DEBUG = True
```

This allows you to configure custom commands to each of your deploy levels. You can also read that level from anywhere on your code using:

```python
from django.conf import settings
from envcrypto import Deployment # as an example, you might use your MyCustomDeployment class

if settings.DEPLOY.LEVEL in [Deployment.DEBUG, Deployment.STAGING]:
  print("Not in production!")
```

## Deployment

## Notes

### Accessing the secrets

Assuming you've just added a TWILIO_AUTH_TOKEN secret key through the steps above, it's worth noticing that in order to access the variable from anywhere within your project, all you'll have to do is:
```python
import settings
twilio_token = settings.TWILIO_AUTH_TOKEN
```

### Compatibility

Currently, Django-Envcrypto supports [python](https://www.python.org/) (3.4+) because it uses Enumerators (Enum) under the hood. We might extend the support in the future.
