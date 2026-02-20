import pytest

import click

from radiant_fulcrum_workflow.cli import _check_config


@pytest.mark.parametrize(
    "uri",
    [
        "config.radiantConfig",
        "/path/to/config.radiantConfig",
        "s3://bucket/config.radiantConfig",
    ],
)
def test_check_config_valid(uri):
    """
    Check that valid config URIs pass the check.
    """
    assert _check_config(None, "config", uri) == uri


@pytest.mark.parametrize(
    "uri",
    [
        "config.toml",
        "/path/to/config.toml",
        "s3://bucket/config.toml",
        "",
        "\n",
        "\n.\n",
    ],
)
def test_check_config_invalid(uri):
    """
    Check that valid config URIs pass the check.
    """
    with pytest.raises(click.BadParameter):
        _check_config(None, "config", uri)
