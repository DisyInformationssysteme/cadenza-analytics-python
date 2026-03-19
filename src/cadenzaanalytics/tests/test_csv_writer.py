"""Unit tests for Cadenza CSV writer."""
from datetime import datetime, timezone, timedelta

from shapely.geometry import Point, LineString, MultiPoint, MultiLineString, Polygon
import pandas as pd
import numpy as np
import pytest
from cadenzaanalytics.util.csv import to_cadenza_csv

#pylint: disable=too-many-public-methods
class TestCadenzaCsvWriter:
    """Test suite for to_cadenza_csv function."""

    def test_empty_dataframe(self):
        """Empty DataFrame should return empty string."""
        df = pd.DataFrame()
        result = to_cadenza_csv(df)
        assert result == ""

    def test_single_value(self):
        """Single quoted value."""
        df = pd.DataFrame({"header": ["value"]})
        result = to_cadenza_csv(df)
        assert result == '"header"\r\n"value"\r\n'

    def test_empty_string(self):
        """Empty string should be quoted."""
        df = pd.DataFrame({"col1": ["", ""], "col2": ["a", "b"]})
        result = to_cadenza_csv(df)
        assert result == '"col1";"col2"\r\n"";"a"\r\n"";"b"\r\n'

    def test_none_values(self):
        """None values should be unquoted."""
        df = pd.DataFrame({"col1": [None, "value"], "col2": ["value2", None]})
        result = to_cadenza_csv(df)
        assert result == '"col1";"col2"\r\n;"value2"\r\n"value";\r\n'

    def test_nan_values(self):
        """NaN values should be unquoted (treated as None)."""
        df = pd.DataFrame({"col1": [np.nan, 1.5], "col2": [2.5, np.nan]})
        result = to_cadenza_csv(df)
        assert result == '"col1";"col2"\r\n;"2.5"\r\n"1.5";\r\n'

    def test_multiple_rows(self):
        """Multiple data rows."""
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": ["30", None]})
        result = to_cadenza_csv(df)
        assert result == '"name";"age"\r\n"Alice";"30"\r\n"Bob";\r\n'

    def test_escaped_quotes(self):
        """Double quotes should be escaped."""
        df = pd.DataFrame({"text": ['He said "hello"']})
        result = to_cadenza_csv(df)
        assert result == '"text"\r\n"He said ""hello"""\r\n'

    def test_semicolon_in_value(self):
        """Semicolons should be preserved in quoted values."""
        df = pd.DataFrame({"col1": ["a;b;c"], "col2": ["normal"]})
        result = to_cadenza_csv(df)
        assert result == '"col1";"col2"\r\n"a;b;c";"normal"\r\n'

    def test_newline_in_value(self):
        """Newlines should be preserved in quoted values."""
        df = pd.DataFrame({"text": ["line1\r\nline2"]})
        result = to_cadenza_csv(df)
        assert result == '"text"\r\n"line1\r\nline2"\r\n'

    def test_numbers(self):
        """Numbers should be quoted as strings."""
        df = pd.DataFrame({"int": ["123"], "float": ["45.67"]})
        result = to_cadenza_csv(df)
        assert result == '"int";"float"\r\n"123";"45.67"\r\n'

    def test_datetime_formatting(self):
        """Datetime columns should be formatted as ISO8601."""
        df = pd.DataFrame({
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13Z")],
            "value": [42]
        })
        result = to_cadenza_csv(df, datetime_columns=["timestamp"])
        assert result == '"timestamp";"value"\r\n"2023-01-03T15:29:13Z";"42"\r\n'

    def test_datetime_with_none(self):
        """Datetime formatting should handle None values."""
        df = pd.DataFrame({
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13Z"), None]
        })
        result = to_cadenza_csv(df, datetime_columns=["timestamp"])
        assert result == '"timestamp"\r\n"2023-01-03T15:29:13Z"\r\n\r\n'

    def test_geometry_formatting(self):
        """Geometry columns should be converted to WKT."""
        df = pd.DataFrame({
            "location": [Point(1, 2)],
            "name": ["Place A"]
        })
        result = to_cadenza_csv(df, geometry_columns=["location"])
        assert result == '"location";"name"\r\n"POINT (1 2)";"Place A"\r\n'

    def test_geometry_with_none(self):
        """Geometry formatting should handle None values."""
        df = pd.DataFrame({
            "location": [Point(1, 2), None]
        })
        result = to_cadenza_csv(df, geometry_columns=["location"])
        assert result == '"location"\r\n"POINT (1 2)"\r\n\r\n'

    def test_geometry_multiple_types(self):
        """Geometry formatting should handle different geometry types."""
        df = pd.DataFrame({
            "geom": [Point(1, 2), LineString([(0, 0), (1, 1)])]
        })
        result = to_cadenza_csv(df, geometry_columns=["geom"])
        assert result == '"geom"\r\n"POINT (1 2)"\r\n"LINESTRING (0 0, 1 1)"\r\n'

    def test_combined_datetime_geometry(self):
        """Test combining datetime and geometry formatting."""
        df = pd.DataFrame({
            "id": [1],
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13Z")],
            "location": [Point(10, 20)],
            "value": [42.5]
        })
        result = to_cadenza_csv(
            df,
            datetime_columns=["timestamp"],
            geometry_columns=["location"]
        )
        assert result == '"id";"timestamp";"location";"value"\r\n"1";"2023-01-03T15:29:13Z";"POINT (10 20)";"42.5"\r\n'

    def test_all_none_row(self):
        """Row with all None values."""
        df = pd.DataFrame({"a": [None], "b": [None], "c": [None]})
        result = to_cadenza_csv(df)
        assert result == '"a";"b";"c"\r\n;;\r\n'

    def test_mixed_row(self):
        """Row with mixed None and values."""
        df = pd.DataFrame({"col1": [""], "col2": [None], "col3": ["def"]})
        result = to_cadenza_csv(df)
        assert result == '"col1";"col2";"col3"\r\n"";;"def"\r\n'

    def test_single_column(self):
        """Single column CSV."""
        df = pd.DataFrame({"only": ["val1", "val2"]})
        result = to_cadenza_csv(df)
        assert result == '"only"\r\n"val1"\r\n"val2"\r\n'

    def test_single_column_with_none(self):
        """Single column with None value."""
        df = pd.DataFrame({"col": ["val", None]})
        result = to_cadenza_csv(df)
        assert result == '"col"\r\n"val"\r\n\r\n'

    def test_pandas_na(self):
        """pd.NA values should be unquoted (empty line for single column)."""
        df = pd.DataFrame({"col": [pd.NA, "value"]}, dtype="string")
        result = to_cadenza_csv(df)
        # Single column with None creates empty line (no semicolon)
        assert result == '"col"\r\n\r\n"value"\r\n'

    def test_numeric_dtypes(self):
        """Numeric dtypes Int64 and Float64 should work correctly."""
        df = pd.DataFrame({"int_col": [123, 456, None], "float_col": [1.5, None, 3.7]})
        df = df.astype({"int_col": "Int64", "float_col": "Float64"})
        result = to_cadenza_csv(df)
        assert result == '"int_col";"float_col"\r\n"123";"1.5"\r\n"456";\r\n;"3.7"\r\n'

    def test_unicode_characters(self):
        """Unicode characters should be preserved."""
        df = pd.DataFrame({"text": ["Hello 世界", "Emoji: 😀🎉", "Français: café"]})
        result = to_cadenza_csv(df)
        assert result == '"text"\r\n"Hello 世界"\r\n"Emoji: 😀🎉"\r\n"Français: café"\r\n'

    def test_very_long_value(self):
        """Very long values should be handled correctly."""
        long_text = "a" * 10000
        df = pd.DataFrame({"text": [long_text]})
        result = to_cadenza_csv(df)
        assert long_text in result
        assert result.startswith('"text"\r\n"')

    def test_many_columns(self):
        """Many columns should be handled correctly."""
        num_cols = 100
        data = {f"col{i}": [f"val{i}"] for i in range(num_cols)}
        df = pd.DataFrame(data)
        result = to_cadenza_csv(df)
        assert result.count(';') == num_cols - 1 + num_cols - 1  # header + data row

    def test_whitespace_only_value(self):
        """Whitespace-only values should be quoted and preserved."""
        df = pd.DataFrame({"col": ["   ", "  \t  ", " \n "]})
        result = to_cadenza_csv(df)
        assert result == '"col"\r\n"   "\r\n"  \t  "\r\n" \n "\r\n'

    def test_special_characters_in_column_names(self):
        """Special characters in column names should be quoted properly."""
        df = pd.DataFrame({"col;1": ["a"], 'col"2': ["b"], "col\r\n3": ["c"]})
        result = to_cadenza_csv(df)
        assert result == '"col;1";"col""2";"col\r\n3"\r\n"a";"b";"c"\r\n'

    def test_numeric_string_values(self):
        """Numeric-looking strings should be quoted."""
        df = pd.DataFrame({"code": ["00123", "001.5", "+123", "-456"]})
        result = to_cadenza_csv(df)
        assert result == '"code"\r\n"00123"\r\n"001.5"\r\n"+123"\r\n"-456"\r\n'

    def test_boolean_values_as_strings(self):
        """Boolean-like values should be converted to strings."""
        df = pd.DataFrame({"flag": ["true", "false", "True", "False"]})
        result = to_cadenza_csv(df)
        assert result == '"flag"\r\n"true"\r\n"false"\r\n"True"\r\n"False"\r\n'

    def test_scientific_notation_numbers(self):
        """Numbers in scientific notation should be preserved."""
        df = pd.DataFrame({"value": ["1.5e-10", "3.14e+20"]})
        result = to_cadenza_csv(df)
        assert result == '"value"\r\n"1.5e-10"\r\n"3.14e+20"\r\n'

    def test_multiple_consecutive_none_values(self):
        """Multiple consecutive None values should be unquoted."""
        df = pd.DataFrame({"a": ["val1", None, None, None], "b": [None, None, None, "val2"]})
        result = to_cadenza_csv(df)
        assert result == '"a";"b"\r\n"val1";\r\n;\r\n;\r\n;"val2"\r\n'

    def test_mixed_newlines_in_value(self):
        """Different newline types in values should be preserved."""
        df = pd.DataFrame({"text": ["line1\nline2", "line3\rline4", "line5\r\nline6"]})
        result = to_cadenza_csv(df)
        assert result == '"text"\r\n"line1\nline2"\r\n"line3\rline4"\r\n"line5\r\nline6"\r\n'

    def test_datetime_with_microseconds(self):
        """Datetime with microseconds should format correctly."""
        df = pd.DataFrame({
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13.123456Z")]
        })
        result = to_cadenza_csv(df, datetime_columns=["timestamp"])
        assert result == '"timestamp"\r\n"2023-01-03T15:29:13Z"\r\n'

    def test_datetime_with_timezone_info(self):
        """Datetime with timezone should format correctly."""
        df = pd.DataFrame({
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13", tz="UTC")]
        })
        result = to_cadenza_csv(df, datetime_columns=["timestamp"])
        assert '"2023-01-03T15:29:13Z' in result

    def test_non_pandas_datetime_with_timezone_info(self):
        """Datetime with non-pandas timezone should format correctly."""
        df = pd.DataFrame({
            "timestamp": [datetime(2023, 1, 3, 15, 29, 13, tzinfo=timezone(timedelta(hours=1)))]
        })
        result = to_cadenza_csv(df, datetime_columns=["timestamp"])
        assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
        assert '"2023-01-03T15:29:13+01:00' in result

    def test_non_pandas_non_dtype_datetime_with_timezone_info(self):
        """Datetime with non-pandas timezone should format correctly."""
        df = pd.DataFrame({
            "timestamp": [datetime(2023, 1, 3, 15, 29, 13, tzinfo=timezone(timedelta(hours=1))),
                          datetime(2024, 1, 3, 15, 29, 13, tzinfo=timezone(timedelta(hours=2)))]
        })
        assert not pd.api.types.is_datetime64_any_dtype(df["timestamp"])
        result = to_cadenza_csv(df, datetime_columns=["timestamp"])
        assert '"2023-01-03T15:29:13+01:00' in result

    def test_geometry_linestring_and_polygon(self):
        """Different geometry types should convert to WKT correctly."""
        df = pd.DataFrame({
            "geom": [
                LineString([(0, 0), (1, 1)]),
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
            ]
        })
        result = to_cadenza_csv(df, geometry_columns=["geom"])
        assert 'LINESTRING' in result
        assert 'POLYGON' in result

    def test_geometry_multipoint_and_multilinestring(self):
        """Multi-geometry types should convert to WKT correctly."""
        df = pd.DataFrame({
            "geom": [
                MultiPoint([(0, 0), (1, 1)]),
                MultiLineString([[(0, 0), (1, 1)], [(2, 2), (3, 3)]])
            ]
        })
        result = to_cadenza_csv(df, geometry_columns=["geom"])
        assert 'MULTIPOINT' in result
        assert 'MULTILINESTRING' in result

    def test_empty_string_vs_none_distinction(self):
        """Empty strings and None values must be clearly distinguished."""
        df = pd.DataFrame({
            "col1": ["", None, "", None],
            "col2": [None, "", None, ""],
        })
        result = to_cadenza_csv(df)
        expected = '"col1";"col2"\r\n"";\r\n;""\r\n"";\r\n;""\r\n'
        assert result == expected

    def test_large_dataframe(self):
        """Large dataframe should be handled correctly."""
        num_rows = 1000
        df = pd.DataFrame({
            "id": [str(i) for i in range(num_rows)],
            "value": [f"val{i}" for i in range(num_rows)]
        })
        result = to_cadenza_csv(df)
        # Check header + 1000 data rows + final CRLF
        assert result.count('\r\n') == num_rows + 1

    def test_mixed_types_conversion(self):
        """Mixed types should all be converted to strings."""
        df = pd.DataFrame({
            "mixed": [123, "text", 45.67, True, None]
        })
        result = to_cadenza_csv(df)
        lines = result.split('\r\n')
        assert lines[0] == '"mixed"'
        assert lines[1] == '"123"'
        assert lines[2] == '"text"'
        assert lines[3] == '"45.67"'
        assert lines[4] == '"True"'
        assert lines[5] == ''  # None becomes unquoted (empty)

    def test_zero_values(self):
        """Zero values should be quoted correctly."""
        df = pd.DataFrame({"int": ["0"], "float": ["0.0"], "text": ["000"]})
        result = to_cadenza_csv(df)
        assert result == '"int";"float";"text"\r\n"0";"0.0";"000"\r\n'

    def test_negative_numbers(self):
        """Negative numbers should be quoted correctly."""
        df = pd.DataFrame({"num": ["-123", "-45.67", "-0"]})
        result = to_cadenza_csv(df)
        assert result == '"num"\r\n"-123"\r\n"-45.67"\r\n"-0"\r\n'

    def test_consecutive_quotes(self):
        """Multiple consecutive quotes should be escaped correctly."""
        df = pd.DataFrame({"text": ['He said ""hello""', '"""']})
        result = to_cadenza_csv(df)
        assert result == '"text"\r\n"He said """"hello"""""\r\n""""""""\r\n'

    def test_tab_characters(self):
        """Tab characters should be preserved in quoted values."""
        df = pd.DataFrame({"text": ["col1\tcol2", "a\tb\tc"]})
        result = to_cadenza_csv(df)
        assert result == '"text"\r\n"col1\tcol2"\r\n"a\tb\tc"\r\n'

    def test_datetime_timezone_aware_preservation(self):
        """Timezone-aware datetime values should preserve timezone information."""
        df = pd.DataFrame({
            "timestamp": [
                pd.Timestamp("2023-01-03T15:29:13Z"),
                pd.Timestamp("2023-01-03T15:29:13+00:00"),
            ]
        })
        result = to_cadenza_csv(df, datetime_columns=["timestamp"])
        lines = result.split('\r\n')
        assert lines[0] == '"timestamp"'
        # Both timestamps should be formatted with timezone info
        # isoformat() outputs these consistently
        assert '2023-01-03' in lines[1]
        assert '2023-01-03' in lines[2]

    def test_datetime_column_all_none(self):
        """Datetime column with all None values."""
        df = pd.DataFrame({
            "timestamp": [None, None, None],
            "value": ["a", "b", "c"]
        })
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        result = to_cadenza_csv(df, datetime_columns=["timestamp"])
        assert result == '"timestamp";"value"\r\n;"a"\r\n;"b"\r\n;"c"\r\n'

    def test_float_nan_values(self):
        """Float NaN values without float_columns specified should be treated as None (unquoted)."""
        df = pd.DataFrame({
            "values": [1.5, np.nan, 3.7, np.nan]
        })
        result = to_cadenza_csv(df)
        assert result == '"values"\r\n"1.5"\r\n\r\n"3.7"\r\n\r\n'

    def test_float_nan_values_with_float_column_metadata(self):
        """Float NaN values with float_columns specified should output literal "NaN"."""
        df = pd.DataFrame({
            "values": [1.5, np.nan, 3.7, np.nan]
        })
        result = to_cadenza_csv(df, float_columns=["values"])
        assert result == '"values"\r\n"1.5"\r\n"NaN"\r\n"3.7"\r\n"NaN"\r\n'

    def test_mixed_columns_with_nan(self):
        """Mixed column types with NaN - only float columns should output "NaN"."""
        df = pd.DataFrame({
            "int_col": [1, None, 3],
            "float_col": [1.5, np.nan, 3.7],
            "str_col": ["a", None, "c"]
        })
        result = to_cadenza_csv(df, float_columns=["float_col"], int_columns=["int_col"])
        # int_col: pandas converts to float, but we convert back to int for output
        assert result == '"int_col";"float_col";"str_col"\r\n"1";"1.5";"a"\r\n;"NaN";\r\n"3";"3.7";"c"\r\n'

    def test_int64_and_float64_with_nan(self):
        """INT64 with None should output empty, FLOAT64 with None should output "NaN"."""
        df = pd.DataFrame({
            "int_col": pd.array([1, None, 3], dtype="Int64"),
            "float_col": pd.array([1.5, None, 3.7], dtype="Float64")
        })
        result = to_cadenza_csv(df, float_columns=["float_col"], int_columns=["int_col"])
        # INT64 None = empty, FLOAT64 None = "NaN"
        assert result == '"int_col";"float_col"\r\n"1";"1.5"\r\n;"NaN"\r\n"3";"3.7"\r\n'

    def test_int64_explicit_metadata(self):
        """INT64 columns with int_columns specified should output empty for None."""
        df = pd.DataFrame({
            "int_col1": pd.array([1, None, 3], dtype="Int64"),
            "int_col2": pd.array([10, 20, None], dtype="Int64")
        })
        result = to_cadenza_csv(df, int_columns=["int_col1", "int_col2"])
        # Both INT64 columns should have empty for None
        assert result == '"int_col1";"int_col2"\r\n"1";"10"\r\n;"20"\r\n"3";\r\n'

    def test_int64_explicit_from_float(self):
        """INT64 columns with int_columns specified should output empty for None."""
        df = pd.DataFrame({
            "int_col1": pd.array([1, 2, 3], dtype="Int64"),
            "int_col2": pd.array([10.0, 20.5, 13.6], dtype="Float64")
        })
        result = to_cadenza_csv(df, int_columns=["int_col1", "int_col2"])
        # Both INT64 columns should have empty for None
        assert result == '"int_col1";"int_col2"\r\n"1";"10"\r\n"2";"20"\r\n"3";"13"\r\n'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
