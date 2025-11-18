from typing import List, Dict, Optional

from cadenzaanalytics.request.view_parameter import ViewParameter


class RequestParameter:
    """This class holds the parameters of the analytics request send by cadenza.
    """

    def __init__(self, request_metadata: dict):
        #TODO: Refactor
        self._request_parameters = request_metadata._request_metadata['parameters']


    @property
    def view(self) -> ViewParameter:
        """Returns the view parameters of the request.

        Returns
        -------
        ViewParameter
            View parameter of the request.
        """
        width = self._get_parameter(ViewParameter.VIEW_WIDTH_PARAMETER_NAME)
        height = self._get_parameter(ViewParameter.VIEW_HEIGHT_PARAMETER_NAME)
        device_pixel_ratio = self._get_parameter(ViewParameter.VIEW_DEVICE_PIXEL_RATIO_PARAMETER_NAME)

        return ViewParameter(
            width=int(width) if width is not None else None,
            height=int(height) if height is not None else None,
            device_pixel_ratio=float(device_pixel_ratio) if device_pixel_ratio is not None else None
        )


    def _get_parameter(self, name: str) -> Optional[str]:
        """Returns a specific parameter value.

        Parameters
        ----------
        name : str
            The name of the parameter.

        Returns
        -------
        str
            The value of the parameter if found, else an empty string.
        """

        if name in self._request_parameters:
            return self._request_parameters[name]
        return None