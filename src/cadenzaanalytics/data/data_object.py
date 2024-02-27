import json


# pylint: disable=protected-access
class DataObject:
    _attribute_mapping = {}

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

                constructor_parameters[parameter_key] = value

        return cls(**constructor_parameters)
