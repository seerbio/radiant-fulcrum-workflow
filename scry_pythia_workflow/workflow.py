from datetime import date as _date
from importlib.resources import files as _resource_files
import logging as _logging
from typing import (
    Any as _Any,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Tuple as _Tuple,
    Union as _Union,
)

from dotdict import dotdict as _dotdict
from pathlib import Path as _Path
from pyspark.sql import (
    SparkSession as _SparkSession,
)
import toml as _toml

from wheely.mammoth import (
    PsmDataset as _PsmDataset,
)
from wheely.mammoth.proteins import (
    ProteinDataset as _ProteinDataset,
)

from scry.workflow import (
    mbr_workflow as _mbr_workflow,
    v1 as _v1_workflow,
)

_logger = _logging.getLogger(__name__)


def pythia(
    library: str,
    fasta: str,
    mzml: _Union[str, _Iterable[str]],
    fdr_thresh: _Optional[float] = 0.01,
    config: _Optional[str] = None,
    mbr: _Optional[bool] = False,
    threads: int = 0,
    results_dir: _Optional[str] = None,
    spark: _Optional[_SparkSession] = None,
    **kwargs,
) -> _Tuple[_PsmDataset, _ProteinDataset]:
    """
    Workflow for running Pythia within Scry.

    To use, call ``scry.scry(workflow="pythia")`` or run ``scry`` using the following TOML:

    .. code:: toml

        workflow = "pythia"

    Parameters
    ----------

    library : str
        URI of a predicted, spectrum, or chromatogram library.
    fasta : str
        URI of a FASTA sequence database.
    mzml : str|Iterable[str]
        URI or list of URIs of mzML files to search.
    fdr_thresh : float, optional
        FDR threshold used for filtering PSMs, Precursors, and PGs. Default: 0.01.
    config : str, optional
        URI of a Pythia configuration file (TOML format). If ``None``, default
        configuration will be used.
    mbr : bool, optional
        Whether to run match-between-runs (MBR) or single-pass "library-free" workflow.
    threads : int, optional
        Number of threads to use when running Pythia. Default: 0 (auto-detect).
    results_dir : str, optional
        Directory to write intermediate and final results to. If ``None``, a folder will be
        created in the current working directory.
    spark : SparkSession, optional
        A Spark session to use when creating the search result dataset. If ``None`` a session
        will be created with default configuration.
    kwargs :
        Any additional keyword arguments to pass to the underlying workflow (either `v1` or `mbr`).
    """
    results_dir = _check_or_create_results_dir(results_dir)

    updated_config = _check_or_update_config(config, threads, results_dir)

    params = (_to_mbr_params if mbr else _to_libfree_params)(
        library=library,
        fasta=fasta,
        mzml=mzml,
        fdr_thresh=fdr_thresh,
        config=updated_config,
        results_dir=results_dir,
    )

    workflow = _mbr_workflow if mbr else _v1_workflow

    return workflow(**params, spark=spark, **kwargs)


def _to_mbr_params(
    library: str,
    fasta: str,
    mzml: _Union[str, _Iterable[str]],
    fdr_thresh: float,
    config: str,
    results_dir: str,
) -> _Mapping[str, _Any]:
    """
    Generate necessary parameters for running the MBR workflow.
    """
    raise NotImplementedError("TODO")


def _to_libfree_params(
    library: str,
    fasta: str,
    mzml: _Union[str, _Iterable[str]],
    fdr_thresh: float,
    config: str,
    results_dir: str,
) -> _Mapping[str, _Any]:
    """
    Generate necessary parameters for running the library-free (``v1``) workflow.
    """
    raise NotImplementedError("TODO")


def _check_or_create_results_dir(
    results_dir: _Union[str, None],
) -> str:
    """
    Check that the given results directory is valid, or create a new one if ``None`` was given.

    If the given directory is invalid or not writable, raises an error.
    """
    if results_dir is None:
        newdir = _create_results_dir()
        _logger.info("results_dir not provided; will use %s", newdir)
        return newdir

    results_path = _Path(results_dir)

    if results_path.exists() and not results_path.is_dir():
        raise ValueError(f"results_dir '{results_dir}' is not a directory.")

    results_path.mkdir(parents=True, exist_ok=True)

    return results_dir


def _create_results_dir() -> str:
    base_dir = _Path.cwd()

    today = _date.today().isoformat()

    candidate = base_dir / f"results-{today}"
    if not candidate.exists():
        candidate.mkdir()
        return str(candidate)

    index = 1
    while index < 100:
        candidate = base_dir / f"results-{today}-{index:d}"
        if not candidate.exists():
            candidate.mkdir()
            return str(candidate)
        index += 1
    raise RuntimeError(
        "Could not create a new results directory after 100 attempts."
    )


def _check_or_update_config(
    config_uri: _Union[str, None],
    threads: _Union[int, None],
    fdr: _Union[float, None],
    results_dir: str,
) -> str:
    """
    Check that the given configuration is valid and agrees with the given number of ``threads`` and FDR cutoff.

    If the configuration is ``None``, creates a default configuration in ``results_dir`` and returns its URI.

    If the configuration is unreadable or invalid, raises an error.

    If the configuration is valid but has a different number of threads than ``threads`` or different FDR than ``fdr``,
    creates a new configuration file in ``results_dir`` with the updated parameters and returns its URI.

    Otherwise, copies the configuration to ``results_dir`` and returns its URI.
    """
    if config_uri is None:
        config = _get_default_pythia_config()

        config.setdefault("General", _dotdict()).threadCount = (
            threads if threads and threads > 0 else 0
        )
        config.setdefault("FdrParams", _dotdict()).percentFdr = 100 * (
            fdr if fdr is not None else 0.01
        )

        newconfig = _Path(results_dir) / "config.pythiaConfig"
        with newconfig.open("w") as f:
            _toml.dump(config, f)

        return str(newconfig)

    raise NotImplementedError("TODO")


def _get_default_pythia_config():
    default_config = (
        _resource_files("scry_pythia_workflow")
        / "data"
        / "default.pythiaConfig"
    )

    with default_config.open("r") as f:
        config = _toml.load(f, _dotdict)

    return config
