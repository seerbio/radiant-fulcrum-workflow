Docs for ``scry_pythia_workflow``
==================

This project provides a simplified workflow for running Pythia within
the Scry scalable proteomics analysis framework.

Getting Started
---------------

This library requires Python 3.8+ and can be installed with pip:

.. code :: shell

    pip install 'scry-pythia-workflow[local]'

You can then directly run the ``pythia_scry`` command from the terminal:

.. code :: shell

    pythia_scry --library /path/to/library.tsv --fasta /path/to/database.fasta file1.mzML file2.mzML

Scry Workflow
-------------

In addition to the ``pythia_scry`` command, this package provides a Scry workflow
that can be run with the ``scry`` command. You must provide appropriate parameters
in TOML or JSON format. For example:

.. code :: shell

    scry -v --param-toml '
    workflow = "pythia"
    library = "/path/to/library.tsv"
    fasta = "/path/to/database.fasta"

    mzml = [
        "file1.mzML",
        "file2.mzML",
    ]
    '

Contents
========

.. toctree::
    :maxdepth: 4
