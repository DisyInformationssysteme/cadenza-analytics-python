from typing import Optional

from flask import Response

from cadenzaanalytics.request.request_table import RequestTable
from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse


class UrlResponse(ExtensionDataResponse):
    """A response containing a URL redirect from an analytics extension."""

    def __init__(self, url: str) -> None:
        """Initialize a UrlResponse.

        Parameters
        ----------
        url : str
            URL to redirect to.
        """
        content_type = 'text/uri-list'
        super().__init__(content_type)

        self._url = url

    def get_response(self, request_table: Optional[RequestTable] = None) -> Response:
        """Get the URL response.

        Parameters
        ----------
        request_table : Optional[RequestTable]
            Not used for URL responses.

        Returns
        -------
        Response
            Flask Response containing the URL.
        """
        return self._create_response(self._url)
