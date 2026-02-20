"""
CLI for Radiant DIA + Fulcrum Pipeline
"""

import logging
from typing import (
    Tuple as _Tuple,
)

import click
import toml

from fulcrum.cli import main as fulcrum_main

_logger = logging.getLogger(__name__)


def _check_config(ctx, param, value):
    """
    Callback to check that the config file is a valid config.
    """
    if value is not None:
        if not (
            value.endswith(".radiantConfig")
            or value.endswith(".toml")
            or value.endswith(".pythiaConfig")
        ):
            raise click.BadParameter("Unsupported config file extension")
    return value


@click.command(
    name="radiant_fulcrum",
    help="""
    CLI for running Radiant DIA within the Fulcrum Pipeline.
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
    help="URI of a Radiant DIA configuration file (TOML format).",
    metavar="URI",
)
@click.option(
    "--mbr/--no-mbr",
    "--no-libfree/--libfree",
    is_flag=True,
    type=bool,
    default=False,
    help="Whether to run match-between-runs (MBR) after searching with Radiant DIA. Default: --libfree.",
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
    help="Number of threads to use when running Radiant DIA. Default: 0 (auto-detect).",
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
    CLI for running Radiant DIA within the Fulcrum Pipeline.
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
    _logger.debug("Will run Fulcrum with parameters:\n%s", param_toml)

    fulcrum_main.callback(
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
    Compute parameters to pass to Fulcrum based on CLI arguments.
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
        workflow="radiant",
        spark_config={
            # Enhancement: allow master to be set via CLI, to allow core count control or remote cluster
            "spark.master": "local[*]",
            # TODO: allow controlling driver memory
            "spark.driver.memory": "8g",
        },
    )


if __name__ == "__main__":
    main()
