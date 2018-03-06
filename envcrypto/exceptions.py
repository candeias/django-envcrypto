"""Definition of all Exceptions."""


class DjangoEnvcryptException(Exception):
    """Overwrite behaviour of the exceptions."""
    MESSAGE = None

    def __init__(self, *args, **kwargs):
        """Send the message defined in the class."""
        if self.MESSAGE is not None:
            super().__init__(self.MESSAGE, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)


class EnvKeyNotFound(DjangoEnvcryptException):
    """Could not find a key in the environment or in the credentials."""

    pass


class EnvFileNotFound(DjangoEnvcryptException):
    """Could not find the required .env file."""

    pass


class InvalidEnvFile(DjangoEnvcryptException):
    """Could not read the .env file."""

    pass


class FileWriteError(DjangoEnvcryptException):
    """Could not save the file"""

    pass


class VariableNotFound(DjangoEnvcryptException):
    """The variable could not be found."""

    pass


class VariableExists(DjangoEnvcryptException):
    """The variable already exists in the data. You can overwrite by passing a force option."""
    MESSAGE = "The variable you are adding already exists, you can force it to be modified."


class DeploymentIsNotAEnum(DjangoEnvcryptException):
    """The Deployment is not an Enum object."""

    pass


class DeploymentLevelNotFound(DjangoEnvcryptException):
    """The Deployment Level could not be found."""

    pass


class InvalidKey(DjangoEnvcryptException):
    """The supplied key is not a valid key."""

    pass
