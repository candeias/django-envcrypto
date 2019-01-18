"""Test the crypto module."""
from ..exceptions import DeploymentIsNotAEnum, DeploymentIsNotAClass
from ..levels import DeployLevel, Deployment
from .tests import CommonTestCase
from enum import Enum


class RealDeploymentEnvironments(Enum):
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'


class LevelsDeployLevel(CommonTestCase):
    """Test the DeployLevel module."""

    NON_ENUM = "engage!"

    def test_levels_empty(self):
        """Deploylevel should give back the default deploy."""
        deploy_level = DeployLevel()

        self.assertEqual(deploy_level.levels, Deployment,
                         "Deployment is not the default")

    def test_levels_non_enum(self):
        """Deployment should be a enum."""
        with self.assertRaises(
                DeploymentIsNotAClass,
                msg="Please pass a class as the run levels"):
            DeployLevel(levels=self.NON_ENUM)

    def test_levels_is_valid_enum_should_not_raise(self):
        """DeployLevel should give back the specified enum."""
        deploy_level = DeployLevel(levels=RealDeploymentEnvironments)
        self.assertEqual(deploy_level.levels, RealDeploymentEnvironments)
        self.assertEqual(deploy_level.levels.DEVELOPMENT.value, 'development')
        self.assertEqual(deploy_level.levels.STAGING.value, 'staging')
        self.assertEqual(deploy_level.levels.PRODUCTION.value, 'production')

