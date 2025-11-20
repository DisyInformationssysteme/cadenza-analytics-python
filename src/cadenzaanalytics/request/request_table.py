from typing import Callable, List

import pandas as pd
from pandas import DataFrame

from cadenzaanalytics.request.request_metadata import RequestMetadata
from cadenzaanalytics.response.missing_metadata_strategy import MissingMetadataStrategy
from cadenzaanalytics.response.enrichment_response import ColumnMetadata, EnrichmentResponse


class RequestTable:
    """A class representing an analytics request table.
    """
    def __init__(self, metadata: RequestMetadata, data: DataFrame):
        self._metadata = metadata
        self._data = data

    @property
    def metadata(self) -> RequestMetadata:
        """Get the metadata associated with the request.

        Returns
        -------
        RequestMetadata
            The metadata associated with the request.
        """
        return self._metadata

    @property
    def data(self) -> DataFrame:
        """Get the data payload of the request.

        Returns
        -------
        object
            The data associated with the request.
        """
        return self._data

    def to_enrichment(self, *,
                      new_columns: List[ColumnMetadata],
                      row_mapper: Callable[[pd.Series], pd.Series],
                      missing_metadata_strategy: MissingMetadataStrategy=MissingMetadataStrategy.ADD_DEFAULT_METADATA) \
            -> EnrichmentResponse:
        """Creates an enrichment response by adding the given new columns and applying the mapper
        on all data rows. This is a convenience method for creating enrichment responses where
        each input row is mapped to a single output row.

        :param new_columns: Description of the columns that are added as an enrichment to the cadenza objecttype.
        :param row_mapper: Takes a row (pandas series) and returns a row (pandas series). The returned series
        must have indices that correspond to the new_columns' names.
        :param missing_metadata_strategy: Description of the strategy to handle missing metadata.
        :return: An enrichment response.
        """
        result_data = self._data.apply(
            row_mapper,
            axis=1,
            result_type='expand'
        )
        id_names = self._metadata.id_names
        result_data[id_names] = self._data[id_names]

        return EnrichmentResponse(result_data,
                                  self._metadata.id_columns + new_columns,
                                  missing_metadata_strategy=missing_metadata_strategy)
