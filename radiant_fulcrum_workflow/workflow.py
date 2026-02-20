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

from copy import deepcopy as _deepcopy
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

from fulcrum.output import get_backend as _get_output_backend

from fulcrum.workflow.registry import get_workflow as _get_workflow

_logger = _logging.getLogger(__name__)


def radiant(
    library: str,
    fasta: str,
    mzml: _Union[str, _Iterable[str]],
    fdr_thresh: _Optional[float] = None,
    config: _Optional[str] = None,
    mbr: _Optional[bool] = False,
    threads: int = 0,
    results_dir: _Optional[str] = None,
    spark: _Optional[_SparkSession] = None,
    overrides: _Optional[_Mapping[str, _Any]] = None,
    **kwargs,
) -> _Tuple[_PsmDataset, _ProteinDataset]:
    """
    Workflow for running Radiant DIA within the Fulcrum Pipeline.

    To use, call ``fulcrum.fulcrum(workflow="radiant")`` or run ``fulcrum`` using the following TOML:

    .. code:: toml

        workflow = "radiant"

    Parameters
    ----------

    library : str
        URI of a predicted, spectrum, or chromatogram library.
    fasta : str
        URI of a FASTA sequence database.
    mzml : str|Iterable[str]
        URI or list of URIs of mzML files to search.
    fdr_thresh : float, optional
        FDR threshold between (0 and 1) used for filtering PSMs, Precursors, and PGs.
        Note: if unspecified the default value (0.01) will be used for all workflow steps, but output will
        be written unfiltered.
    config : str, optional
        URI of a Radiant DIA configuration file (TOML format). If ``None``, default
        configuration will be used.
    mbr : bool, optional
        Whether to run match-between-runs (MBR) or single-pass "library-free" workflow.
    threads : int, optional
        Number of threads to use when running Radaint DIA. Default: 0 (auto-detect).
    results_dir : str, optional
        Directory to write intermediate and final results to. If ``None``, a folder will be
        created in the current working directory.
    spark : SparkSession, optional
        A Spark session to use when creating the search result dataset. If ``None`` a session
        will be created with default configuration.
    overrides : dict, optional
        Override arguments to pass to the underlying workflow (either `v1` or `mbr`).
        Parameters passed in this way will override any defaults or those passed via other arguments.
        Using this argument permits overriding any parameters that can not be set via ``kwargs`` due to
        shadowing by other arguments to this function.
    kwargs :
        Any additional keyword arguments to pass to the underlying workflow (either `v1` or `mbr`).
        Parameters passed in this way will override any defaults or those passed via other arguments (other
        than ``overrides``).
    """
    results_dir = _check_or_create_results_dir(results_dir)

    updated_config = _check_or_update_config(
        config, threads, fdr_thresh, results_dir
    )

    params = (_to_mbr_params if mbr else _to_libfree_params)(
        library=library,
        fasta=fasta,
        mzml=mzml,
        fdr_thresh=fdr_thresh,
        config=updated_config,
        results_dir=results_dir,
    )

    if overrides:
        overrides = _merge_recursive(kwargs, overrides, _deepcopy_dotdict)
    else:
        overrides = kwargs

    params = _configure_output(
        params, fdr_thresh, results_dir, overrides=overrides
    )

    params = _merge_recursive(params, overrides, _deepcopy_dotdict)

    _logger.debug(
        "Generated Fulcrum workflow parameters:\n%s", _toml.dumps(params)
    )

    workflow = _get_workflow(params.pop("workflow"))

    return workflow(**params, spark=spark)


def _to_mbr_params(
    library: str,
    fasta: str,
    mzml: _Union[str, _Iterable[str]],
    fdr_thresh: _Union[float, None],
    config: str,
    results_dir: str,
) -> _Mapping[str, _Any]:
    """
    Generate necessary parameters for running the MBR workflow.
    """
    params = _read_default_toml("default.mbr.toml")

    if isinstance(mzml, str):
        mzml = [mzml]
    else:
        mzml = list(mzml)

    results_path = _Path(results_dir)

    params.library.search.library = library
    params.library.search.fasta = fasta
    params.library.search.location = mzml
    params.library.search.config = config
    params.library.search.output_location = str(
        results_path / "radiant-firstpass-results"
    )
    params.library.output.location = str(
        results_path / "fulcrum-mbr-library.tsv"
    )
    if fdr_thresh is not None:
        params.library.output.qval_thresh = fdr_thresh

    params.search.fasta = fasta
    params.search.location = mzml
    params.search.config = config
    params.search.output_location = str(results_path / "radiant-results")

    params.proffer.fasta_uri = fasta

    if fdr_thresh is not None:
        params.proffer.qvalue_threshold = fdr_thresh
        params.protein_rollup.qvalue_threshold = fdr_thresh

    return params


def _to_libfree_params(
    library: str,
    fasta: str,
    mzml: _Union[str, _Iterable[str]],
    fdr_thresh: _Union[float, None],
    config: str,
    results_dir: str,
) -> _Mapping[str, _Any]:
    """
    Generate necessary parameters for running the library-free (``v1``) workflow.
    """
    params = _read_default_toml("default.v1.toml")

    if isinstance(mzml, str):
        mzml = [mzml]
    else:
        mzml = list(mzml)

    params.search.library = library
    params.search.fasta = fasta
    params.search.location = mzml
    params.search.config = config
    params.search.output_location = str(_Path(results_dir) / "radiant-results")

    params.proffer.fasta_uri = fasta
    if fdr_thresh is not None:
        params.proffer.qvalue_threshold = fdr_thresh
        params.protein_rollup.qvalue_threshold = fdr_thresh

    return params


