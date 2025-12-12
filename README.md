# Pythia workflow for Scry

This plugin permits running Pythia searches with straightforward configuration.
Many key choices are made for the user to simplify the experience.

## Installation  

This library requires Python 3.8+ and can be installed with pip:  

```shell
pip install 'scry-pythia-workflow[local]'
```

## Basic Usage  

After [installation](#installation), you can directly run the `pythia_scry` command from the terminal:

```shell
pythia_scry --library /path/to/library.tsv --fasta /path/to/database.fasta --config /path/to/config.pythiaConfig file1.mzML file2.mzML
```

For a full list of arguments, run:

```shell
pythia_scry --help
```

## Advanced Usage with Scry

This package provides plugins for [Scry](https://github.com/seerbio/scry/).

After [installation](#installation) you may use the
following Scry parameters:

```toml
workflow = "pythia"
library = "/path/to/library.tsv"
fasta = "/path/to/database.fasta"
config = "/path/to/config.pythiaConfig"

mzml = [
"file1.mzML",
"file2.mzML",
]
```

For a complete list of supported parameters, see the project's documentation (linked in the sidebar above).
