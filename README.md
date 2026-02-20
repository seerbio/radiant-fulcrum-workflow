# Radiant DIA workflow plugin for Fulcrum Pipeline

This plugin permits running Radiant DIA™ searches with straightforward configuration.
Many key choices are made for the user to simplify the experience.

## Installation  

This library requires Python 3.10+ and can be installed with pip:  

```shell
pip install 'radiant-fulcrum-workflow[local]'
```

## Basic Usage  

After [installation](#installation), you can directly run the `radiant_fulcrum` command from the terminal:

```shell
radiant_fulcrum --library /path/to/library.tsv --fasta /path/to/database.fasta --config /path/to/config.radiantConfig file1.mzML file2.mzML
```

For a full list of arguments, run:

```shell
radiant_fulcrum --help
```

## Advanced Usage in the Fulcrum Pipeline

This package provides plugins for [Fulcrum Pipeline™](https://github.com/seerbio/fulcrum/).

After [installation](#installation) you may use the
following parameters:

```toml
workflow = "radiant"
library = "/path/to/library.tsv"
fasta = "/path/to/database.fasta"
config = "/path/to/config.radiantConfig"

mzml = [
"file1.mzML",
"file2.mzML",
]
```

For a complete list of supported parameters, see the project's documentation (linked in the sidebar above).
