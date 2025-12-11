import pytest

import click

from scry_pythia_workflow.cli import _check_config

@pytest.mark.parametrize(
    "uri",
    [
        "config.pythiaConfig",
        "/path/to/config.pythiaConfig",
        "s3://bucket/config.pythiaConfig",
    ]
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
    ]
)
def test_check_config_invalid(uri):
    """
    Check that valid config URIs pass the check.
    """
    with pytest.raises(click.BadParameter):
        _check_config(None, "config", uri)
