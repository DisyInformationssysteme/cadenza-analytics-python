<pre>    
 <b>!! This module is currently in beta status !!</b>

    It can be used for testing, but there may be breaking changes before a full release.
    This documentation is still under developement as well.

</pre>

Cadenza Analytics is the offical package for fast and easy creation of [disy Cadenza](https://www.disy.net/en/products/disy-cadenza/) Analytics Extensions with Python. The purpose of this module is to encapsule the communication via the Cadenza API.

# Cadenza Analytics Extensions

An Analytics Extension extends the functional spectrum of [disy Cadenza](https://www.disy.net/en/products/disy-cadenza/) with an analysis function or a visualisation type. An Analytics Extension exchanges structured data with Cadenza via the Cadenza API and both receives data from and returns data to Cadenza. A user can integrate an analysis extension into Cadenza via the Cadenza Management Center and manage it there (if they have the appropriate rights).

As of Cadenza Autumn 2023 (9.3), the following types and capabilities of analysis extensions are officially supported:

- **Visualization** 
  The Analytics Extension provides a new visualization type for displaying a bitmap image (PNG).

- **Data enrichment**
  The Analytcs Extension returns data that enriches an existing Cadenza object type by adding additional attributes, which virtually add additional columns to the original data set.

- **Data generation**
  The Analytics Extension provides a result data set that is created as a new Cadenza object type.


# Installation
As this package is currently only available on GitHub, an installation via source is necessary. In the near future this package will also be made available via the Python Package Index (PyPI).

To install the package the [GitHub repository](https://github.com/DisyInformationssysteme/cadenza-analytics-python) needs to be cloned. Once the repository is locally available the package can be installed via pip. Navigate to the root folder of the project and run:

```
pip install .
```


## Dependencies
* Python 3
* Flask
* Pandas
* requests-toolbelt



# Supported Data Types

Currently, the following Cadenza attribute types can be passed to an Analytics Extension.
The table shows the mapping to Python data types:

| Cadenza Attribute Type              | Pandas Column Type |  Example Value       | Notes |
|-------------------------------------|-----------|--------------------------|-------|
| Text (String)                       | string    | `"Text"`                 | |
| Number (Integer)                    | pandas.Int64Dtype     | `1`                      | |
| Number (Long)                       | pandas.Long64Dtype    | `1`                      | |
| Floating point number (Double)      | pandas.Float64Dtype   | `1.23`                   | |
| Date                                | string    | `"2022-11-12T12:34:56+13:45[Pacific/Chatham]"` | A date is represented as an [ISO string with time zone offset from UTC](https://en.wikipedia.org/wiki/ISO_8601#Coordinated_Universal_Time_(UTC)) (UTC) and additional time zone identifier in brackets. |
| Geometry                            | string    | `"POINT(8.41594949941623, 49.0048124984033)"` | A geometry is represented as a [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) string.<br><br>*Note:* By default, coordinates use the WGS84 projection. | 

