# Cadenza Analytics Python
**cadenzaanalytics** for python is the official package for fast and easy creation of [disy Cadenza](https://www.disy.net/de/produkte/cadenza/datenanalyse-software/) analytics extensions. It enables the extension of disy Cadenza for advanced analytics purposes with the usage of python code.

Currently, this package is in **beta status**: it can be used for testing, but there
may be breaking changes before a full release.


## Development of Cadenza Analytics Python

### Development Environment
Development is possible via most common IDEs such as Visual Studio Code or PyCharm. Make sure to mark the `src` directory as "Sources Root" to make sure cross imports from the `examples` directory work as expected.

### Versioning
Versioning will happen via [setuptools-scm](https://setuptools-scm.readthedocs.io/en/latest/config/). This dynamically creates a version from an annotated git tag, by default expecting a tag in the style `v0.0.4` to create a version number `0.0.4`.
If the current git status is not tagged it will append a local-part to the version; see [pyproject.toml > tool.setuptools_scm > local_scheme](pyproject.toml) for configuration. 
To find out what version number will be generated use `python -m setuptools_scm` (after installation, e.g. `pip install setuptools_scm`).

## Installation:
As this package is currently only available on GitHub, an installation via source is necessary. In the near future this package will also be made available via the Python Package Index (PyPI).

To install the package the repository needs to be cloned. Once the repository is locally available the package can be installed via pip. Navigate to the root folder of the project and run:

```
pip install .
```


## Dependencies:
* Python 3
* Flask
* Pandas
* requests-toolbelt


## Example:
An example for an image visualisation can be found in `examples/extension/image-demo-extension.py`.

To test the example extension, navigate to the folder `examples/extension`. Run the example file in your python environment e.g.:
```
python image-demo-extension.py
```
A development server will be started on localhost `http://127.0.0.1:5005`. The analytics extension can now be registered and used in disy Cadenza.

It is not recommended to use the development server in a production environment.


## License:
[License](LICENSE.md)