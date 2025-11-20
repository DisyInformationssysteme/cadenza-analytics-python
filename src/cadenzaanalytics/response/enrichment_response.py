from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.data.attribute_group import AttributeGroup
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
                 *,
                 column_metadata: List[ColumnMetadata],
                 id_columns: List[ColumnMetadata],
                 missing_metadata_strategy: MissingMetadataStrategy = MissingMetadataStrategy.ADD_DEFAULT_METADATA):
        """Initialize an EnrichmentResponse instance.

        Parameters
        ----------
        data : DataFrame
            The data to be enriched. Must contain the id columns.
        column_metadata : List[ColumnMetadata]
            List of column metadata to be added. Must not contain id columns.
        id_columns : List[ColumnMetadata]
            List of identifier columns. Must be equal to table.metadata.id_columns. Id columns are
            required for executing an enrichment.
        missing_metadata_strategy : MissingMetadataStrategy, optional
            Strategy to handle missing metadata, by default MissingMetadataStrategy.ADD_DEFAULT_METADATA.
            The REMOVE_DATA_COLUMNS strategy will remove non-id columns from the data frame unless they are
            specified in column_metadata. The ADD_DEFAULT_METADATA will add default metadata to
            all non-id columns that are missing in the column_metadata list.
        """
        self._id_columns = id_columns
        super().__init__(data,
                         column_metadata=column_metadata + id_columns,
                         missing_metadata_strategy=missing_metadata_strategy)
        self._validate_ids(column_metadata)


    def _validate_ids(self, column_metadata: List[ColumnMetadata]):
        has_id_column_defined = False

        for column in self._id_columns:
            if column.attribute_group_name == AttributeGroup.ID_ATTRIBUTE_GROUP_NAME:
                has_id_column_defined = True
            else:
                raise ValueError(f"Identifier column \"{column.name}\" is not an id attribute.")
            if column.name not in self._data.columns:
                raise ValueError(f"Identifier column \"{column.name}\" not found in response data.")

        if not has_id_column_defined:
            raise ValueError("Identifier column missing in metadata definition. This is mandatory for an enrichment.")

        if any(column.attribute_group_name == AttributeGroup.ID_ATTRIBUTE_GROUP_NAME for column in column_metadata):
            raise ValueError("Found identifier column in column_metadata list. "
                             "Identifier column must be defined in id_columns.")
