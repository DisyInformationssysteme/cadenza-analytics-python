import json
from typing import List

from flask import Response
from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.response.extension_response import ExtensionResponse


class ErrorResponse(ExtensionResponse):
    """A class representing an error response from an extension.

    Parameters
    ----------
    ExtensionResponse : type
        The base extension response type from which ErrorResponse inherits.
    """   
    def __init__(self, message: str, status: int = 400):
        self._message = message
        self._status = status

    def get_response(self, original_column_metadata: List[ColumnMetadata], original_data: DataFrame):
        """Get the error response.

        Returns
        -------
        Response
            The error response.
        """        
        return self._create_response(self._message)

    def _get_response_json(self, message: str):
        error_message = {
            "message": message
        }

        return json.dumps(error_message, default=str)

    def _create_response(self, message: str):
        return Response(response=self._get_response_json(message), status=self._status, mimetype="application/json")
