from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata


class ExtensionResponse:
    def get_response(self, original_column_metadata: List[ColumnMetadata], original_data: DataFrame):
        pass
