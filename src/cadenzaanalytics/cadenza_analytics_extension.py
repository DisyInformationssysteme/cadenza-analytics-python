"""Represents a disy Cadenza analytics extension and holds its configuration. In conenction with the
`cadenza anayltics extension service` the extension handels the processing of analytics requests, when
invoked via HTTP POST on the relative path."""
import json
from io import StringIO
from typing import Callable, List

import pandas as pd
from flask import Response, request

from cadenzaanalytics.data.analytics_extension import AnalyticsExtension
from cadenzaanalytics.data.attribute_group import AttributeGroup
from cadenzaanalytics.data.extension_type import ExtensionType
from cadenzaanalytics.data.parameter import Parameter
from cadenzaanalytics.request.analytics_request import AnalyticsRequest
from cadenzaanalytics.request.request_metadata import RequestMetadata
from cadenzaanalytics.response.extension_response import ExtensionResponse


class CadenzaAnalyticsExtension:
    """Class representing a Cadenza analytics extension.
    """
    def __init__(self,
                 relative_path: str,
                 analytics_function: Callable[[RequestMetadata, pd.DataFrame], ExtensionResponse],
                 print_name: str,
                 extension_type: ExtensionType,
                 attribute_groups: List[AttributeGroup],
                 parameters: List[Parameter] = None):
        self._relative_path = relative_path
        self._analytics_function = analytics_function

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

        analytics_response = self._analytics_function(analytics_request.metadata, analytics_request.data)

        return analytics_response.get_response(analytics_request.metadata.get_columns(), analytics_request.data)

    def get_capabilities(self) -> Response:
        """Get the capabilities of the extension.

        Returns
        -------
        Response
            The capabilities of the extension.
        """
        return Response(response=self._analytics_extension.to_json(), status=200, mimetype="application/json")

    def _get_request_data(self, multipart_request) -> AnalyticsRequest:
        metadata_dict = json.loads(self._get_from_request(multipart_request, 'metadata'))
        metadata = RequestMetadata(metadata_dict)

        if metadata.has_columns():
            type_mapping = {}
            for column in metadata.get_columns():
                type_mapping[column.name] = column.data_type.pandas_type()
            csv_data = StringIO(self._get_from_request(multipart_request, 'data'))
            df_data = pd.read_csv(csv_data, sep=";", dtype=type_mapping)
        else:
            df_data = pd.DataFrame()

        return AnalyticsRequest(metadata, df_data)

    def _get_from_request(self, multipart_request, part_name):
        return multipart_request.form[part_name] if part_name in multipart_request.form else multipart_request.files[part_name].read().decode('UTF-8')
