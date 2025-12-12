"""
CLI for Scry+Pythia search
"""

import logging
from typing import (
    Tuple as _Tuple,
)

import click
import toml

from scry.cli import main as scry_main

_logger = logging.getLogger(__name__)


def _check_config(ctx, param, value):
    """
    Callback to check that the config file is a valid Pythia config.
    """
    if value is not None:
        if not value.endswith(".pythiaConfig"):
            raise click.BadParameter("extension must be `.pythiaConfig`")
    return value


@click.command(
    name="pythia_scry",
    help="""
    CLI for running Pythia within the Scry search pipeline.
    """,
)
@click.option(
    "--library",
    type=str,
    required=True,
    help="URI of a predicted, spectrum, or chromatogram library",
    metavar="URI",
)
@click.option(
    "--fasta",
    type=str,
    required=True,
    help="URI of a FASTA sequence database.",
    metavar="URI",
)
@click.option(
    "--config",
    type=str,
    required=False,
    default=None,
    callback=_check_config,
    help="URI of a Pythia configuration file (TOML format).",
    metavar="URI",
)
@click.option(
    "--mbr/--no-mbr",
    "--no-libfree/--libfree",
    is_flag=True,
    type=bool,
    default=False,
    help="Whether to run match-between-runs (MBR) after searching with Pythia. Default: --libfree.",
)
@click.option(
    "--fdr-thresh",
    "--fdr-threshold",
    type=float,
    required=False,
    default=0.01,
    help="FDR threshold threshold used for filtering PSMs, Precursors, and PGs.",
    metavar="FDR",
)
@click.option(
    "--threads",
    type=int,
    required=False,
    default=0,
    help="Number of threads to use when running Pythia. Default: 0 (auto-detect).",
    metavar="THREADS",
)
@click.option(
    "--results-dir",
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
    ),
    required=False,
    default=None,
    help="Directory to save parameters and results to. If not specified, a new folder will be created in the current working directory.",
    metavar="DIR",
)
@click.argument(
    "mzml_files",
    type=str,
    nargs=-1,
    metavar="MZML [MZML...]",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase the level of verbosity. May be specified multiple times.",
)
@click.option(
    "-q",
    "--quiet",
    count=True,
    help="Decrease the level of verbosity. May be specified multiple times.",
)
def main(
    library: str,
    fasta: str,
    config: str,
    mbr: bool,
    fdr_thresh: float,
    threads: int,
    results_dir: str,
    mzml_files: _Tuple[str],
    verbose,
    quiet,
):
    """
    CLI for running Pythia within the Scry search pipeline.
    """

    params_dict = _to_parameters(
        library,
        fasta,
        config,
        mbr,
        fdr_thresh,
        threads,
        results_dir,
        mzml_files,
    )

    param_toml = toml.dumps(params_dict)
    _logger.debug("Will run Scry with parameters:\n%s", param_toml)

    scry_main.callback(
        param_toml=param_toml,
        verbose=verbose,
        quiet=quiet,
    )


def _to_parameters(
    library: str,
    fasta: str,
    config: str,
    mbr: bool,
    fdr_thresh: float,
    threads: int,
    results_dir: str,
    mzml_files: _Tuple[str],
):
    """
    Compute parameters to pass to scry based on CLI arguments.
    """
    return dict(
        library=library,
        fasta=fasta,
        config=config,
        mbr=mbr,
        fdr_thresh=fdr_thresh,
        threads=threads,
        results_dir=results_dir,
        mzml=mzml_files,
        workflow="pythia",
        spark_config={
            # Enhancement: allow master to be set via CLI, to allow core count control or remote cluster
            "spark.master": "local[*]",
            # TODO: allow controlling driver memory
            "spark.driver.memory": "8g",
        },
    )


if __name__ == "__main__":
    main()
