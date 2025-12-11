"""
CLI for Scry+Pythia search
"""

import logging

import click
import toml

from scry.cli import main as scry_main

_logger = logging.getLogger(__name__)


@click.command(
    help="""
    CLI for running Pythia within the Scry search pipeline.
    """
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
    verbose,
    quiet,
):
    """
    CLI for running Pythia within the Scry search pipeline.
    """

    params_dict = _to_parameters(
        # TODO: pass CLI options/arguments
    )

    param_toml = toml.dumps(params_dict)
    _logger.debug("Will run Scry with parameters:\n%s", param_toml)

    scry_main(
        param_toml=param_toml,
        verbose=verbose,
        quiet=quiet,
    )


def _to_parameters(

):
    """
    Compute parameters to pass to scry based on CLI arguments.
    """
    raise NotImplementedError("TODO")