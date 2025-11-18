from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata


class ExtensionResponse:
    """A class representing a response from an extension.
    """
    def get_response(self):
        """Get the response from the extension.
        """
