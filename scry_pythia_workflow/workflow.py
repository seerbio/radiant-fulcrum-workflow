from importlib.resources import files as _resource_files
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
    raise NotImplementedError("TODO")


def _check_or_update_config(
    config_uri: _Union[str, None],
    threads: _Union[int, None],
    results_dir: str,
) -> str:
    """
    Check that the given configuration is valid and agrees with the given number of ``threads``.

    If the configuration is ``None``, creates a default configuration in ``results_dir`` and returns its URI.

    If the configuration is unreadable or invalid, raises an error.

    If the configuration is valid but has a different number of threads than ``threads``, creates a
    new configuration file in ``results_dir`` with the updated number of threads and returns its URI.

    Otherwise, copies the configuration to ``results_dir`` and returns its URI.
    """
    if config_uri is None:
        default_config = _resource_files("scry_pythia_workflow") / "data" / "default.pythiaConfig"

        with default_config.open("r") as f:
            config = _toml.load(f, _dotdict)
        config.setdefault("General", _dotdict()).threadCount = threads if threads and threads > 0 else 0

        newconfig = _Path(results_dir) / "config.pythiaConfig"
        with newconfig.open("w") as f:
            _toml.dump(config, f)

        return str(newconfig)

    raise NotImplementedError("TODO")