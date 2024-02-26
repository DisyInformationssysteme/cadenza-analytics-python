from pandas import DataFrame
import csv

from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse
from cadenzaanalytics.data.column_metadata import ColumnMetadata


class CsvResponse(ExtensionDataResponse):
    def __init__(self, data: DataFrame, column_metadata: list[ColumnMetadata]):
        content_type = 'text/csv'
        super().__init__(content_type)

        self._data = data
        self._column_meta_data = column_metadata

    def get_response(self):
        csv_data = self._data.to_csv(
            sep=';',
            encoding='utf-8',
            quoting=csv.QUOTE_ALL,
            index=False,
            quotechar='"',
            lineterminator='\r\n')

        return self._create_response(csv_data, self._column_meta_data)
