import csv
import sys
from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.attribute_role import AttributeRole
from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse
from cadenzaanalytics.response.missing_metadata_strategy import MissingMetadataStrategy


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
                 missing_metadata_strategy: MissingMetadataStrategy = MissingMetadataStrategy.ADD_DEFAULT_METADATA):

        content_type = 'text/csv'
        super().__init__(content_type)

        self._data = data
        self._column_meta_data = column_metadata

        self._is_runtime_validation_active = True
        self._missing_metadata_strategy = missing_metadata_strategy


    @property
    def disable_runtime_validation(self) -> bool:
        """Getter for toggle to disable the runtime validation of the response.
        The runtime validation is enabled by default.

        Returns
        -------
        bool
            Current setting of toggle
        """

        return not self._is_runtime_validation_active


    @disable_runtime_validation.setter
    def disable_runtime_validation(self, value: bool):
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


    def get_response(self, original_column_metadata: List[ColumnMetadata], original_data: DataFrame):
        """Get the CSV response.

        Returns
        -------
        Response
            The CSV response.
        """
        if self._is_runtime_validation_active:
            self._validate_response()


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


    def _validate_response(self):
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
                    #TODO: Add logging entry when this option is executed
                    self._column_meta_data.append(
                        ColumnMetadata(
                            name=df_column_name,
                            print_name=df_column_name,
                            data_type=DataType.from_pandas_dtype(self._data[df_column_name].dtype),
                            role=AttributeRole.DIMENSION
                        )
                    )
                elif self._missing_metadata_strategy == MissingMetadataStrategy.REMOVE_DATA_COLUMNS:
                    #TODO: Add logging entry when this option is executed
                    self._data.drop(df_column_name, axis=1, inplace=True)
                else:
                    raise ValueError(f"Metadata definition for column \"{df_column_name}\" is missing.")

        # metadata definition without columns in data
        if len(metadata_column_names) > 0:
            raise ValueError(f"Metadata column definition without column in data found."
                            f"Number of missing columns: {len(metadata_column_names)}")

        # empty data response
        if len(self._data.columns) == 0:
            raise ValueError("Response without any data column.")
