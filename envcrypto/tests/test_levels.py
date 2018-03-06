"""Test the crypto module."""
from ..exceptions import DeploymentIsNotAEnum
from ..levels import DeployLevel, Deployment
from .tests import CommonTestCase


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
                DeploymentIsNotAEnum,
                msg="Non Enum doesn't raise an exception"):
            DeployLevel(levels=self.NON_ENUM)
