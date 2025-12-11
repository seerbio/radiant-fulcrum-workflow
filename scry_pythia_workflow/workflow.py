from typing import (
    Iterable as _Iterable,
    Optional as _Optional,
    Tuple as _Tuple,
    Union as _Union,
)

from pyspark.sql import (
    SparkSession as _SparkSession,
)

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
    updated_config = check_or_update_config(config, threads, results_dir)

    params = (to_mbr_params if mbr else to_libfree_params)(
        library=library,
        fasta=fasta,
        mzml=mzml,
        fdr_thresh=fdr_thresh,
        config=updated_config,
        threads=threads,
        results_dir=results_dir,
    )

    workflow = _mbr_workflow if mbr else _v1_workflow

    return workflow(**params, spark=spark, **kwargs)