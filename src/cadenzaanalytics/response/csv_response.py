from typing import List, Optional
import logging

from flask import Response
from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.data_type import DataType
from cadenzaanalytics.request.request_table import RequestTable
from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse
from cadenzaanalytics.response.missing_metadata_strategy import MissingMetadataStrategy
from cadenzaanalytics.util import to_cadenza_csv

logger = logging.getLogger('cadenzaanalytics')


class CsvResponse(ExtensionDataResponse):
    """Base class for CSV-based responses from an analytics extension.

    Handles DataFrame to CSV conversion with metadata generation.
    """

    def __init__(self,
                 data: DataFrame,
                 column_metadata: List[ColumnMetadata],
                 *,
                 missing_metadata_strategy: MissingMetadataStrategy = MissingMetadataStrategy.ADD_DEFAULT_METADATA
                 ) -> None:
        """Initialize a CsvResponse.

        Parameters
        ----------
        data : DataFrame
            The response data as a pandas DataFrame.
        column_metadata : List[ColumnMetadata]
            Metadata describing the columns in the response.
        missing_metadata_strategy : MissingMetadataStrategy, optional
            Strategy for handling columns without metadata, by default ADD_DEFAULT_METADATA.
        """
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
    def runtime_validation_disabled(self, value: bool) -> None:
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
    def missing_metadata_strategy(self, value: MissingMetadataStrategy) -> None:
        """Setter for the strategy of handling missing metadata."""

        self._missing_metadata_strategy = value


    def get_response(self, request_table: Optional[RequestTable] = None) -> Response:
        """Get the CSV response.

        Parameters
        ----------
        request_table : Optional[RequestTable]
            The request table, used by enrichment responses for ID mapping.

        Returns
        -------
        Response
            Flask Response containing the CSV data.
        """
        leftover_metadata_column_names = self._apply_missing_metadata_strategy()
        self._validate_response(leftover_metadata_column_names)

        datetime_columns = [c.name for c in self._column_meta_data if c.data_type == DataType.ZONEDDATETIME]
        geometry_columns = [c.name for c in self._column_meta_data if c.data_type == DataType.GEOMETRY]
        float_columns = [c.name for c in self._column_meta_data if c.data_type == DataType.FLOAT64]
        int_columns = [c.name for c in self._column_meta_data if c.data_type == DataType.INT64]
        csv_data = to_cadenza_csv(self._data,
                                  datetime_columns=datetime_columns,
                                  geometry_columns=geometry_columns,
                                  float_columns=float_columns,
                                  int_columns=int_columns)
        return self._create_response(csv_data, self._column_meta_data)


    def _validate_response(self, leftover_metadata_column_names: List[str]) -> None:
        """Validate the response data and metadata.

        Parameters
        ----------
        leftover_metadata_column_names : List[str]
            Column names that have metadata but no corresponding data column.

        Raises
        ------
        ValueError
            If there are metadata definitions without data columns or no data columns exist.
        """
        if not self._is_runtime_validation_active:
            return
        # metadata definition without columns in data
        if len(leftover_metadata_column_names) > 0:
            raise ValueError(f"Metadata column definition without column in data found."
                            f"Missing columns: {leftover_metadata_column_names}")
        # empty data response
        if len(self._data.columns) == 0:
            raise ValueError("Response without any data column.")

    def _apply_missing_metadata_strategy(self) -> List[str]:
        """Apply the configured strategy for handling columns with missing metadata.

        Depending on the missing_metadata_strategy setting, this method will either:
        - ADD_DEFAULT_METADATA: Generate default metadata for columns without explicit metadata
        - REMOVE_DATA_COLUMNS: Remove data columns that have no metadata definition
        - RAISE_EXCEPTION: Raise a ValueError for columns without metadata

        Returns
        -------
        List[str]
            Names of metadata columns that have no corresponding data column.

        Raises
        ------
        ValueError
            If duplicate metadata definitions exist or if RAISE_ERROR strategy is used
            and columns without metadata are found.
        """
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
                            data_type=DataType.from_pandas_dtype(self._data[df_column_name].dtype)
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
