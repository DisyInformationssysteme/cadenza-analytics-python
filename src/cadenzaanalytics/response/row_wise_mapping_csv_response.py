from typing import Callable, List

from pandas import DataFrame, Series

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.response.error_response import ErrorResponse
from cadenzaanalytics.response.csv_response import CsvResponse
from cadenzaanalytics.data.attribute_group import KEY_ATTRIBUTE_GROUP_NAME
from cadenzaanalytics.response.extension_response import ExtensionResponse


class RowWiseMappingCsvResponse(ExtensionResponse):
    def __init__(self, response_columns: List[ColumnMetadata], row_mapper: Callable, closure: Callable=None):
        self._response_columns = response_columns
        self._row_mapper = row_mapper
        self._closure = closure

    def get_response(self, original_column_metadata: List[ColumnMetadata], original_data: DataFrame):
        key_attribute_columns = [c for c in original_column_metadata
                                 if c.attribute_group_name == KEY_ATTRIBUTE_GROUP_NAME]
        key_attribute_column_names = [c.name for c in key_attribute_columns]
        truncated_original_data = original_data.drop(key_attribute_column_names, axis=1)
        result_data = truncated_original_data.apply(self._apply_and_wrap, axis=1)
        if len(self._response_columns) != len(result_data.columns):
            return ErrorResponse(
                f"Expected  {len(result_data.columns)} response columns but got {len(self._response_columns)}", 500)
        extended_result_data = result_data.join(original_data.loc[:, key_attribute_column_names])
        csv_response = CsvResponse(extended_result_data, self._response_columns + key_attribute_columns)
        response = csv_response.get_response(original_column_metadata, original_data)
        if self._closure is not None:
            self._closure(result_data)
        return response

    def _apply_and_wrap(self, row):
        mapped_row = self._row_mapper(row)
        if isinstance(mapped_row, Series):
            return mapped_row
        return Series(mapped_row, index=[c.name for c in self._response_columns])
