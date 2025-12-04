# Cadenza Analytics Python
**cadenzaanalytics** is the official package for fast and easy creation of [disy Cadenza](https://www.disy.net/en/products/disy-cadenza/) analytics extensions with Python.
It enables the extension of disy Cadenza for advanced analytics purposes with the usage of python code.

Find the docs at https://disyinformationssysteme.github.io/cadenza-analytics-python

[![CI](https://github.com/DisyInformationssysteme/cadenza-analytics-python/actions/workflows/ci.yml/badge.svg)](https://github.com/DisyInformationssysteme/cadenza-analytics-python/actions/workflows/ci.yml)
[![Pylint](https://github.com/DisyInformationssysteme/cadenza-analytics-python/actions/workflows/pylint.yml/badge.svg)](https://github.com/DisyInformationssysteme/cadenza-analytics-python/actions/workflows/pylint.yml)

## Dependencies:
* Python 3
* Flask
* Pandas
* requests-toolbelt
* chardet

## Installation:
The simplest way to install `cadenzaanalytics` is from the [Python Package Index (PyPI)](https://pypi.org/project/cadenzaanalytics/) using the package installer [pip](https://pypi.org/project/pip/).
To install the most recent version, simply execute
```console
pip install cadenzaanalytics
```

## Examples:
Example extensions can be found in [examples](https://github.com/DisyInformationssysteme/cadenza-analytics-python/tree/main/examples).

To test an example extension, clone this repository, install the dependencies, navigate to the folder, e.g. `examples/data/extension`.
Run the example file in your python environment e.g.:
```
python example_extensions.py
```
A development server will be started on localhost `http://127.0.0.1:5005`.
The analytics extension can now be registered and used in disy Cadenza.

It is not recommended to use the development server in a production environment.

## License:
[License](https://github.com/DisyInformationssysteme/cadenza-analytics-python/tree/main/LICENSE.md)
