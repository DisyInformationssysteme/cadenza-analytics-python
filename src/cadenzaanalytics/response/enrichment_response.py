from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.attribute_group import AttributeGroup
from cadenzaanalytics.request.request_table import RequestTable
from cadenzaanalytics.response.csv_response import CsvResponse
from cadenzaanalytics.response.missing_metadata_strategy import MissingMetadataStrategy


class EnrichmentResponse(CsvResponse):
    """A class representing an enrichment response from an extension.

    Parameters
    ----------
    CsvResponse : type
        The data response type from which EnrichmentResponse inherits.
    """
    def __init__(self,
                 data: DataFrame,
                 column_metadata: List[ColumnMetadata],
                 *,
                 missing_metadata_strategy: MissingMetadataStrategy = MissingMetadataStrategy.ADD_DEFAULT_METADATA):
        """Initialize an EnrichmentResponse instance.

        Parameters
        ----------
        data : DataFrame
            The data to be enriched. Must contain the id columns.
        column_metadata : List[ColumnMetadata]
            List of column metadata to be added.
        missing_metadata_strategy : MissingMetadataStrategy, optional
            Strategy to handle missing metadata, by default MissingMetadataStrategy.ADD_DEFAULT_METADATA.
            The REMOVE_DATA_COLUMNS strategy will remove non-id columns from the data frame unless they are
            specified in column_metadata. The ADD_DEFAULT_METADATA will add default metadata to
            all non-id columns that are missing in the column_metadata list.
        """
        super().__init__(data,
                         column_metadata=column_metadata,
                         missing_metadata_strategy=missing_metadata_strategy)

    def get_response(self, request_table: RequestTable = None):
        if request_table is None:
            raise ValueError("Enrichment responses need the request table for validating ids and handling missing ids.")
        self._validate_ids(request_table)
        return super().get_response(request_table)

    def _validate_ids(self, request_table: RequestTable):
        available_id_names = []
        for column in self._column_meta_data:
            if column.attribute_group_name == AttributeGroup.ID_ATTRIBUTE_GROUP_NAME:
                available_id_names.append(column.name)
                # ids explicitly defined must always be present in the data, independent of missing_metadata_strategy
                if column.name not in self._data.columns:
                    raise ValueError(f"Id column \"{column.name}\" specified in response column_meta"
                                     f" but such a column was not found in response data. Either add the column to"
                                     f" the data frame or remove it from the response column_meta.")
        expected_id_names = request_table.metadata.id_names
        if len(available_id_names) > 0 and set(available_id_names) != set(expected_id_names):
            # do not support mixed cases: if there are any ids in the response, they need to match the expectation
            raise ValueError(f"Expected id columns {expected_id_names} "
                             f"do not match id columns {available_id_names} specified in response column_meta.")
        # now either no id columns are defined, or they match the expected id columns
        if len(available_id_names) == 0:
            # none are defined, we always add them from the request metadata
            self._column_meta_data.extend(request_table.metadata.ids)
        columns_in_data = set(self._data.columns)
        for id_column in expected_id_names:
            if id_column not in columns_in_data:
                # Assumes column length matches one by one as only such kind of enrichment responses
                # are expected or supported, else this will throw an ValueError.
                # Changes in row order cannot be detected or managed here.
                self._data.loc[:, id_column] = request_table.data[id_column]
        # now we know that the result has the expected ids and that there is corresponding result data
