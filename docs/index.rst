Docs for ``radiant_fulcrum_workflow``
==================

This project provides a simplified workflow for running Radiant DIA™ within
the Fulcrum Pipeline™ scalable proteomics analysis framework.

Getting Started
---------------

This library requires Python 3.8+ and can be installed with pip:

.. code :: shell

    pip install 'radiant-fulcrum-workflow[local]'

You can then directly run the ``radiant_fulcrum`` command from the terminal:

.. code :: shell

    radiant_fulcrum --library /path/to/library.tsv --fasta /path/to/database.fasta --config /path/to/config.radiantConfig file1.mzML file2.mzML

For a full list of arguments, run:

.. code :: shell

    radiant_fulcrum --help

Fulcrum Pipeline Workflow
-------------

In addition to the ``radiant_fulcrum`` command, this package provides a workflow
that can be run with the ``fulcrum`` command. You must provide appropriate parameters
in TOML or JSON format. For example:

.. code :: shell

    fulcrum -v --param-toml '
    workflow = "radiant"
    library = "/path/to/library.tsv"
    fasta = "/path/to/database.fasta"
    config = "/path/to/config.radiantConfig"

    mzml = [
        "file1.mzML",
        "file2.mzML",
    ]
    '

For a full list of supported parameters, see :py:func:`radiant_fulcrum_workflow.workflow.radiant`.

Contents
========

.. toctree::
    :maxdepth: 4
