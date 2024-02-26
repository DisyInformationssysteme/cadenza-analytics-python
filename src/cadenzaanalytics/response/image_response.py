from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse


class ImageResponse(ExtensionDataResponse):
    def __init__(self, image):
        content_type = 'image/png'
        super().__init__(content_type)

        self._image = image

    def get_response(self):
        return self._create_response(self._image)
