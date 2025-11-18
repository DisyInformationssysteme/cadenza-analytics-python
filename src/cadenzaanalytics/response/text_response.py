from cadenzaanalytics.response.extension_data_response import ExtensionDataResponse


class TextResponse(ExtensionDataResponse):
    """A class representing a text response from an extension.

    Parameters
    ----------
    ExtensionDataResponse : type
        The base extension data response type from which TextResponse inherits.
    """
    def __init__(self, text):
        content_type = 'text/plain'
        super().__init__(content_type)

        self._text = text

    def get_response(self):
        """Get the text response.

        Returns
        -------
        Response
            The text response.
        """
        return self._create_response(self._text)
