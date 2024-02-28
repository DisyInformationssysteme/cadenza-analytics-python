    !! This module is currently in beta status.

# Cadenza Analytics Extensions
Cadenza Analytics is the offical package for fast and easy creation of [disy Cadenza](https://www.disy.net/en/products/disy-cadenza/) Analytics Extensions with Python. The purpose of this module is to encapsule the communication via the Cadenza API.

An Analytics Extension extends the functional spectrum of [disy Cadenza](https://www.disy.net/en/products/disy-cadenza/) with an analysis function or a visualisation type. An Analytics Extension exchanges structured data with Cadenza via the Cadenza API and both receives data from and returns data to Cadenza. A user can integrate an analysis extension into Cadenza via the Cadenza Management Center and manage it there (if they have the appropriate rights).


Currently this package is in beta status: it can be used for testing, but there may be breaking changes before a full release and this documentation is still being developed.


## Installation
As this package is currently only available on GitHub, an installation via source is necessary. In the near future this package will also be made available via the Python Package Index (PyPI).

To install the package the repository needs to be cloned. Once the repository is locally available the package can be installed via pip. Navigate to the root folder of the project and run:

```
pip install .
```


## Dependencies
* Python 3
* Flask
* Pandas
* requests-toolbelt

