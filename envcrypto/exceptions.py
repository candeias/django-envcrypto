"""Definition of all Exceptions."""


class NoEnvKeyFound(Exception):
    """Could not find a key in the environment or in the credentials."""

    pass


class NoEnvFileFound(Exception):
    """Could not find the required .env file."""

    pass


class NoVarFound(Exception):
    """The variable could not be found."""

    pass


class NoDeploymentLevelFound(Exception):
    """The Deployment Level could not be found."""

    pass


class NoValidKeyFound(Exception):
    """The supplied key is not a valid key."""

    pass
