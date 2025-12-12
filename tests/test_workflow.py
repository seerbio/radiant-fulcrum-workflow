import pytest
import toml

from dotdict import dotdict
from pathlib import Path

from scry_pythia_workflow.workflow import _check_or_update_config


@pytest.mark.parametrize(
    "config_uri",
    [
        None,
    ]
)
@pytest.mark.parametrize(
    "threads",
    [
        None,
        -1,
        0,
        8,
    ]
)
def test_default_config(tmp_path, config_uri, threads):
    """
    Test that providing None as config_uri creates a default config in results_dir
    """
    results_dir = tmp_path / "results"
    results_dir.mkdir()

    result = _check_or_update_config(config_uri, threads, str(results_dir))

    assert result is not None

    config_path = Path(result)

    assert config_path.exists()

    if not config_uri:
        assert config_path == (results_dir / "config.pythiaConfig")

    with config_path.open("r") as f:
        config = toml.load(f, dotdict)

    assert config.General.threadCount == (threads if threads and threads > 0 else 0)