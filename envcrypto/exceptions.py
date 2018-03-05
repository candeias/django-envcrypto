"""Definition of all Exceptions."""


class EnvKeyNotFound(Exception):
    """Could not find a key in the environment or in the credentials."""

    pass


class EnvFileNotFound(Exception):
    """Could not find the required .env file."""

    pass


class InvalidEnvFile(Exception):
    """Could not read the .env file."""

    pass


class FileWriteError(Exception):
    """Could not save the file"""

    pass


class VariableNotFound(Exception):
    """The variable could not be found."""

    pass


class VariableExists(Exception):
    """The variable already exists in the data. You can overwrite by passing a force option."""

    pass


class DeploymentIsNotAEnum(Exception):
    """The Deployment is not an Enum object."""

    pass


class DeploymentLevelNotFound(Exception):
    """The Deployment Level could not be found."""

    pass


class InvalidKey(Exception):
    """The supplied key is not a valid key."""

    pass
