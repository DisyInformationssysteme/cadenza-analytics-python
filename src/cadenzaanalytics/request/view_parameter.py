class ViewParameter:
    """This class holds view parameters of the analytics request send by cadenza.
    This information include parameters such as width and height.
    """
    VIEW_WIDTH_PARAMETER_NAME = 'net.disy.cadenza.imageWidth'
    VIEW_HEIGHT_PARAMETER_NAME = 'net.disy.cadenza.imageHeight'
    VIEW_DEVICE_PIXEL_RATIO_PARAMETER_NAME = 'net.disy.cadenza.devicePixelRatio'

    def __init__(self, width: int, height: int, device_pixel_ratio: float):
        self._width = width
        self._height = height
        self._device_pixel_ratio = device_pixel_ratio


    @property
    def width(self) -> int:
        """Getter for view width.

        Returns
        -------
        int
            View width
        """

        return self._width


    @property
    def height(self) -> int:
        """Getter for view height.

        Returns
        -------
        int
            View height
        """

        return self._height


    @property
    def device_pixel_ratio(self) -> float:
        """Getter for view device pixel ratio.

        Returns
        -------
        float
            View device pixel ratio
        """

        return self._device_pixel_ratio
