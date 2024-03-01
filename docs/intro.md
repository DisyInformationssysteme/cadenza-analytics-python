<pre>    
 <b>!! This module is currently in beta status !!</b>

    It can be used for testing, but there may be breaking changes before a full release.
    This documentation is still under developement as well.
    It is not yet recommended to use disy Cadenza Analytics Extension in production.

</pre>


# disy Cadenza Analytics Extensions

An Analytics Extension extends the functional spectrum of [disy Cadenza](https://www.disy.net/en/products/disy-cadenza/) with an analysis function or a visualisation type. An Analytics Extension is a web service that exchanges structured data with disy Cadenza via the Cadenza API. A user can integrate an analysis extension into disy Cadenza via the Management Center and manage it there (if they have the appropriate rights).

As of disy Cadenza Autumn 2023 (9.3), the following types and capabilities of analysis extensions are officially supported:

- **Visualization** 
  The Analytics Extension type `visualization` provides a new visualization type for displaying a bitmap image (PNG).

- **Data enrichment**
  The Analytcs Extension type `enrichment` returns data that enriches an existing Cadenza object type by adding additional attributes, which virtually add additional columns to the original data set.

- **Data generation**
  The Analytics Extension type `calculation` provides a result data set that is created as a new Cadenza object type.

## Communication

An Analytics Extension defines one endpoint that, depending in the HTTP method of the request, is used to supply the Extension's configuration to disy Cadenza, or exchange data and results with Cadenza respectively.

<!--- Beware: path to image must not be relative to this document, but relative to the one that includes this md file! (in this case: src/cadenzaanalytics/__init__.py--->
<img src="../../docs/communication.png" alt="(Image: Communication between disy Cadenza and Analytics Extension)" width="800">

When receiving an `HTTP(S) GET` request, the endpoint returns a JSON representation of the extention's configuration. This step is executed once when registering the Analytics Extension from the disy Cadenza Management Center GUI and does not need to be repeated unless the extension's configuration changes.

By sending an `HTTP(S) POST` request to the same endpoint and including the data, metadata and parameters as specified in the extension's configuration as payload, the extension is executed. This step is executed each time that the Analytics Extension is invoked from the disy Cadenza GUI and Cadenza takes care of properly formatting the payload.

The `cadenzaanalytics` module provides the functionality to abstract the required communication and easily configure the Analytics Extension's responses to the above requests. 


# Installation

As long as this package is in beta, it is only available on GitHub, and an installation via source is necessary. In the near future this package will also be made available via the Python Package Index (PyPI).

To install the package the [GitHub repository](https://github.com/DisyInformationssysteme/cadenza-analytics-python) needs to be cloned. Once the repository is locally available the package can be installed via `pip`. Navigate to the root folder of the project and run:

```
pip install .
```


## Dependencies

* Python 3
* Flask
* Pandas
* requests-toolbelt


# Usage

The following code snippets show the steps that are needed to develop and deploy custom functionality as a disy Cadenza Analytics Extension.

Full, working examples can be found in the [module's GitHub repository](https://github.com/DisyInformationssysteme/cadenza-analytics-python/tree/main) in the `examples` folder.

Initially, the module must be imported:

```
import cadenzaanalytics as ca
```


## Defining Expected Data

We specify what data can be passed from disy Cadenza to the Anylytics Extension by defining at least one `cadenzaanalytics.data.attribute_group`.

```
my_attribute_group = ca.AttributeGroup(
                         name='my_data',
                         print_name='Any numeric attribute',
                         data_types=[ca.DataType.INT64, 
                                     ca.DataType.FLOAT64],
                         min_attributes=1,
                         max_attributes=1
                     )
```

This object requires a `name`, a `print_name` and defines the respective `data_types` (cmp. `cadenzaanalytics.data.data_type`) that will later be available for selection in disy Cadenza when invoking the extension's execution.
Optionally, the number of individual attributes (i.e. data columns) that may be passed to the extension can be constrained.

Multiple `AttributeGroup` objects may be defined.

## Defining Expected Parameters

An extension may or may not require parametrization beyond the actual data that is passed to it.
A parameter can be optionally defined by creating a `cadenzaanalytics.data.parameter` object.


```
my_param = ca.Parameter(
               name='flag',
               print_name='Some flag that my analysis needs',
               parameter_type=ca.ParameterType.BOOLEAN,
               default_value='True'
           )
```
This object again requires a `name` and a `print_name`, as well as a `cadenzaanalytics.data.parameter_type`.
Optionally, we can specify whether an attribute needs to be specified and/or a default value.
Multiple parameters can be defined. 

As an alternative to requesting input of a parameter in one of the standard data types, a list from which a user selects a value can be defined via the `SELECT` type:

```
my_param2 = ca.Parameter(
                name='dropdown',
                print_name='Select option'
                parameter_type=ca.ParameterType.SELECT,
                required=True,
                default_value='Option 1',
                options=['Option 1', 'Option 2', 'Option 3']
            )
```

## Configuring the Extension

To specify the endpoint where the extension expects to receive from disy Cadenza and tie the previous configration together, a `CadenzaAnalyticsExtension()` must be defined.

```
my_extension = ca.CadenzaAnalyticsExtension(
                   relative_path='my-extension',
                   analytics_function=my_analytics_function,
                   print_name='My extension's print name in Cadenza', ,
                   extension_type=ca.ExtensionType.CALCULATION,
                   attribute_groups=[my_attribute_group],
                   parameters=[my_param, my_param2]
               )
```

The `relative_path` defines the endpoint, i.e. the subdirectory of the URL under wich the extension will be available after deployment.
Further parameters include the `print_name` shown in Cadenza, and the attribute groups and parameters defined above. 
Additionally, the appropriate `cadenzaanalytics.data.extension_type` (visualization, enrichment, or calculation) must be specified.

The `analytics_function` is the name of the Python method that should be invoked (see next section).

## Including Custom Analytics Code

The analysis function `analytics_function` is the method that contains the specific functionality for the extension. 
It implements what the extension should be doing when being invoked from disy Cadenza. 
This method takes two arguments,  `metadata` and `data`.

```
def analytics_function (metadata: ca.RequestMetadata, data: pd.DataFrame):
    # do something
    return #something
```

The actual content and return type of this function will depend both on the extension type (visualization, enrichment, or calculation) and naturally the actual analytics code that the extension should execute. 

### Reading Data, Metadata and Parameters

Accessing the data that is transferred from Cadenza is very simple.
Within the defined analytics function, a [pandas DataFrame](https://pandas.pydata.org/) `data` is available that can be directly accessed.

Currently, the following Cadenza attribute types can be passed to an Analytics Extension.
The table shows the mapping to Pyton data types:

| Cadenza Attribute Type              | Pandas Column Type |  Example Value       | Notes |
|-------------------------------------|-----------|--------------------------|-------|
| Text (String)                       | string    | `"Text"`                 | |
| Number (Integer)                    | pandas.Int64Dtype     | `1`                      | |
| Number (Long)                       | pandas.Long64Dtype    | `1`                      | |
| Floating point number (Double)      | pandas.Float64Dtype   | `1.23`                   | |
| Date                                | string    | `"2022-11-12T12:34:56+13:45[Pacific/Chatham]"` | A date is represented as an [ISO string with time zone offset from UTC](https://en.wikipedia.org/wiki/ISO_8601#Coordinated_Universal_Time_(UTC)) (UTC) and additional time zone identifier in brackets. |
| Geometry                            | string    | `"POINT(8.41594949941623, 49.0048124984033)"` | A geometry is represented as a [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) string.<br><br>*Note:* By default, coordinates use the WGS84 projection. | 

The same is true for the `cadenzaanalytics.request.request_metadata` object, which automatically is available as `metadata`. 

Parameters are always passed as `string` and can be read through the `cadenzaanalytics.request.request_metadata` methods `get_parameter` for a single parameter, respectively `get_parameters` for a dictionary of all parameters.

```
param_flag = metadata.get_parameter('flag')
```

## Returning Data

TBD

## Registering the Extension

TBD

# Deployment 

TBD

