"""Represents a disy Cadenza analytics extension that is accessible via disy Cadenza at entry points
 depending on the extension type. The extension will run its main analytics function when invoked
 with a POST on the relative path."""
import json
from io import StringIO
from typing import Callable
import pandas as pd
from flask import Response, request

from cadenzaanalytics.data.analytics_extension import AnalyticsExtension
from cadenzaanalytics.data.extension_type import ExtensionType
from cadenzaanalytics.data.attribute_group import AttributeGroup
from cadenzaanalytics.data.parameter import Parameter
from cadenzaanalytics.request.analytics_request import AnalyticsRequest
from cadenzaanalytics.request.request_metadata import RequestMetadata
from cadenzaanalytics.response.extension_response import ExtensionResponse


class CadenzaAnalyticsExtension:
    def __init__(self,
                 relative_path: str,
                 analytics_function: Callable[[RequestMetadata, pd.DataFrame], ExtensionResponse],
                 print_name: str,
                 extension_type: ExtensionType,
                 attribute_groups: list[AttributeGroup],
                 parameters: list[Parameter] = None):
        self._relative_path = relative_path
        self._analytics_function = analytics_function

        self._analytics_extension = AnalyticsExtension(print_name, extension_type, attribute_groups, parameters)

    @property
    def relative_path(self) -> str:
        return self._relative_path

    @property
    def print_name(self) -> str:
        return self._analytics_extension.print_name

    @property
    def extension_type(self) -> ExtensionType:
        return self._analytics_extension.extension_type

    def handle_request(self) -> Response:
        analytics_request = self._get_request_data(request)

        analytics_response = self._analytics_function(analytics_request.metadata, analytics_request.data)

        return analytics_response.get_response()

    def get_capabilities(self) -> Response:
        return Response(response=self._analytics_extension.to_json(), status=200,  mimetype="application/json")

    def _get_request_data(self, multipart_request) -> AnalyticsRequest:
        metadata_dict = json.loads(multipart_request.form['metadata'])
        metadata = RequestMetadata(metadata_dict)

        if metadata.has_columns():
            csv_data = StringIO(multipart_request.form['data'])
            df_data = pd.read_csv(csv_data, sep=";")
        else:
            df_data = pd.DataFrame()

        return AnalyticsRequest(metadata, df_data)
