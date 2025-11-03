import json


# pylint: disable=protected-access
class DataObject:
    """A class representing a data object that can be serialized to JSON.

    Returns
    -------
    dict
        Serialize the data object to a JSON string.
    """
    _attribute_mapping = {}
    _attribute_constructors = {}  # required for enums that are deserialized

    def _to_dict(self) -> dict:
        result = {}

        for key, attribute in self._attribute_mapping.items():
            value = getattr(self, attribute)

            if value is not None:
                if isinstance(value, list):
                    result_list = []

                    for element in value:
                        if issubclass(type(element), DataObject):
                            result_list.append(element._to_dict())
                        else:
                            result_list.append(element)

                    result[key] = result_list
                else:
                    result[key] = value

        return result

    def to_json(self, indent=None) -> str:
        """Serialize the data object to a JSON string.

        Parameters
        ----------
        indent : int, optional
            The number of spaces to use for indentation, by default None

        Returns
        -------
        str
            A JSON string representing the data object.
        """
        return json.dumps(self._to_dict(), indent=indent, default=str)

    @classmethod
    def _from_dict(cls, data: dict):
        constructor_parameters = {}

        # remap data fields to constructor parameters
        for key, value in data.items():
            if key in cls._attribute_mapping:
                # TODO: Consider removing the underscore from attribute mapping, and adding it when used
                # get the constructor parameter key be removing underscore from attribute mapping
                parameter_key = cls._attribute_mapping[key][1:]

                if key in cls._attribute_constructors:
                    value = cls._attribute_constructors[key](value)
                constructor_parameters[parameter_key] = value

        return cls(**constructor_parameters)


    def __str__(self):
        return self.to_json(indent=4)

    def __repr__(self):
        return self.__str__()