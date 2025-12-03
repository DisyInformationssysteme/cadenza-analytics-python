For a minimal working example, see the [Quick Start](#quick-start) section below.

This is the documentation for `cadenzaanalytics` version {{version}}.

# disy Cadenza Analytics Extensions

An Analytics Extension extends the functional spectrum of [disy Cadenza](https://www.disy.net/en/products/disy-cadenza/) with an analysis function or a visualisation type.
An Analytics Extension is a web service that exchanges structured data with disy Cadenza via the Cadenza API.
A user can integrate an analysis extension into disy Cadenza via the Management Center and manage it there (if they have the appropriate rights).

As of disy Cadenza Autumn 2023 (9.3), the following types and capabilities of analysis extensions are officially supported:

- **Data**: Returns a structured data set from which a new Cadenza object type can be created.
- **Enrichment**: Enriches an existing Cadenza object type by adding additional attributes (columns).
- **Visual**: Returns static content (PNG image, text, or URL) to be displayed in a Cadenza view or through a map operation.


## Communication

An Analytics Extension defines one endpoint that, depending on the HTTP method of the request, is used to supply the Extension's configuration to disy Cadenza, or exchange data and results with Cadenza respectively.

<!--- Beware: when building documentation locally, path to image must not be relative to this document, but relative to the one that includes this md file!
             (in this case: src/cadenzaanalytics/__init__.py  ->  <img src="../../docs/communication.png"... )
             but when building via github action, the path must be relative to root
--->
<img src="communication.png" alt="(Image: Communication between disy Cadenza and Analytics Extension)" width="800">

When receiving an `HTTP(S) GET` request, the endpoint returns a JSON representation of the extension's configuration.
This step is executed once when registering the Analytics Extension from the disy Cadenza Management Center GUI and does not need to be repeated unless the extension's configuration changes.

By sending an `HTTP(S) POST` request to the same endpoint and including the data, metadata and parameters as specified in the extension's configuration as payload, the extension is executed.
This step is executed each time that the Analytics Extension is invoked from the disy Cadenza GUI and Cadenza takes care of properly formatting the payload.

The `cadenzaanalytics` module provides the functionality to abstract the required communication and easily configure the Analytics Extension's responses to the above requests.


# Installation

## Requirements and Dependencies

The `cadenzaanalytics` package has the following dependencies:

* Python 3.12+
* [Flask](https://flask.palletsprojects.com/en/3.0.x/)
* [Pandas](https://pandas.pydata.org/)
* [Shapely](https://shapely.readthedocs.io/)
* requests-toolbelt
* chardet

For each disy Cadenza version, the correct corresponding library version needs to be used.
The disy Cadenza main version is reflected in the corresponding major and minor version of `cadenzaanalytics` (e.g. 10.4.0 for Cadenza 10.4), while the last version segment is increased for both bugfixes and functional changes.

For Cadenza 10.2 and earlier versions, `cadenzaanalytics` used a semantic versioning scheme.
The first version of disy Cadenza that supported Analytics Extensions is disy Cadenza Autumn 2023 (9.3).

## Installation via PyPI

The simplest way to install `cadenzaanalytics` is from the [Python Package Index (PyPI)](https://pypi.org/project/cadenzaanalytics/) using the package installer [`pip`](https://pypi.org/project/pip/).
To install the most recent version, simply execute
```console
pip install cadenzaanalytics
```

In order to install a specific version of `cadenzaanalytics`, e.g. to develop an Analytics Extension for an older version of disy Cadenza, specify the version in the `pip` call:

```console
pip install cadenzaanalytics==10.3.0
```

## Installation from Source
The source of the package can be obtained from the project's public [GitHub repository](https://github.com/DisyInformationssysteme/cadenza-analytics-python).

Once the repository is locally available, the package can be installed using the package installer [`pip`](https://pypi.org/project/pip/).
To install the package from source, navigate to the root folder of the project and run:

```console
pip install .
```


# Quick Start

Here is a complete, minimal example of a Data Extension that echoes the input data back to Cadenza:

```python
import cadenzaanalytics as ca

# 1. Define the analytics function
def echo_function(request: ca.AnalyticsRequest):
    table = request["table"]
    return ca.DataResponse(table.data, table.metadata.columns)

# 2. Define what data the extension accepts
my_attribute_group = ca.AttributeGroup(
    name="data",
    print_name="Any data",
    data_types=[ca.DataType.STRING, ca.DataType.INT64, ca.DataType.FLOAT64]
)

# 3. Wrap attribute groups in a Table
my_table = ca.Table(name="table", attribute_groups=[my_attribute_group])

# 4. Configure the extension
my_extension = ca.CadenzaAnalyticsExtension(
    relative_path="echo-extension",
    print_name="Echo Extension",
    extension_type=ca.ExtensionType.DATA,
    tables=[my_table],
    analytics_function=echo_function
)

# 5. Register and run
analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.add_analytics_extension(my_extension)

if __name__ == "__main__":
    analytics_service.run_development_server(port=5000, debug=True)
```

The key components are:

1. **Analytics function**: Receives an `AnalyticsRequest` and returns a response. Access the table via `request["table"]`, then use `.data` to get the pandas DataFrame.

2. **AttributeGroup**: Defines what columns the user can select in Cadenza. The `name` becomes the column name (or prefix for multi-column groups).

3. **Table**: Wraps one or more attribute groups. The table's `name` (here `"table"`) is how you access it in your function via `request["table"]`.

4. **CadenzaAnalyticsExtension**: Ties everything together with a URL path, display name, and extension type.

5. **CadenzaAnalyticsExtensionService**: Registers extensions and runs the web server.

Save this as `my_extension.py` and run it with `python my_extension.py`. The extension will be available at `http://localhost:5000/echo-extension`.

More complete examples can be found in the [`examples` folder of the module's GitHub repository](https://github.com/DisyInformationssysteme/cadenza-analytics-python/tree/main/examples).


# Usage

The following sections explain each component in detail, following the same order as the Quick Start example.

## The Analytics Function

The analytics function is the core of your extension. It receives an [`AnalyticsRequest`](cadenzaanalytics/request/analytics_request.html) and returns a response object.

```python
def my_analytics_function(request: ca.AnalyticsRequest):
    # Access data and metadata via the request object
    table = request["table"]
    data = table.data          # pandas DataFrame
    metadata = table.metadata  # RequestMetadata

    # Process the data
    result = do_something(data)

    # Return appropriate response
    return ca.DataResponse(result, metadata.columns)
```

The `request["table"]` access uses the table name you define when configuring expected data (see [Defining Expected Data](#defining-expected-data) below).

The return type depends on the extension type:
- **Data extensions**: Return [`DataResponse`](cadenzaanalytics/response/data_response.html)
- **Enrichment extensions**: Return [`EnrichmentResponse`](cadenzaanalytics/response/enrichment_response.html)
- **Visual extensions**: Return [`ImageResponse`](cadenzaanalytics/response/image_response.html), [`TextResponse`](cadenzaanalytics/response/text_response.html), or [`UrlResponse`](cadenzaanalytics/response/url_response.html)



### Reading Data

The `request` object provides access to tables by name:

```python
table = request["table"]
data = table.data          # pandas DataFrame with all the data passed from Cadenza
metadata = table.metadata  # RequestMetadata object
```

### Reading Metadata

The `metadata` object contains information on the columns in the `data` DataFrame, such as their print name and type in disy Cadenza, their column name in the pandas DataFrame, or additional information like a `geometry_type`, where applicable.

The metadata supports pythonic access patterns:

```python
# Get all columns as a list
all_columns = metadata.columns

# Access a specific column by name
column = metadata["column_name"]

# Check if a column exists
if "my_column" in metadata:
    column = metadata["my_column"]

# Iterate over column names
for column_name in metadata:
    print(column_name)

# Get columns grouped by attribute group
columns_by_group = metadata.groups
if "my_data" in columns_by_group:
    for column in columns_by_group["my_data"]:
        column_data = data[column.name]
```

### Reading Parameters

Parameters are accessed through the `request.parameters` object:

```python
# Get a parameter value
flag_value = request.parameters["flag"]

# Get parameter with default if not set
value = request.parameters.get("optional_param", 42)

# get full info about the parameter, e.g., the srs for geometry parameters
srs = request.parameters.info("geom").srs
```

### View Parameters (Visual Extensions)

For visual extensions used as Cadenza workbook views, you can access the view dimensions:

```python
view = request.parameters.view
width = view.width                    # View width in pixels
height = view.height                  # View height in pixels
pixel_ratio = view.device_pixel_ratio # Device pixel ratio for high-DPI displays
```

These values are `None` when the extension is invoked outside of a workbook view context.


## Defining Expected Data

To specify what data can be passed from disy Cadenza to the Analytics Extension, you define a [`Table`](cadenzaanalytics/data/table.html) containing one or more [`AttributeGroup`](cadenzaanalytics/data/attribute_group.html) objects.

### Table

A [`Table`](cadenzaanalytics/data/table.html) wraps attribute groups and defines how you access the data in your analytics function:

```python
my_table = ca.Table(
    name="table",
    attribute_groups=[my_attribute_group, another_group]
)
```

The `name` parameter (here `"table"`) is the key you use to access the table in your analytics function via `request["table"]`. Currently, at most one table per extension is supported.

### Attribute Groups

An [`AttributeGroup`](cadenzaanalytics/data/attribute_group.html) defines a set of columns that the user can select in Cadenza:

```python
my_attribute_group = ca.AttributeGroup(
    name="my_data",
    print_name="Any numeric attribute",
    data_types=[ca.DataType.INT64, ca.DataType.FLOAT64],
    min_attributes=1,
    max_attributes=1
)
```

Parameters:
- `name`: Internal identifier for the group (used to access columns in your code)
- `print_name`: Display name shown in Cadenza
- `data_types`: List of allowed [`DataType`](cadenzaanalytics/data/data_type.html) values
- `min_attributes`: Minimum number of columns the user must select (default: 0)
- `max_attributes`: Maximum number of columns the user can select (default: unlimited)

### Multi-Column Attribute Groups and Naming Convention

When an `AttributeGroup` allows multiple columns, the columns are named with a numeric suffix based on the group name:

```python
# Definition allowing 2-3 columns
number_group = ca.AttributeGroup(
    name="number",
    print_name="Numeric values",
    data_types=[ca.DataType.INT64, ca.DataType.FLOAT64],
    min_attributes=2,
    max_attributes=3
)

# In the analytics function, columns will be named:
# "number_1", "number_2", and optionally "number_3"
def my_function(request: ca.AnalyticsRequest):
    table = request["table"]
    result = table.data["number_1"] + table.data["number_2"]
    if "number_3" in table.data.columns:
        result += table.data["number_3"]
    return ca.DataResponse(...)
```

### Geometry Attribute Groups

For geometry data, use `DataType.GEOMETRY` and specify the allowed geometry types and coordinate reference system:

```python
geometry_group = ca.AttributeGroup(
    name="geometry",
    print_name="Location",
    data_types=[ca.DataType.GEOMETRY],
    geometry_types=[
        ca.GeometryType.POINT,
        ca.GeometryType.MULTIPOINT,
        ca.GeometryType.LINESTRING,
        ca.GeometryType.MULTILINESTRING,
        ca.GeometryType.POLYGON,
        ca.GeometryType.MULTIPOLYGON
    ],
    requested_srs="EPSG:4326",  # WGS84; use "EPSG:3857" for Web Mercator
    min_attributes=1,
    max_attributes=1
)
```

Geometry columns are automatically parsed from WKT strings into [Shapely](https://shapely.readthedocs.io/) geometry objects. You can use them directly with Shapely operations or convert to a GeoDataFrame:

```python
import geopandas as gpd

def my_function(request: ca.AnalyticsRequest):
    table = request["table"]
    # table.data is a pandas DataFrame, geometry columns contain Shapely objects
    gdf = gpd.GeoDataFrame(table.data, geometry="geometry")
    # Now you can use GeoPandas operations
```

### DateTime Attribute Groups

DateTime columns use `DataType.ZONEDDATETIME` and are automatically parsed as pandas datetime with timezone:

```python
datetime_group = ca.AttributeGroup(
    name="timestamp",
    print_name="Date/Time",
    data_types=[ca.DataType.ZONEDDATETIME],
    min_attributes=1,
    max_attributes=1
)
```

In your analytics function, the datetime column will be a pandas datetime64 with timezone information.


## Data Type Mapping

The following table shows how Cadenza attribute types map to Python/pandas types:

| Cadenza Attribute Type         | Pandas Column Type    | Python Type          | Notes |
|--------------------------------|-----------------------|----------------------|-------|
| Text (String)                  | string                | `str`                | |
| Number (Integer)               | pandas.Int64Dtype     | `int`                | Nullable integer |
| Number (Long)                  | pandas.Int64Dtype     | `int`                | Nullable integer |
| Floating point number (Double) | pandas.Float64Dtype   | `float`              | Nullable float |
| Date/Time                      | datetime64[ns, UTC]   | `datetime`           | Parsed with timezone |
| Geometry                       | object                | `shapely.Geometry`   | Parsed from WKT |


## Defining Parameters

An extension may require user-configurable parameters beyond the data.

### Basic Parameters

```python
my_param = ca.Parameter(
    name="threshold",
    print_name="Threshold value",
    parameter_type=ca.ParameterType.FLOAT64,
    default_value=0.5,
    required=False
)
```

Parameters:
- `name`: Internal identifier
- `print_name`: Display name in Cadenza
- `parameter_type`: One of [`ParameterType`](cadenzaanalytics/data/parameter_type.html) values
- `default_value`: Default value (optional)
- `required`: Whether the parameter is mandatory (default: False)

Available parameter types:
- `ParameterType.STRING`
- `ParameterType.INT64`
- `ParameterType.FLOAT64`
- `ParameterType.BOOLEAN`
- `ParameterType.ZONEDDATETIME`
- `ParameterType.GEOMETRY`
- `ParameterType.SELECT`

### Selection Parameters

For a dropdown selection:

```python
my_param = ca.Parameter(
    name="method",
    print_name="Calculation method",
    parameter_type=ca.ParameterType.SELECT,
    required=True,
    default_value="average",
    options=["average", "median", "sum"]
)
```

### Geometry Parameters

```python
area_param = ca.Parameter(
    name="area",
    print_name="Analysis area",
    parameter_type=ca.ParameterType.GEOMETRY,
    geometry_types=[ca.GeometryType.POLYGON],
    requested_srs="EPSG:4326",
    required=False
)
```

The geometry parameter value will be a Shapely geometry object.

**Note:** Parameters for Analytics Extensions of the type `visual` can currently *not* yet be assigned on the disy Cadenza side when displaying the result as a Cadenza view.


## Configuring the Extension

The [`CadenzaAnalyticsExtension`](cadenzaanalytics/cadenza_analytics_extension.html) ties everything together:

```python
my_extension = ca.CadenzaAnalyticsExtension(
    relative_path="my-extension",
    print_name="My Extension",
    extension_type=ca.ExtensionType.DATA,
    tables=[my_table],
    parameters=[my_param],
    analytics_function=my_analytics_function
)
```

Parameters:
- `relative_path`: URL path where the extension will be available
- `print_name`: Display name in Cadenza
- `extension_type`: One of `ExtensionType.DATA`, `ExtensionType.ENRICHMENT`, or `ExtensionType.VISUAL`
- `tables`: List of Table objects (currently at most one table is supported)
- `parameters`: List of Parameter objects (optional)
- `analytics_function`: The function to invoke when the extension is called


## Returning Responses

### Data Extensions

A [`DataResponse`](cadenzaanalytics/response/data_response.html) returns a new dataset to Cadenza:

```python
def data_function(request: ca.AnalyticsRequest):
    table = request["table"]
    result = process(table.data)

    # Option 1: Forward existing metadata
    return ca.DataResponse(result, table.metadata.columns)

    # Option 2: Define new metadata
    columns = [
        ca.ColumnMetadata(
            name="result",
            print_name="Result",
            data_type=ca.DataType.FLOAT64,
            role=ca.AttributeRole.MEASURE,
            measure_aggregation=ca.MeasureAggregation.SUM
        )
    ]
    return ca.DataResponse(result, columns)
```

The `column_metadata` parameter specifies how Cadenza should interpret each column. If metadata for a column is missing, it will be auto-generated by default. You can change this behavior with `missing_metadata_strategy`:

- `MissingMetadataStrategy.ADD_DEFAULT_METADATA` (default): Auto-generate metadata for missing columns
- `MissingMetadataStrategy.REMOVE_DATA_COLUMNS`: Remove columns without metadata from the response
- `MissingMetadataStrategy.RAISE_EXCEPTION`: Raise an error if metadata is missing

### Enrichment Extensions

An [`EnrichmentResponse`](cadenzaanalytics/response/enrichment_response.html) adds new columns to an existing Cadenza object type:

```python
def enrichment_function(request: ca.AnalyticsRequest):
    table = request["table"]
    data = table.data

    # Calculate new column
    data["calculated"] = data["input"] * 2

    # Define metadata for new columns only
    new_column = ca.ColumnMetadata(
        name="calculated",
        print_name="Calculated Value",
        data_type=ca.DataType.FLOAT64,
        role=ca.AttributeRole.MEASURE
    )

    return ca.EnrichmentResponse(data, [new_column])
```

The library automatically handles ID columns - they are taken from the request metadata and added to the response. You only need to specify metadata for the new columns you're adding.

To return only specific columns, use `REMOVE_DATA_COLUMNS`:

```python
return ca.EnrichmentResponse(
    data,
    [new_column],
    missing_metadata_strategy=ca.MissingMetadataStrategy.REMOVE_DATA_COLUMNS
)
```

### Visual Extensions

Visual extensions can return images, text, or URLs.

**Image Response:**

```python
def image_function(request: ca.AnalyticsRequest):
    # Create image (e.g., with matplotlib)
    import matplotlib.pyplot as plt
    from io import BytesIO

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    return ca.ImageResponse(buf.read())
```

For workbook views, use the view parameters to size your output:

```python
def responsive_image_function(request: ca.AnalyticsRequest):
    view = request.parameters.view
    width = view.width or 800
    height = view.height or 600
    dpi = 100 * (view.device_pixel_ratio or 1)

    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=dpi)
    # ... create plot ...
    return ca.ImageResponse(buf.read())
```

**Text Response:**

```python
def text_function(request: ca.AnalyticsRequest):
    result = "Analysis complete. Found 42 results."
    return ca.TextResponse(result)
```

**URL Response:**

```python
def url_function(request: ca.AnalyticsRequest):
    # Return a URL to be displayed in an iframe
    return ca.UrlResponse("https://example.com/report?id=123")
```

### Error Response

To abort execution and return an error message to Cadenza:

```python
def my_function(request: ca.AnalyticsRequest):
    table = request["table"]
    if "required_column" not in table.data.columns:
        return ca.ErrorResponse("Required column not found.", 400)

    # ... normal processing ...
```


## Registering and Running

Register the extension with a [`CadenzaAnalyticsExtensionService`](cadenzaanalytics/cadenza_analytics_extension_service.html):

```python
analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.add_analytics_extension(my_extension)

# You can register multiple extensions
analytics_service.add_analytics_extension(another_extension)
```

The service provides a root endpoint (`/`) that lists all registered extensions.


## Logging

`cadenzaanalytics` is built on top of Flask, which in turn uses standard Python logging.
This logger can also be used to log your own messages for your Analytics Extension, or define your own logger according to [standard Python logging](https://docs.python.org/3/howto/logging.html#).

The default log level of the `cadenzaanalytics` module is `INFO`.
To change the log level, set the environment variable `CADENZAANALYTICS_LOG_LVL` accordingly, e.g.
```console
export CADENZAANALYTICS_LOG_LVL='DEBUG'
```


# Deployment

Since `cadenzaanalytics` is built on the [Flask framework](https://flask.palletsprojects.com/en/stable), the deployment options for a Cadenza Analytics Extension are basically the same as for any Flask application.
Below, we present a few options, a more comprehensive overview can be found in the [Deploying to Production](https://flask.palletsprojects.com/en/stable/deploying/index.html) section of the official Flask documentation.

## Local Execution (Development Only)

For development purposes, using the built-in development server is most convenient.
However, it should not be used in production, as it has not been designed for security, stability, or efficiency.

```python
if __name__ == "__main__":
    analytics_service.run_development_server(port=5000, debug=True)
```

If `debug=True`, the Flask development server starts in debug mode with more verbose logging and automatic reload on code changes.
See [Flask documentation](https://flask.palletsprojects.com/en/stable/debugging/#the-built-in-debugger) for details.

## WSGI Deployment

For production, use a WSGI server like [Gunicorn](https://gunicorn.org/) or [uWSGI](https://uwsgi-docs.readthedocs.io/).

**Example with Gunicorn:**

Add an `app` export to your extension file (e.g., `echo_extension.py` from the Quick Start):
```python
# ... your extension code ...

analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.add_analytics_extension(my_extension)

# Export the Flask app for WSGI servers
app = analytics_service.app

if __name__ == "__main__":
    analytics_service.run_development_server(port=5000, debug=True)
```

Run with Gunicorn:
```console
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 echo_extension:app
```

For multiple workers:
```console
gunicorn --bind 0.0.0.0:8000 --workers 4 echo_extension:app
```

## Docker

A minimal Dockerfile for a Cadenza Analytics Extension:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "echo_extension:app"]
```

Example `requirements.txt`:
```
cadenzaanalytics
gunicorn
```

Build and run:
```console
docker build -t my-extension .
docker run -p 8000:8000 my-extension
```

## Advanced Configuration

### Running behing Reverse Proxy

When running behind a reverse proxy (like nginx), you may need to configure Flask to trust proxy headers. Use Werkzeug's `ProxyFix` middleware:

```python
from werkzeug.middleware.proxy_fix import ProxyFix

analytics_service = ca.CadenzaAnalyticsExtensionService()
analytics_service.app.wsgi_app = ProxyFix(
    analytics_service.app.wsgi_app, x_for=1, x_proto=1, x_host=1
)
```

### Adjusting Maximum Request Size
As of Werkzeug 3.1, the setting for `max_form_memory_size` is 500,000 bytes. 
Since Cadenza sends the payload as `multipart/form` data, this default setting may prove to be too low to accomodate the data sent from Cadenza.

The setting can be adjusted using
```python
from flask.wrappers import Request  # do NOT use the werkzeug.wrappers Request
    Request.max_form_memory_size = 100 * 1024 * 1024
```

