"""The `cadenzaanalytics` module provides functionality to extend the business
and location intelligence software [disy Cadenza](https://www.disy.net/en/products/disy-cadenza/)
with Analytics Extensions, which may be used to execute custom Python code, e.g.
to create, enrich or visualize data using Python.

The purpose of this module is to encapsulate the communication via the Cadenza API.

.. include:: ../../docs/intro.md
"""
import os
from logging.config import dictConfig

from cadenzaanalytics.cadenza_analytics_extension import CadenzaAnalyticsExtension
from cadenzaanalytics.cadenza_analytics_extension_service import CadenzaAnalyticsExtensionService

from cadenzaanalytics.data.analytics_extension import AnalyticsExtension
from cadenzaanalytics.data.attribute_group import AttributeGroup
from cadenzaanalytics.data.attribute_role import AttributeRole
from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.data.extension_type import ExtensionType
from cadenzaanalytics.data.geometry_type import GeometryType
from cadenzaanalytics.data.measure_aggregation import MeasureAggregation
from cadenzaanalytics.data.parameter import Parameter
from cadenzaanalytics.data.parameter_type import ParameterType

from cadenzaanalytics.request.analytics_request import AnalyticsRequest
from cadenzaanalytics.request.request_metadata import RequestMetadata
from cadenzaanalytics.request.view_parameter import ViewParameter

from cadenzaanalytics.response.data_response import DataResponse
from cadenzaanalytics.response.enrichment_response import EnrichmentResponse
from cadenzaanalytics.response.missing_metadata_strategy import MissingMetadataStrategy
from cadenzaanalytics.response.image_response import ImageResponse
from cadenzaanalytics.response.text_response import TextResponse
from cadenzaanalytics.response.url_response import UrlResponse
from cadenzaanalytics.response.error_response import ErrorResponse

from cadenzaanalytics.version import __version__


# Logging configuration, format similar to gunicorn
dictConfig({
    'disable_existing_loggers': False,
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] [%(process)d] [%(levelname)s] [%(module)s] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S %z'
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': os.environ.get('CADENZAANALYTICS_LOG_LVL', 'INFO'),
        'handlers': ['wsgi']
    }
})
