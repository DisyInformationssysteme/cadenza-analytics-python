import json
from typing import Optional

from flask import Response

from cadenzaanalytics.request.request_table import RequestTable
from cadenzaanalytics.response.extension_response import ExtensionResponse


class ErrorResponse(ExtensionResponse):
    """A response representing an error from an analytics extension."""

    def __init__(self, message: str, status: int = 400) -> None:
        """Initialize an ErrorResponse.

        Parameters
        ----------
        message : str
            Error message to return.
        status : int, optional
            HTTP status code, by default 400.
        """
        self._message = message
        self._status = status

    def get_response(self, request_table: Optional[RequestTable] = None) -> Response:
        """Get the error response.

        Parameters
        ----------
        request_table : Optional[RequestTable]
            Not used for error responses.

        Returns
        -------
        Response
            Flask Response containing the error message as JSON.
        """
        return self._create_response(self._message)

    def _get_response_json(self, message: str) -> str:
        error_message = {
            "message": message
        }

        return json.dumps(error_message, default=str)

    def _create_response(self, message: str) -> Response:
        return Response(response=self._get_response_json(message), status=self._status, mimetype="application/json")
