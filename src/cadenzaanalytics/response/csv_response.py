import csv
import sys
from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse


class CsvResponse(ExtensionDataResponse):
    """A class representing a CSV response from an extension.

    Parameters
    ----------
    ExtensionDataResponse : type
        The base extension data response type from which CsvResponse inherits.
    """
    def __init__(self, data: DataFrame, column_metadata: List[ColumnMetadata]):
        content_type = 'text/csv'
        super().__init__(content_type)

        self._data = data
        self._column_meta_data = column_metadata

    def get_response(self, original_column_metadata: List[ColumnMetadata], original_data: DataFrame):
        """Get the CSV response.

        Returns
        -------
        Response
            The CSV response.
        """
        python_3_12 = (3, 12)
        if sys.version_info >= python_3_12:
            csv_data = self._data.to_csv(
                sep=';',
                encoding='utf-8',
                quoting=csv.QUOTE_NOTNULL,
                index=False,
                na_rep=None,  # missing/None/Null values are sent without quotes
                quotechar='"',
                lineterminator='\r\n')
        else:
            csv_data = self._data.to_csv(
                sep=';',
                encoding='utf-8',
                quoting=csv.QUOTE_ALL,
                index=False,
                quotechar='"',
                lineterminator='\r\n')
            # Needed to make sure we sent NULL/None values and not empty strings.
            # This replacement might be problematic for escaped quotes within a string.
            # As the proper solution is to use python 3.12,
            # we do not support more sophisticated support for missing values here.
            csv_data = csv_data.replace('""', '')

        return self._create_response(csv_data, self._column_meta_data)
