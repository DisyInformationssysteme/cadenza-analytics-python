from typing import Callable, List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.response.error_response import ErrorResponse
from cadenzaanalytics.response.csv_response import CsvResponse
from cadenzaanalytics.data.attribute_group import KEY_ATTRIBUTE_GROUP_NAME
from cadenzaanalytics.response.extension_response import ExtensionResponse


class RowWiseMappingCsvResponse(ExtensionResponse):
    def __init__(self, response_columns: List[ColumnMetadata], row_mapper: Callable):
        self._response_columns = response_columns
        self._row_mapper = row_mapper

    def get_response(self, original_column_metadata: List[ColumnMetadata], original_data: DataFrame):
        key_attribute_columns = [c for c in original_column_metadata
                                 if c.attribute_group_name == KEY_ATTRIBUTE_GROUP_NAME]
        key_attribute_column_names = [c.name for c in key_attribute_columns]
        truncated_original_data = original_data.drop(key_attribute_column_names, axis=1)
        result_data = truncated_original_data.apply(self._row_mapper, axis=1)
        if len(self._response_columns) != len(result_data.columns):
            return ErrorResponse(
                f"Expected  {len(result_data.columns)} response columns but got {len(self._response_columns)}", 500)
        extended_result_data = result_data.join(original_data.loc[:, key_attribute_column_names])
        csv_response = CsvResponse(extended_result_data, self._response_columns + key_attribute_columns)
        return csv_response.get_response(original_column_metadata, original_data)