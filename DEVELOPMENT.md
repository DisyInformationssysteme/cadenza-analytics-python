# Development of Cadenza Analytics Python

## Development Environment
Development is possible via most common IDEs such as Visual Studio Code or PyCharm.
Make sure to mark the `src` directory as "Sources Root" to make sure cross imports from the `examples` directory work as expected and that imports within `cadenzaanalytics` can get resolved by the IDE.

## Architecture Guidelines

The `cadenzaanalytics` library is designed with the following principles:

### Target Audience: Data Scientists
The primary users are data scientists who want to extend Cadenza with custom analytics.
The API should feel natural to someone familiar with Python data analysis workflows, not require deep knowledge of web frameworks or HTTP protocols.

### Pandas-Centric Abstraction
Input data from Cadenza is automatically converted to pandas DataFrames, and output data is expected as DataFrames. This abstraction:
- Hides the underlying CSV/multipart HTTP communication
- Allows users to focus on data transformation logic
- Leverages the pandas ecosystem that data scientists already know

### Pythonic Design
- Use clear, descriptive names over abbreviations
- Use properties over getters
- Prefer explicit configuration over implicit behavior
- Follow Python conventions (snake_case, type hints where helpful)
- Keep the public API surface minimal and intuitive

### Minimal Boilerplate
Extension authors should be able to create a working extension with minimal ceremony. The framework handles:
- HTTP routing and request parsing
- Data serialization/deserialization
- Extension discovery and registration
- Error handling and response formatting

### Flask as Implementation Detail
While Flask powers the HTTP layer, it should remain an implementation detail. Users interact with `CadenzaAnalyticsExtensionService` and `CadenzaAnalyticsExtension`, not Flask directly.

## Python version
We aim to support older python versions and dependencies, but best experience and most features will be available for newer versions, currently this is Python `3.12`.

## Versioning
Versioning of `cadenzaanalytics` will happen via [poetry-bumpversion](https://github.com/monim67/poetry-bumpversion).
On release, this will bump the version depending on the chosen release type.
For test releases, a prerelease (alpha) version is used (e.g. `10.3.0a0`).

## Documentation
On a proper release (i.e. not a test release), all "Unreleased" changes in the [Changelog](CHANGELOG.md) will be automatically tagged with the released version.
So make sure to add relevant changelog notes for every change you make and follow the style described in the changelog file.

Also, on a release, documentation for all version branches will be generated using `pdoc` and uploaded to this repositories githubpages at https://disyinformationssysteme.github.io/cadenza-analytics-python.
Reference documentation is built from docstrings.
The documentation workflow can also be triggered manually on the dedicated branch `githubpages`.

### Building Documentation Locally
In order to build the library documentation locally, e.g. during development, execute
```commandline
pdoc --logo https://www.disy.net/typo3conf/ext/contentelements/Resources/Public/dist/img/logo-disy.svg \
     --logo-link https://www.disy.net/en/products/disy-cadenza \
     --favicon https://www.disy.net/favicon.ico \
     --docformat numpy \
     -o docs/html \
     --no-show-source \
     src/cadenzaanalytics
```
This will locally write the documentation to `docs/html/`.

## Contributing

### Code Style

We use [Pylint](https://github.com/pylint-dev/pylint) for code quality. Key style rules:

- **Line length**: 120 characters maximum
- **Docstrings**: While not required (disabled in pylint), they are welcome and used for API reference doc generation. We use [NumPy docstring format](https://numpydoc.readthedocs.io/en/latest/format.html).
- **Type hints**: Encouraged for public APIs, optional for internal code

Globally disabled rules are configured in [.pylintrc](.pylintrc). For local suppressions, use:
```python
# pylint: disable=rule-name
```

Run pylint locally before submitting:
```commandline
pip install pylint
pylint --rcfile=.pylintrc $(git ls-files '*.py')
```

There is a GitHub workflow to validate this. For IDEs like PyCharm there are also plugins for Pylint so that linting can happen within the IDE and pipeline errors can be avoided.

### Changelog
Every user-facing change must include an entry in [CHANGELOG.md](CHANGELOG.md). 
Follow the existing format (based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)) and add entries under the "Unreleased" section.

### Pull Requests
- Ensure all GitHub workflows pass
- Add or update type hints and docstrings
- Update documentation if adding/changing public APIs
- Add or update examples if introducing new features

## Releasing:
Make sure to check the following
- Does the [Changelog](CHANGELOG.md) contain all relevant information?
- Are all relevant workflows green?
- Do you want to make a test release to https://test.pypi.org?
This is helpful to test `cadenzaanalytics` with existing extensions.
To get the latest version immediately it might be good to disable caches, e.g. via `pip install --upgrade cadenzaanalytics --extra-index-url https://test.pypi.org/simple --no-cache-dir`.
For a first installation in a new (virtual) environment, you can use `pip install cadenzaanalytics --extra-index-url https://test.pypi.org/simple`
- In test releases, CI changes to the repository (bumping the version, updating the changelog, etc.) are _not_ pushed.
- To make a proper non-test release, choose the `pypi.org` deployment environment in the release dialog.

## Dockerized Example Extension
To run the example (and your production application) in a docker container you will need to define the wsgi server that will run the flask app.
The provided Dockerfile in the examples uses gunicorn with some example options, for more details consult the [documentation](https://docs.gunicorn.org/en/latest/settings.html).
Important is that gunicorn has access to a function creating or providing the flask app object, which for `cadenzaanalytics` is the `CadenzaAnalyticsExtensionService`.
The requirements file can use test releases when adding `--extra-index-url https://test.pypi.org/simple` in the first line.
It can (re)define versions of its own or transient dependencies, but most importantly needs the `cadenzaanalytics` dependency.
```commandline
cd examples/data
docker build . -t cadenza-analytics-example
docker image list
docker run -p 8080:8080 YOUR_CREATED_IMAGE_ID
```

## Technical notes
The release process uses PyPi's [trusted publishing](https://docs.pypi.org/trusted-publishers/), so is based on
OIDC id token and uses no API token from PyPi.
The relevant permission `id-token: write` must be given to the release-job.

The test environment test.pypi.org makes no guarantee on availability of the package or even on the account.
So it might be necessary to recreate an account at some point in time.

To test and play around with poetry-bumpversion locally, you can use it as follows, see documentation of [poetry](https://python-poetry.org/docs/#installing-with-pipx) and [poetry-bumpversion](https://pypi.org/project/poetry-bumpversion/)
```commandline
pipx install poetry
pipx run poetry self add poetry-bumpversion
pipx run poetry version minor -s
```

The documentation build workflow runs on a separate branch `githubpages` for all version branches.
In order to enable cross-branch triggering of this workflow, a valid PAT with read content and read/write workflows permissions needs to be stored in the secret `WORKFLOW_TRIGGER_TOKEN`.
An alternative is to manually trigger the workflow.
