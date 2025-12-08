import collections
from typing import Iterator, List, Optional

from cadenzaanalytics.data.parameter_value import ParameterValue
from cadenzaanalytics.request.view_parameter import ViewParameter
from cadenzaanalytics.data.parameter_value_type import ParameterValueType


class RequestParameter(collections.abc.Mapping[str, ParameterValueType]):
    """Provides access to parameters from an analytics request.

    Supports dict-like access to parameter values via `params["name"]` syntax.
    Use `params.info("name")` to access the full ParameterValue object with metadata.
    """

    def __init__(self, request_parameters: List[dict]) -> None:
        """Initialize RequestParameter from a list of parameter dictionaries.

        Parameters
        ----------
        request_parameters : List[dict]
            List of parameter dictionaries from the Cadenza request.
        """
        self._request_parameters = {param["name"]: ParameterValue._from_dict(param) for param in request_parameters}

    @property
    def view(self) -> ViewParameter:
        """Returns the view parameters of the request.

        Returns
        -------
        ViewParameter
            View parameter of the request.
        """
        width = self._get_parameter_value(ViewParameter.VIEW_WIDTH_PARAMETER_NAME)
        height = self._get_parameter_value(ViewParameter.VIEW_HEIGHT_PARAMETER_NAME)
        device_pixel_ratio = self._get_parameter_value(ViewParameter.VIEW_DEVICE_PIXEL_RATIO_PARAMETER_NAME)

        return ViewParameter(
            width=width,
            height=height,
            device_pixel_ratio=device_pixel_ratio
        )

    def __getitem__(self, name: str) -> Optional[ParameterValueType]:
        parameter = self._get_parameter(name)
        if parameter is not None:
            return parameter.value
        raise KeyError(f"Parameter {name} not found.")

    def __iter__(self) -> Iterator[str]:
        return iter(self._request_parameters)

    def __len__(self) -> int:
        return len(self._request_parameters)

    def __contains__(self, name: str) -> bool:
        return name in self._request_parameters

    def info(self, name: str) -> Optional[ParameterValue]:
        """Get the full parameter object including metadata.

        Parameters
        ----------
        name : str
            The name of the parameter.

        Returns
        -------
        Optional[ParameterValue]
            The parameter object with value and metadata, or None if not found.
        """
        return self._get_parameter(name)

    def _get_parameter(self, name: str) -> Optional[ParameterValue]:
        """Returns a specific parameter object.

        Parameters
        ----------
        name : str
            The name of the parameter.

        Returns
        -------
        Optional[ParameterValue]
            The parameter object if found, else None.
        """

        if name in self._request_parameters:
            return self._request_parameters[name]
        return None


    def _get_parameter_value(self, name: str) -> Optional[ParameterValueType]:
        """Returns a specific parameter value.

        Parameters
        ----------
        name : str
            The name of the parameter.

        Returns
        -------
        Optional[ParameterValueType]
            The value of the parameter if found, else None.
        """

        if name in self._request_parameters:
            return self._request_parameters[name].value
        return None
