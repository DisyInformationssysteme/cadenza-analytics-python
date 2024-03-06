from typing import List

from pandas import DataFrame

from cadenzaanalytics.data.column_metadata import ColumnMetadata
from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse


class ImageResponse(ExtensionDataResponse):
    def __init__(self, image):
        content_type = 'image/png'
        super().__init__(content_type)

        self._image = image

    def get_response(self, original_column_metadata: List[ColumnMetadata], original_data: DataFrame):
        return self._create_response(self._image)
