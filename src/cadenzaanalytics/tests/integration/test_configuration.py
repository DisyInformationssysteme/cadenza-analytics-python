"""Extension authors get immediate feedback for invalid required configuration."""

import pytest

import cadenzaanalytics as ca


@pytest.mark.parametrize("field", ["name", "print_name", "data_types", "min_attributes"])
def test_attribute_group_rejects_null_required_configuration(field):
    settings = {"name": "values", "print_name": "Values", "data_types": [ca.DataType.STRING], "min_attributes": 0}
    settings[field] = None

    with pytest.raises(ValueError):
        ca.AttributeGroup(**settings)


@pytest.mark.parametrize("field", ["name", "print_name", "parameter_type"])
def test_parameter_rejects_null_required_configuration(field):
    settings = {"name": "note", "print_name": "Note", "parameter_type": ca.ParameterType.STRING}
    settings[field] = None

    with pytest.raises(ValueError):
        ca.Parameter(**settings)


@pytest.mark.parametrize("field", ["print_name", "extension_type"])
def test_extension_rejects_null_required_configuration(field):
    def analyse(_request):
        return ca.TextResponse("example")

    settings = {"relative_path": "orders", "print_name": "Orders", "extension_type": ca.ExtensionType.DATA,
                "analytics_function": analyse}
    settings[field] = None

    with pytest.raises(ValueError):
        ca.CadenzaAnalyticsExtension(**settings)
