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
                 data: DataFrame, column_metadata: List[ColumnMetadata],
                 missing_metadata_strategy: MissingMetadataStrategy = MissingMetadataStrategy.ADD_DEFAULT_METADATA):

        super().__init__(data, column_metadata, missing_metadata_strategy)


    def _validate_response(self):
        has_id_column_defined = False

        for column in self._column_meta_data:
            if column.attribute_group_name == AttributeGroup.ID_ATTRIBUTE_GROUP_NAME:
                has_id_column_defined = True

        if not has_id_column_defined:
            raise ValueError("Identifier column missing in metadata definition. This is mandatory for an enrichment.")
        super()._validate_response()