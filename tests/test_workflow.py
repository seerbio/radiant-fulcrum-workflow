import pytest
import toml

from dotdict import dotdict
from pathlib import Path

from scry_pythia_workflow.workflow import (
    _check_or_create_results_dir,
    _check_or_update_config,
    _get_default_pythia_config,
)


@pytest.fixture()
def tmp_workingdir(tmp_path, monkeypatch):
    working_dir = tmp_path / "workingdir"
    working_dir.mkdir()
    monkeypatch.chdir(working_dir)

    assert Path.cwd() == working_dir


def test_create_results_dir(tmp_workingdir):
    """
    Test creating a new results directory when ``None`` is provided
    """
    result_dir = _check_or_create_results_dir(None)

    result_path = Path(result_dir)

    assert result_path.exists()
    assert result_path.is_dir()
    assert result_path.parent == Path.cwd()

    # Try again to ensure a new directory is created
    result_dir2 = _check_or_create_results_dir(None)

    assert result_dir2 != result_dir

    result_path2 = Path(result_dir2)

    assert result_path2.exists()
    assert result_path2.is_dir()
    assert result_path2.parent == Path.cwd()

    # ...and one more time to check the counting logic
    result_dir3 = _check_or_create_results_dir(None)

    assert result_dir3 not in {result_dir, result_dir2}

    result_path3 = Path(result_dir3)

    assert result_path3.exists()
    assert result_path3.is_dir()
    assert result_path3.parent == Path.cwd()


@pytest.fixture()
def valid_results_dir(tmp_path) -> str:
    results_dir = tmp_path / "results"
    return str(results_dir)


@pytest.fixture()
def extant_results_dir(valid_results_dir) -> str:
    results_dir = Path(valid_results_dir)
    results_dir.mkdir()
    return str(results_dir)


@pytest.mark.parametrize(
    "dir_fixture", ["valid_results_dir", "extant_results_dir"]
)
def test_check_results_dir(request, dir_fixture):
    """
    Test checking a valid results directory
    """
    input = request.getfixturevalue(dir_fixture)
    results_dir = _check_or_create_results_dir(input)

    assert results_dir == input
    assert Path(results_dir).is_dir()
    assert Path(results_dir).exists()


@pytest.mark.parametrize(
    "threads",
    [
        None,
        -1,
        0,
        8,
    ],
)
@pytest.mark.parametrize(
    "fdr",
    [
        None,
        0.01,
        0.05,
    ],
)
def test_default_config(tmp_path, threads, fdr):
    """
    Test that providing None as config_uri creates a default config in results_dir
    """
    results_dir = tmp_path / "results"
    results_dir.mkdir()

    result = _check_or_update_config(None, threads, fdr, str(results_dir))

    assert result is not None

    config_path = Path(result)

    assert config_path.exists()
    assert config_path == (results_dir / "config.pythiaConfig")

    with config_path.open("r") as f:
        config = toml.load(f, dotdict)

    assert config.General.threadCount == (
        threads if threads and threads > 0 else 0
    )
    assert config.FdrParams.percentFDR == 100 * (
        fdr if fdr is not None else 0.01
    )


@pytest.fixture()
def custom_config(tmp_path) -> str:
    default_config = _get_default_pythia_config()

    p = tmp_path / "config.pythiaConfig"

    with p.open("w") as f:
        toml.dump(default_config, f)

    return str(p)


@pytest.mark.parametrize(
    "threads",
    [
        None,
        -1,
        0,
        8,
    ],
)
@pytest.mark.parametrize(
    "fdr",
    [
        None,
        0.01,
        0.05,
    ],
)
def test_custom_config(tmp_path, custom_config, threads, fdr):
    """
    Test that providing None as config_uri creates a default config in results_dir
    """
    results_dir = tmp_path / "results"
    results_dir.mkdir()

    result = _check_or_update_config(
        custom_config, threads, fdr, str(results_dir)
    )

    assert result is not None

    config_path = Path(result)

    assert config_path.exists()
    assert config_path == (results_dir / "config.pythiaConfig")

    with config_path.open("r") as f:
        config = toml.load(f, dotdict)

    assert config.General.threadCount == (
        threads if threads and threads > 0 else 0
    )
    assert config.FdrParams.percentFDR == 100 * (
        fdr if fdr is not None else 0.01
    )
