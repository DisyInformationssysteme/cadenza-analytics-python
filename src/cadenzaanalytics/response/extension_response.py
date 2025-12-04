from typing import Optional

from flask import Response

from cadenzaanalytics.request.request_table import RequestTable


class ExtensionResponse:
    """Base class representing a response from an analytics extension.

    Subclasses implement specific response types such as data, image, text, or error responses.
    """

    def get_response(self, request_table: Optional[RequestTable] = None) -> Response:
        """Get the response from the extension.

        This method is internal to cadenzaanalytics and must not be called by client code.

        Parameters
        ----------
        request_table : Optional[RequestTable]
            The request table, required for enrichment responses to map IDs.

        Returns
        -------
        Response
            Flask Response object with appropriate content type and data.
        """
