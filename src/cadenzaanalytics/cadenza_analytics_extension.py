"""Represents a disy Cadenza analytics extension and holds its configuration. In conenction with the
`cadenza anayltics extension service` the extension handels the processing of analytics requests, when
invoked via HTTP POST on the relative path."""
import json
import logging
from io import StringIO
from typing import Callable, List

import numpy as np
import pandas as pd
from flask import Response, request
from shapely import from_wkt

from cadenzaanalytics.data.analytics_extension import AnalyticsExtension
from cadenzaanalytics.data.extension_type import ExtensionType
from cadenzaanalytics.data.parameter import Parameter
from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.data.table import Table
from cadenzaanalytics.request.analytics_request import AnalyticsRequest
from cadenzaanalytics.request.request_parameter import RequestParameter
from cadenzaanalytics.request.request_metadata import RequestMetadata
from cadenzaanalytics.request.request_table import RequestTable
from cadenzaanalytics.response.extension_response import ExtensionResponse


logger = logging.getLogger('cadenzaanalytics')


class CadenzaAnalyticsExtension:
    """Class representing a Cadenza analytics extension, the central object to create for and register
    in the CadenzaAnalyticsExtensionService.
    """
    def __init__(self, *,
                 relative_path: str,
                 analytics_function: Callable[[AnalyticsRequest], ExtensionResponse],
                 print_name: str,
                 extension_type: ExtensionType,
                 tables: List[Table] = None,
                 parameters: List[Parameter] = None):

        self._relative_path = relative_path
        self._analytics_function = analytics_function

        attribute_groups = []
        if tables is None:
            tables = []
        if len(tables) > 1:
            raise ValueError('At most one table is supported')
        if len(tables) == 1:
            attribute_groups = tables[0].attribute_groups
            self._table_name = tables[0].name
        else:
            self._table_name = None
        self._analytics_extension = AnalyticsExtension(print_name, extension_type, attribute_groups, parameters)


    @property
    def relative_path(self) -> str:
        """Getter for the relative path of the extension.

        Returns
        -------
        str
            The relative path of the extension.
        """
        return self._relative_path

    @property
    def print_name(self) -> str:
        """Getter for the printable name of the extension.

        Returns
        -------
        str
            The printable name of the extension.
        """
        return self._analytics_extension.print_name

    @property
    def extension_type(self) -> ExtensionType:
        """Getter for the type of the extension.

        Returns
        -------
        str
            The type of the extension.
        """
        return self._analytics_extension.extension_type

    def handle_request(self) -> Response:
        """Handle the processing of extension requests.

        Returns
        -------
        Response
            The response to the request.
        """
        analytics_request = self._get_request_data(request)

        analytics_response = self._analytics_function(analytics_request)

        request_table = analytics_request[self._table_name] if self._table_name in analytics_request else None
        return analytics_response.get_response(request_table=request_table)

    def get_capabilities(self) -> Response:
        """Get the capabilities of the extension.

        Returns
        -------
        Response
            The capabilities of the extension.
        """
        return Response(response=self._analytics_extension.to_json(), status=200, mimetype="application/json")

    def _get_request_data(self, multipart_request) -> AnalyticsRequest:
        logger.info('Processing POST request...')

        metadata_dict = json.loads(self._get_from_request(multipart_request, 'metadata'))
        logger.debug('Received metadata:\n%s', metadata_dict)

        metadata = RequestMetadata(metadata_dict)
        parameters = RequestParameter(metadata_dict['parameters'])

        if len(metadata.columns) > 0:
            has_data = True
            type_mapping = {}
            na_values_mapping = {}
            datetime_columns = []
            geometry_columns = []

            for column in metadata.columns:
                if column.data_type == DataType.ZONEDDATETIME:
                    datetime_columns.append(column.name)
                    # must be empty list, otherwise pd.read_csv interprets empty strings as NA which
                    # is rejected by the parse_dates mechanism before it reaches the _parse_datetime function
                    na_values_mapping[column.name] = []
                elif column.data_type == DataType.STRING:
                    # only empty strings must be considered as NA
                    # unfortunately there does not seem to be a way to interpret empty quotes as empty string
                    # and unquoted as None
                    na_values_mapping[column.name] = ['']
                else:
                    # pandas default list of NA values, mostly relevant for numeric columns
                    na_values_mapping[column.name] = ['-1.#IND', '1.#QNAN', '1.#IND', '-1.#QNAN', '#N/A N/A',
                                                      '#N/A', 'N/A', 'n/a', 'NA', '<NA>', '#NA', 'NULL', 'null',
                                                      'NaN', '-NaN', 'nan', '-nan', 'None', '']

                if column.data_type == DataType.GEOMETRY:
                    geometry_columns.append(column.name)

                type_mapping[column.name] = column.data_type.pandas_type()

            csv_data = StringIO(self._get_from_request(multipart_request, 'data'))
            # read_csv cannot distinguish None from empty strings
            df_data = pd.read_csv(
                csv_data,
                sep=';',
                dtype=type_mapping,
                parse_dates=datetime_columns,
                date_format='ISO8601',
                na_values=na_values_mapping,
                keep_default_na=False,
            )

            # Parse WKT geometries into shapely geometry objects using vectorized from_wkt
            for gcol in geometry_columns:
                values = df_data[gcol].to_numpy()
                # from_wkt handles None values; replace empty strings with None
                values = np.where((values == '') | pd.isna(values), None, values)
                df_data[gcol] = from_wkt(values, on_invalid='warn')

            logger.debug('Received data:\n%s', df_data.head())
        else:
            has_data = False
            df_data = None
            logger.debug('Received request without data')

        analytics_request = AnalyticsRequest(parameters, cadenza_version=request.headers.get("X-Disy-Cadenza-Version"))
        if has_data:
            analytics_request[self._table_name] = RequestTable(df_data, metadata)

        return analytics_request

    def _get_from_request(self, multipart_request, part_name):
        if part_name in multipart_request.form:
            return multipart_request.form[part_name]
        return multipart_request.files[part_name].read().decode('UTF-8')
