<pre>    
 <b>!! This module is currently in beta status !!</b>

    It can be used for testing, but there may be breaking changes before a full release.
    This documentation is still under developement as well.

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

An Analytics Extension defines one endpoint that, depending on the HTTP method of the request, is used to supply the Extension's configuration to disy Cadenza, or exchange data and results with Cadenza respectively.

<!--- Beware: when building documentation locally, path to image must not be relative to this document, but relative to the one that includes this md file! 
             (in this case: src/cadenzaanalytics/__init__.py  ->  <img src="../../docs/communication.png"... )
             but when building per github action, the path must be relative to root
--->
<img src="communication.png" alt="(Image: Communication between disy Cadenza and Analytics Extension)" width="800">

When receiving an `HTTP(S) GET` request, the endpoint returns a JSON representation of the extention's configuration. This step is executed once when registering the Analytics Extension from the disy Cadenza Management Center GUI and does not need to be repeated unless the extension's configuration changes.

By sending an `HTTP(S) POST` request to the same endpoint and including the data, metadata and parameters as specified in the extension's configuration as payload, the extension is executed. This step is executed each time that the Analytics Extension is invoked from the disy Cadenza GUI and Cadenza takes care of properly formatting the payload.

The `cadenzaanalytics` module provides the functionality to abstract the required communication and easily configure the Analytics Extension's responses to the above requests. 


# Installation

As long as this package is in beta, it is only available on GitHub, and an installation via source is necessary. In the near future this package will also be made available via the Python Package Index (PyPI). 

Furthermore, a corresponding version will be packaged as source code with each release of disy Cadenza.

## Requirements and Dependencies

The `cadenzaanalytics` package has the following dependencies:

* Python 3
* [Flask](https://flask.palletsprojects.com/en/3.0.x/)
* [Pandas](https://pandas.pydata.org/)
* requests-toolbelt

The first version of disy Cadenza that supports Analytics Extensions is disy Cadenza Autumn 2023 (9.3). For each disy Cadenza version, the correct corresponding library version needs to be used:

|disy Cadenza version | cadenzaanalytics version|
|---------------------|-------------------------|
| 9.3 (Autumn 2023)   |             < 0.2 (beta)|



<!-- 
## Installation via PyPI

The simplest way to install `cadenzaanalytics` is from the [Python Package Index (PyPI)](https://pypi.org/project/cadenzaanalytics/) using the package installer [`pip`](https://pypi.org/project/pip/). To install the most recent version, simply execute
```
pip install cadenzaanalytics
```

In order to install a specific version of `cadenzaanalytics`, e.g. to develop an Analytics Extension for an older version of disy Cadenza, specify the version in the `pip` call:

```
pip install cadenzaanalytics==0.1.21
```
-->


## Installation from Source
The source of the package can be obtained from the project's public [GitHub repository](https://github.com/DisyInformationssysteme/cadenza-analytics-python). Alternatively with each release of disy Cadenza, the offline source code of the matching version of `cadenzaanalytics` is packaged in the distributions `developer.zip`.

Once the repository is locally available, the package can be installed using the package installer [`pip`](https://pypi.org/project/pip/). 
To install the package from source, navigate to the root folder of the project and run:

```
pip install .
```


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
Optionally, we can specify whether a parameter is mandatory and/or a default value for it.
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

To specify the endpoint where the extension expects to receive from disy Cadenza and tie the previous configuration together, a [`CadenzaAnalyticsExtension()`](cadenzaanalytics/cadenza_analytics_extension.html) must be defined.

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

The analysis function `my_analytics_function` (or whatever you choose to name it) is the method that contains the specific functionality for the extension. 
It implements what the extension should be doing when being invoked from disy Cadenza. 
This method takes two arguments,  `metadata` and `data`, which both will be passed to it automatically when the extension is invoked from Cadenza.

```
def my_analytics_function (metadata: ca.RequestMetadata, data: pd.DataFrame):
    # do something
    return #something
```

The actual content and return type of this function will depend both on the extension type (visualization, enrichment, or calculation) and naturally the actual analytics code that the extension should execute. 

### Reading Data, Metadata and Parameters

Accessing the data that is transferred from Cadenza is simple.
Within the defined analytics function, a [Pandas DataFrame](https://pandas.pydata.org/) `data` is automatically available, which holds all the data passed from Cadenza.

Same as the `data` object, the `cadenzaanalytics.request.request_metadata` object is also automatically available in the analysis function as `metadata`. 

The `metadata` object contains information on the columns in the `data` DataFrame, such as their print name and type in disy Cadenza, their column name in the pandas DataFrame, or additional information like a `geometry_type`, where applicable.

This information can be used to access the `data` DataFrame's columns by the attribute group's name.

```
all_data_columns = metadata.get_all_columns_by_attribute_groups()

my_data_columns = all_data_columns.get('my_data')

if my_data_columns is not None:
    my_data = data[my_data_columns[0].name]
```

While it is also possible to directly access the columns of `data` by name or by index, this is less robust, since the actual column names of the dataframe depend on their configuration in disy Cadenza and changing them there might lead to the extension not functioning properly anymore.


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


Parameters are stored in `metadata` as well. They are always passed as `string` and can be read through the `cadenzaanalytics.request.request_metadata` methods `get_parameter` for a single parameter, respectively `get_parameters` for a dictionary of all parameters.

```
param_flag = metadata.get_parameter('flag')
```

## Returning Data

Depending on the extension type, there are specific objects for returning the response.

### Data Generation

A `cadenzaanalytics.response.csv_response` is used for calculations.
The response must include the data and the proper metadata 

The following example returns the data received from disy Cadenza back to it.
```
def echo_analytics_function(metadata: ca.RequestMetadata, data: pd.DataFrame):
    return ca.CsvResponse(data, metadata.get_all_columns_by_attribute_groups()['any_data'])
```


### Data Enrichment

A `cadenzaanalytics.response.csv_response` is used for enrichments as well.
The response must be in the format of a text, a CSV file or a DataFrame so that it fits. 

TODO

The metadata must be adapted and also returned to disy Cadenza via the response method.

TODO

### Visualization
As result of a visualization extension, an `cadenzaanalytics.response.image_response` must be returned.
Visualization extensions return a bitmap image in PNG format.

The image can be created in various ways, e.g. by using FigureCanvas from matplotlib to render a plot or image.
The following snippet shows returning an image loaded from a file.

```
with open("example_image.png", "rb") as image_file:
    image = image_file.read()

return ca.ImageResponse(image)
```


### Returning an Error
In order to abort the execution of the function with an error and pass an according message to disy Cadenza, a `cadenzaanalytics.response.error_response` can be returned.

```
if my_data is None:
        return ca.ErrorResponse('Didn't find expected attribute "my_data".', 400)
```

## Registering the Extension

TBD

```
analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.add_analytics_extension(my_extension)
```

TODO "directory" service multiple extensions

# Deployment 

Since `cadenzaanalytics` is built on the [Flask framework](https://flask.palletsprojects.com/en/3.0.x/), ...

## Local Execution

```
if __name__ == '__main__':
    analytics_service.run_development_server(8080)

```

## WSGI Deployment
