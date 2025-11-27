from cadenzaanalytics.request.request_table import RequestTable


class ExtensionResponse:
    """A class representing a response from an extension.
    """
    def get_response(self, request_table: RequestTable = None):
        """Get the response from the extension. The interface of this method is internal to cadenzaanalytics
        and must not be called or used by client code.
        """
