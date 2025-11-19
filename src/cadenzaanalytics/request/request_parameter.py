from typing import Optional, Any

from cadenzaanalytics.data.parameter_value import ParameterValue
from cadenzaanalytics.request.view_parameter import ViewParameter


class RequestParameter:
    """This class holds the parameters of the analytics request send by cadenza.
    """

    def __init__(self, request_parameters: dict):
        self._request_parameters = {param["name"]: ParameterValue._from_dict(param) for param in request_parameters}


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
            width=width,
            height=height,
            device_pixel_ratio=device_pixel_ratio
        )

    def __getitem__(self, name: str) -> Any:
        return self._get_parameter(name)


    def _get_parameter(self, name: str) -> Any:
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
            return self._request_parameters[name].value
        return None
