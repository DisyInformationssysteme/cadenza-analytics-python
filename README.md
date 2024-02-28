# Cadenza Analytics Python
**cadenzaanalytics** for python is the official package for fast and easy creation of [disy Cadenza](https://www.disy.net/de/produkte/cadenza/datenanalyse-software/) analytics extensions. It enables the extension of disy Cadenza for advanced analytics purposes with the usage of python code.

Currently, this package is in **beta status**: it can be used for testing, but there
may be breaking changes before a full release.

[![CI](https://github.com/DisyInformationssysteme/cadenza-analytics-python/actions/workflows/ci.yml/badge.svg)](https://github.com/DisyInformationssysteme/cadenza-analytics-python/actions/workflows/ci.yml)
[![Pylint](https://github.com/DisyInformationssysteme/cadenza-analytics-python/actions/workflows/pylint.yml/badge.svg)](https://github.com/DisyInformationssysteme/cadenza-analytics-python/actions/workflows/pylint.yml)

## Dependencies:
* Python 3
* Flask
* Pandas
* requests-toolbelt


## Example:
An example extension can be found in [examples/extension/example_extensions.py](examples/extension/example_extensions.py).

To test the example extension, clone this repository, install the dependencies, navigate to the folder `examples/extension`. Run the example file in your python environment e.g.:
```
python example_extensions.py
```
A development server will be started on localhost `http://127.0.0.1:5005`. The analytics extension can now be registered and used in disy Cadenza.

It is not recommended to use the development server in a production environment.

## Development of Cadenza Analytics Python

### Development Environment
Development is possible via most common IDEs such as Visual Studio Code or PyCharm. Make sure to mark the `src` directory as "Sources Root" to make sure cross imports from the `examples` directory work as expected and that imports within `cadenzaanalytics` can get resolved by the IDE.

### Python version
We aim to support older python versions and dependencies, but best experience and most features will be available for newer versions, currently this is Python `9.12`.
### Versioning
Versioning of `cadenzaanalytics` will happen via [poetry-bumpversion](https://github.com/monim67/poetry-bumpversion). On release, this will bump the version depending on the chosen release type.
The project uses semantic versioning with a major, minor and patch version. 

### Documentation
On release, all "Unreleased" changes in the [Changelog](CHANGELOG.md) will be automatically tagged with the released version.
So make sure to add relevant changelog notes for every change you make and follow the style described in the changelog file.

### Pylint
[Pylint](https://github.com/pylint-dev/pylint) is used for making sure that `cadenzaanalytics` follows some common styles. If necessary some rules can be disabled globally in the [.pylintrc](.pylintrc) file or in the corresponding python file. There is a GitHub workflow to validate this. For some IDEs like PyCharm there are also plugins for Pylint so that linting can happen within the IDE and errors in the pipeline can be avoided.
### Releasing:
Make sure to check the following
- Does the [Changelog](CHANGELOG.md) contain all relevant information?
- Are all relevant workflows green?
- Do you want to make a test release to https://test.pypi.org? This is helpful to test `cadenzaanalytics` with existing extensions. To get the latest version immediately it might be good to disable caches, e.g. via `pip install --upgrade cadenzaanalytics --extra-index-url https://test.pypi.org/simple --no-cache-dir`. For a first installation in a new (virtual) environment, you can use `pip install cadenzaanalytics --extra-index-url https://test.pypi.org/simple` 
- To make a non-test release, choose the pypi.org deployment environment in the release dialog.

### Technical notes
The release process uses PyPi's [trusted publishing](https://docs.pypi.org/trusted-publishers/), so is based on
OIDC id token and uses no API token from PyPi. The relevant permission `id-token: write` must be given to the release-job.

The test environment test.pypi.org makes no guarantee on availability of the package or even on the account. So it might be necessary to recreate an account at some point in time.

To test and play around with poetry-bumpversion locally, you can use it as follows, see documentation of [poetry](https://python-poetry.org/docs/#installing-with-pipx) and [poetry-bumpversion](https://pypi.org/project/poetry-bumpversion/)
```commandline
pipx install poetry
pipx run poetry self add poetry-bumpversion
pipx run poetry version minor -s
```

## License:
[License](LICENSE.md)