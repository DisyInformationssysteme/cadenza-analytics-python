from typing import Optional


class ViewParameter:
    """View parameters for visual analytics extensions.

    Contains dimensions and pixel ratio for extensions displayed as Cadenza workbook views.
    These parameters are only available for VISUAL extension types.
    """

    VIEW_WIDTH_PARAMETER_NAME = 'net.disy.cadenza.imageWidth'
    VIEW_HEIGHT_PARAMETER_NAME = 'net.disy.cadenza.imageHeight'
    VIEW_DEVICE_PIXEL_RATIO_PARAMETER_NAME = 'net.disy.cadenza.devicePixelRatio'

    def __init__(self, width: Optional[int], height: Optional[int], device_pixel_ratio: Optional[float]) -> None:
        """Initialize view parameters.

        Parameters
        ----------
        width : Optional[int]
            View width in pixels.
        height : Optional[int]
            View height in pixels.
        device_pixel_ratio : Optional[float]
            Device pixel ratio for high-DPI displays.
        """
        self._width = width
        self._height = height
        self._device_pixel_ratio = device_pixel_ratio

    @property
    def width(self) -> Optional[int]:
        """Get the view width.

        Returns
        -------
        Optional[int]
            View width in pixels, or None if not provided.
        """
        return self._width

    @property
    def height(self) -> Optional[int]:
        """Get the view height.

        Returns
        -------
        Optional[int]
            View height in pixels, or None if not provided.
        """
        return self._height

    @property
    def device_pixel_ratio(self) -> Optional[float]:
        """Get the device pixel ratio.

        Returns
        -------
        Optional[float]
            Device pixel ratio for high-DPI displays, or None if not provided.
        """
        return self._device_pixel_ratio
