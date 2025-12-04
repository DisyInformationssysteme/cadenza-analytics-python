from typing import Optional

from flask import Response

from cadenzaanalytics.request.request_table import RequestTable
from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse


class TextResponse(ExtensionDataResponse):
    """A response containing plain text from an analytics extension."""

    def __init__(self, text: str) -> None:
        """Initialize a TextResponse.

        Parameters
        ----------
        text : str
            Text content to return.
        """
        content_type = 'text/plain;charset=utf-8'
        super().__init__(content_type)

        self._text = text

    def get_response(self, request_table: Optional[RequestTable] = None) -> Response:
        """Get the text response.

        Parameters
        ----------
        request_table : Optional[RequestTable]
            Not used for text responses.

        Returns
        -------
        Response
            Flask Response containing the text content.
        """
        return self._create_response(self._text)
