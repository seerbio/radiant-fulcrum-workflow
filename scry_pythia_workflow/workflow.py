from typing import (
    Optional as _Optional,
    Tuple as _Tuple,
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

from scry.workflow import v1, mbr_workflow

def pythia(
    *args,  # TODO
    spark: _Optional[_SparkSession] = None,
    **kwargs,
) -> _Tuple[_PsmDataset, _ProteinDataset]:
    """
    Workflow for running Pythia within Scry.

    spark : SparkSession, optional
        A Spark session to use when creating the search result dataset. If ``None`` a session
        will be created with default configuration.
    kwargs :
        Any additional keyword arguments to pass to the underlying workflow (either `v1` or `mbr`).
    """
    raise NotImplementedError("TODO")