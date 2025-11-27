import csv
import re
import sys
from typing import List
import logging

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.attribute_role import AttributeRole
from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.request.request_table import RequestTable
from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse
from cadenzaanalytics.response.missing_metadata_strategy import MissingMetadataStrategy

logger = logging.getLogger('cadenzaanalytics')


class CsvResponse(ExtensionDataResponse):
    """A class representing a CSV response from an extension.

    Parameters
    ----------
    ExtensionDataResponse : type
        The base extension data response type from which CsvResponse inherits.
    """
    def __init__(self,
                 data: DataFrame,
                 column_metadata: List[ColumnMetadata],
                 *,
                 missing_metadata_strategy: MissingMetadataStrategy = MissingMetadataStrategy.ADD_DEFAULT_METADATA):

        content_type = 'text/csv'
        super().__init__(content_type)
        # copy data to avoid side effects and allow safely extending data with missing id columns
        self._data = data.copy()
        self._column_meta_data = list(column_metadata)
        self._is_runtime_validation_active = True
        self._missing_metadata_strategy = missing_metadata_strategy


    @property
    def runtime_validation_disabled(self) -> bool:
        """Getter for toggle to disable the runtime validation of the response.
        The runtime validation is enabled by default.

        Returns
        -------
        bool
            Current setting of toggle
        """

        return not self._is_runtime_validation_active


    @runtime_validation_disabled.setter
    def runtime_validation_disabled(self, value: bool):
        """Setter for toggle to disable the runtime validation of the response.
        Set to True to disable the runtime validation.
        """

        self._is_runtime_validation_active = not value


    @property
    def missing_metadata_strategy(self) -> MissingMetadataStrategy:
        """Getter for the strategy of handling missing metadata.

        Returns
        -------
        MissingMetadataStrategy
            Current missing metadata strategy
        """

        return self._missing_metadata_strategy


    @missing_metadata_strategy.setter
    def missing_metadata_strategy(self, value: MissingMetadataStrategy):
        """Setter for the strategy of handling missing metadata."""

        self._missing_metadata_strategy = value


    def get_response(self, request_table: RequestTable = None):
        """Get the CSV response.

        Returns
        -------
        Response
            The CSV response.
        """
        leftover_metadata_column_names = self.apply_missing_metadata_strategy()
        self._validate_response(leftover_metadata_column_names)

        python_3_12 = (3, 12)
        if sys.version_info >= python_3_12 and len(self._data.columns) > 1:
            # The quoting strategies QUOTE_NOTNULL or QUOTE_NULL would fail with the csv writer
            # error "single empty field record must be quoted"
            # if there is only one column and if there is any null-ish value available.
            # Also refer to https://github.com/pandas-dev/pandas/issues/59116
            # Thus we can only use this strategy if there is more than one column, else fallback to
            # the fallback approach that always quotes and then removes quotes again.
            # The limitation to python 3.12 comes from the option QUOTE_NOTNULL only becoming available on that version.
            csv_data = self._data.to_csv(
                sep=';',
                encoding='utf-8',
                quoting=csv.QUOTE_NOTNULL,
                index=False,
                na_rep=None,  # missing/None/Null values are sent without quotes
                quotechar='"',
                lineterminator='\r\n',
                date_format='%Y-%m-%dT%H:%M:%SZ')
        else:
            # info: this approach cannot distinguish empty strings from NULL
            csv_data = self._data.to_csv(
                sep=';',
                encoding='utf-8',
                quoting=csv.QUOTE_ALL,
                index=False,
                quotechar='"',
                lineterminator='\r\n',
                date_format='%Y-%m-%dT%H:%M:%SZ')
            # Needed to make sure to send NULL/None values (unquoted empty content) and not empty strings
            # (quoted empty content)
            # as empty strings would only be valid for DataType.STRING and cause errors for other DataTypes.
            # regex searches and replaces double quotes that are surrounded by separators
            # (start file, end file, semicolon or newline)
            # this way double-quotes that represent a single escaped quote character within a string value are retained
            csv_data = re.sub(r'(^|;|\r\n)""(?=;|\r\n|$)', r'\1', csv_data)
        return self._create_response(csv_data, self._column_meta_data)


    def _validate_response(self, leftover_metadata_column_names: List[str]):
        if not self._is_runtime_validation_active:
            return
        # metadata definition without columns in data
        if len(leftover_metadata_column_names) > 0:
            raise ValueError(f"Metadata column definition without column in data found."
                            f"Missing columns: {leftover_metadata_column_names}")
        # empty data response
        if len(self._data.columns) == 0:
            raise ValueError("Response without any data column.")

    def apply_missing_metadata_strategy(self):
        metadata_column_names = {}

        # prepare dictionary of metadata column name for fast lookup
        for column in self._column_meta_data:
            if column.name not in metadata_column_names:
                metadata_column_names[column.name] = column.name
            else:
                raise ValueError(f"Metadata for column \"{column.name}\" is already defined.")

        for df_column_name in list(self._data):
            if df_column_name in metadata_column_names:
                metadata_column_names.pop(df_column_name)
            else:
                # missing metadata for column
                if self._missing_metadata_strategy == MissingMetadataStrategy.ADD_DEFAULT_METADATA:
                    logger.info('Missing metadata for column "%s": '
                                'Column metadata has been added to response. '
                                'missing_metadata_strategy=%s', df_column_name, self._missing_metadata_strategy.name)

                    self._column_meta_data.append(
                        ColumnMetadata(
                            name=df_column_name,
                            print_name=df_column_name,
                            data_type=DataType.from_pandas_dtype(self._data[df_column_name].dtype),
                            role=AttributeRole.DIMENSION
                        )
                    )
                elif self._missing_metadata_strategy == MissingMetadataStrategy.REMOVE_DATA_COLUMNS:
                    logger.info('Missing metadata for column "%s": '
                                'Column has been removed from response. '
                                'missing_metadata_strategy=%s', df_column_name, self._missing_metadata_strategy.name)

                    self._data.drop(df_column_name, axis=1, inplace=True)
                else:
                    raise ValueError(f"Metadata definition for column \"{df_column_name}\" is missing.")
        return list(metadata_column_names.keys())