def _configure_output(
    params: _Mapping[str, _Any],
    fdr_thresh,
    results_dir,
    overrides: _Mapping[str, _Any] = None,
):
    params = _deepcopy_dotdict(params)
    if overrides is None:
        overrides = _deepcopy_dotdict()

    params.setdefault("output", _deepcopy_dotdict())

    if fdr_thresh is not None:
        params.output.qval_thresh = fdr_thresh

    output_backend = overrides.get("output", {}).get("backend", None)

    if output_backend is None:
        output_backend = params.output.get("backend", None)

    if output_backend is None:
        raise ValueError("No configured output backend!")

    params.output.backend = output_backend

    combined_backends = {"combined"}
    separate_backends = {"write_csv", "write_parquet"}
    lib_backends = {"write_library"}

    def is_backend(backends):
        if output_backend in backends:
            return True

        for backend in combined_backends:
            fn = _get_output_backend(backend)
            if fn == output_backend:
                return True

        return False

    if is_backend(combined_backends):
        # We will write only a single combined output dataset; set a single location
        params.output.location = str(_Path(results_dir) / "fulcrum-results")
    elif is_backend(separate_backends):
        # We will write separate outputs for PSMs and proteins
        params.peptide_output.location = str(
            _Path(results_dir) / "fulcrum-peptides"
        )
        params.protein_output.location = str(
            _Path(results_dir) / "fulcrum-proteins"
        )
    elif is_backend(lib_backends):
        # This is not recommended; log a warning and configure a location (unless overridden)
        if "location" in overrides.get("output", {}):
            _logger.warning(
                "Output backend `write_library` is not recommended for `radiant` workflow! "
                "Proceeding with user-specified output location."
            )
        else:
            _logger.warning(
                "Output backend `write_library` is not recommended for `radiant` workflow! "
                "Proceeding with default output location."
            )
            params.output.location = str(
                _Path(results_dir) / "fulcrum-output-library.tsv"
            )
    else:
        # Unknown backend; log a warning and set a single location
        if "location" in overrides.get("output", {}):
            _logger.warning(
                "Unknown output backend '%s'; proceeding with user-specified output location.",
                output_backend,
            )
        else:
            _logger.warning(
                "Unknown output backend '%s'; setting a default output location",
                output_backend,
            )
            params.output.location = str(
                _Path(results_dir) / "fulcrum-results"
            )

    return params


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


class _deepcopy_dotdict(_dotdict):
    """
    Subclass of ``dotdict`` that supports deep copying.
    """

    def __deepcopy__(self, memo=None):
        return _deepcopy_dotdict(_deepcopy(dict(self), memo=memo))


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

    Parameters
    ----------
    config_uri : str|None
        URI of a Radiant DIA configuration file (TOML format). If ``None``, a default configuration will be used.
    threads : int|None
        Number of threads to use when running Radiant DIA. If ``None``, no change will be made to the configuration.
    fdr : float|None
        FDR threshold (between 0 and 1) used for filtering PSMs, Precursors, and PGs. If ``None``, no change will be
        made to the configuration.
    results_dir : str
        Directory to write the updated configuration file to.
    """
    if config_uri is None:
        config = _get_default_radiant_config()
    else:
        config_path = _Path(config_uri)
        if not config_path.exists():
            raise ValueError(f"config '{config_uri}' does not exist.")

        with config_path.open("r") as f:
            config = _toml.load(f, _deepcopy_dotdict)

    _set_config_fields(config, threads, fdr)

    # TODO: what if newconfig is the same file as config_path? We should check for this and avoid writing if so -- raise?
    newconfig = _Path(results_dir) / "config.radiantConfig"
    with newconfig.open("w") as f:
        _toml.dump(config, f)

    return str(newconfig)


def _set_config_fields(config, threads, fdr):
    if threads and threads > 0:
        config.setdefault("General", _deepcopy_dotdict()).threadCount = threads
    if fdr is not None:
        config.setdefault("FdrParams", _deepcopy_dotdict()).percentFDR = (
            100 * fdr
        )


def _get_default_radiant_config():
    return _read_default_toml("default.radiantConfig")


def _read_default_toml(fname) -> _deepcopy_dotdict:
    loc = _resource_files("radiant_fulcrum_workflow") / "data" / fname

    with loc.open("r") as f:
        params = _toml.load(f, _deepcopy_dotdict)

    return params


def _merge_recursive(a, b, _dict=dict):
    """
    Merge two dictionaries recursively, preferring values from ``b`` when keys overlap.
    """
    res = _dict()

    for k, v in a.items():
        ov = b.get(k, None)

        if ov is not None:
            if isinstance(v, dict) or isinstance(v, _dict):
                assert isinstance(
                    ov, dict
                ), f"Value for `{k}` is not a dict! `{ov}`"

                res[k] = _merge_recursive(v, ov, _dict=_dict)
            elif isinstance(ov, dict) or isinstance(ov, _dict):
                res[k] = _dict(ov)
            else:
                res[k] = ov
        elif isinstance(v, dict) or isinstance(v, _dict):
            res[k] = _dict(v)
        else:
            res[k] = v

    for k, v in b.items():
        if k in a:
            continue

        if isinstance(v, dict) or isinstance(v, _dict):
            res[k] = _dict(v)
        else:
            res[k] = v

    return res
