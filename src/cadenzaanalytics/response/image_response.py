from typing import Optional

from flask import Response

from cadenzaanalytics.request.request_table import RequestTable
from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse


class ImageResponse(ExtensionDataResponse):
    """A response containing a PNG image from an analytics extension."""

    def __init__(self, image: bytes) -> None:
        """Initialize an ImageResponse.

        Parameters
        ----------
        image : bytes
            PNG image data as bytes.
        """
        content_type = 'image/png'
        super().__init__(content_type)

        self._image = image

    def get_response(self, request_table: Optional[RequestTable] = None) -> Response:
        """Get the image response.

        Parameters
        ----------
        request_table : Optional[RequestTable]
            Not used for image responses.

        Returns
        -------
        Response
            Flask Response containing the PNG image.
        """
        return self._create_response(self._image)
