from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse


class UrlResponse(ExtensionDataResponse):
    """A class representing a url response from an extension.

    Parameters
    ----------
    ExtensionDataResponse : type
        The base extension data response type from which UrlResponse inherits.
    """
    def __init__(self, url):
        content_type = 'text/uri-list'
        super().__init__(content_type)

        self._url = url

    def get_response(self):
        """Get the url response.

        Returns
        -------
        Response
            The url response.
        """
        return self._create_response(self._url)
