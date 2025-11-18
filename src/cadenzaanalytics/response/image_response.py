from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse


class ImageResponse(ExtensionDataResponse):
    """A class representing an image response from an extension.

    Parameters
    ----------
    ExtensionDataResponse : type
        The base extension data response type from which ImageResponse inherits.
    """
    def __init__(self, image):
        content_type = 'image/png'
        super().__init__(content_type)

        self._image = image

    def get_response(self):
        """Get the image response.

        Returns
        -------
        Response
            The image response.
        """
        return self._create_response(self._image)
