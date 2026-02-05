"""Unit tests for Cadenza CSV parser."""
from shapely.geometry import Point, LineString, MultiPoint, Polygon
import pandas as pd
import pytest
from cadenzaanalytics.util.csv import from_cadenza_csv


# pylint: disable=too-many-public-methods
class TestCadenzaCsvParser:
    """Test suite for from_cadenza_csv function."""

    def test_empty_input(self):
        """Empty string should return empty DataFrame."""
        result = from_cadenza_csv("")
        assert result.empty
        assert len(result.columns) == 0

    def test_single_quoted_value(self):
        """Single quoted value."""
        csv = '"header"\r\n"value"'
        result = from_cadenza_csv(csv)
        assert list(result.columns) == ["header"]
        assert result.iloc[0, 0] == "value"

    def test_empty_quoted_string(self):
        """Empty quoted string should be empty string, not None."""
        csv = '"col1";"col2"\r\n"";""'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == ""
        assert result.iloc[0, 1] == ""

    def test_unquoted_values_are_none(self):
        """Unquoted values should be parsed as None."""
        csv = '"col1";"col2";"col3"\r\n;"value2";'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] is None
        assert result.iloc[0, 1] == "value2"
        assert result.iloc[0, 2] is None

    def test_mixed_quoted_and_unquoted(self):
        """Mixed quote and unquoted in one row."""
        csv = '"col1";"col2";"col3"\r\n"";;"def"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == ""
        assert result.iloc[0, 1] is None
        assert result.iloc[0, 2] == "def"

    def test_multiple_rows(self):
        """Multiple data rows."""
        csv = '"name";"age"\r\n"Alice";"30"\r\n"Bob";'
        result = from_cadenza_csv(csv)
        assert len(result) == 2
        assert result.iloc[0, 0] == "Alice"
        assert result.iloc[0, 1] == "30"
        assert result.iloc[1, 0] == "Bob"
        assert result.iloc[1, 1] is None

    def test_escaped_quotes(self):
        """Double quotes inside quoted values should be unescaped."""
        csv = '"text"\r\n"He said ""hello"""'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == 'He said "hello"'

    def test_semicolon_in_quoted_value(self):
        """Semicolons inside quoted values should be preserved."""
        csv = '"col1";"col2"\r\n"a;b;c";"normal"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "a;b;c"
        assert result.iloc[0, 1] == "normal"

    def test_newline_in_quoted_value(self):
        """Newlines inside quoted values should be preserved."""
        csv = '"text"\r\n"line1\r\nline2"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "line1\r\nline2"

    def test_newline_with_real_cadenza_output(self):
        """Handles None and a newline within a quoted value correctly."""
        csv = '"a";"b";"c"\r\n;"e\r\nxd";"f"\r\n'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] is None
        assert result.iloc[0, 1] == "e\r\nxd"
        assert result.iloc[0, 2] == "f"

    def test_trailing_empty_line(self):
        """Trailing CRLF is just row terminator, not an additional row."""
        csv = '"col"\r\n"val"\r\n'
        result = from_cadenza_csv(csv)
        assert len(result) == 1  # Just one data row
        assert result.iloc[0, 0] == "val"

    def test_actual_empty_row(self):
        """An actual empty row between CRLFs should be parsed as [None]."""
        csv = '"col"\r\n"val"\r\n\r\n"val2"'
        result = from_cadenza_csv(csv)
        assert len(result) == 3
        assert result.iloc[0, 0] == "val"
        assert result.iloc[1, 0] is None  # Empty row
        assert result.iloc[2, 0] == "val2"

    def test_numbers_as_strings(self):
        """Numbers are initially parsed as strings."""
        csv = '"int";"float"\r\n"123";"45.67"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "123"
        assert result.iloc[0, 1] == "45.67"

    def test_type_mapping_int(self):
        """Type mapping should convert strings to Int64."""
        csv = '"number"\r\n"123"\r\n'
        result = from_cadenza_csv(csv, type_mapping={"number": "Int64"})
        assert result["number"].dtype == "Int64"
        assert result.iloc[0, 0] == 123

    def test_type_mapping_float(self):
        """Type mapping should convert strings to Float64."""
        csv = '"value"\r\n"3.14"'
        result = from_cadenza_csv(csv, type_mapping={"value": "Float64"})
        assert result["value"].dtype == "Float64"
        assert result.iloc[0, 0] == 3.14

    def test_type_mapping_with_none(self):
        """Type mapping should handle None values (unquoted) correctly."""
        csv = '"number"\r\n\r\n"42"'
        result = from_cadenza_csv(csv, type_mapping={"number": "Int64"})
        assert result["number"].dtype == "Int64"
        assert pd.isna(result.iloc[0, 0])  # None becomes pd.NA
        assert result.iloc[1, 0] == 42

    def test_iso_datetime_format(self):
        """ISO8601 datetime strings are kept as strings by default."""
        csv = '"timestamp"\r\n"2023-01-03T15:29:13Z"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "2023-01-03T15:29:13Z"

    def test_datetime_parsing(self):
        """Datetime columns should be parsed when specified."""
        csv = '"timestamp";"value"\r\n"2023-01-03T15:29:13Z";"42"'
        result = from_cadenza_csv(csv, datetime_columns=["timestamp"])
        assert pd.api.types.is_datetime64_any_dtype(result["timestamp"])
        assert result.iloc[0, 0] == pd.Timestamp("2023-01-03T15:29:13Z")
        assert result.iloc[0, 1] == "42"

    def test_datetime_parsing_with_none(self):
        """Datetime parsing should handle None values."""
        csv = '"timestamp"\r\n"2023-01-03T15:29:13Z"\r\n\r\n""'
        result = from_cadenza_csv(csv, datetime_columns=["timestamp"])
        assert pd.api.types.is_datetime64_any_dtype(result["timestamp"])
        assert result.iloc[0, 0] == pd.Timestamp("2023-01-03T15:29:13Z")
        assert pd.isna(result.iloc[1, 0])  # None string becomes None
        assert pd.isna(result.iloc[2, 0])  # Empty string becomes None

    def test_all_none_row(self):
        """Row with all unquoted values should be all None."""
        csv = '"a";"b";"c"\r\n;;'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] is None
        assert result.iloc[0, 1] is None
        assert result.iloc[0, 2] is None

    def test_single_column(self):
        """Single column CSV."""
        csv = '"only"\r\n"val1"\r\n"val2"'
        result = from_cadenza_csv(csv)
        assert list(result.columns) == ["only"]
        assert len(result) == 2
        assert result.iloc[0, 0] == "val1"
        assert result.iloc[1, 0] == "val2"

    def test_leading_unquoted_value(self):
        """Line starting with unquoted value."""
        csv = '"col1";"col2"\r\n;"def"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] is None
        assert result.iloc[0, 1] == "def"

    def test_trailing_unquoted_value(self):
        """Line ending with unquoted value."""
        csv = '"col1";"col2"\r\n"abc";'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "abc"
        assert result.iloc[0, 1] is None

    def test_complex_real_world_example(self):
        """Complex real-world example with mixed types."""
        csv = (
            '"id";"name";"score";"comment"\r\n'
            '"1";"Alice";"95.5";"Excellent work""!"""\r\n'
            '"2";;"75.0";""\r\n'
            ';"Charlie";;"No comment"'
        )
        result = from_cadenza_csv(csv)

        # Row 0
        assert result.iloc[0, 0] == "1"
        assert result.iloc[0, 1] == "Alice"
        assert result.iloc[0, 2] == "95.5"
        assert result.iloc[0, 3] == 'Excellent work"!"'

        # Row 1
        assert result.iloc[1, 0] == "2"
        assert result.iloc[1, 1] is None
        assert result.iloc[1, 2] == "75.0"
        assert result.iloc[1, 3] == ""

        # Row 2
        assert result.iloc[2, 0] is None
        assert result.iloc[2, 1] == "Charlie"
        assert result.iloc[2, 2] is None
        assert result.iloc[2, 3] == "No comment"

    def test_type_mapping_multiple_columns(self):
        """Type mapping for multiple columns with different types."""
        csv = '"id";"score";"name"\r\n"1";"98.5";"Alice"\r\n;"75.0";"Bob"'
        result = from_cadenza_csv(
            csv,
            type_mapping={"id": "Int64", "score": "Float64", "name": "string"}
        )

        assert result["id"].dtype == "Int64"
        assert result["score"].dtype == "Float64"
        assert result["name"].dtype == "string"

        assert result.iloc[0, 0] == 1
        assert result.iloc[0, 1] == 98.5
        assert result.iloc[0, 2] == "Alice"

        assert pd.isna(result.iloc[1, 0])
        assert result.iloc[1, 1] == 75.0
        assert result.iloc[1, 2] == "Bob"

    def test_geometry_parsing(self):
        """Geometry columns should be parsed from WKT when specified."""
        csv = '"location";"name"\r\n"POINT (1 2)";"Place A"'
        result = from_cadenza_csv(csv, geometry_columns=["location"])
        assert result.iloc[0, 0] == Point(1, 2)
        assert result.iloc[0, 1] == "Place A"

    def test_geometry_parsing_with_none(self):
        """Geometry parsing should handle None values."""
        csv = '"location"\r\n"POINT (1 2)"\r\nx'
        result = from_cadenza_csv(csv, geometry_columns=["location"])
        assert result.iloc[0, 0] == Point(1, 2)
        assert result.iloc[1, 0] is None  # Unquoted 'x' becomes None

    def test_geometry_parsing_multiple_types(self):
        """Geometry parsing should handle different geometry types."""
        csv = '"geom"\r\n"POINT (1 2)"\r\n"LINESTRING (0 0, 1 1)"'
        result = from_cadenza_csv(csv, geometry_columns=["geom"])
        assert result.iloc[0, 0] == Point(1, 2)
        assert result.iloc[1, 0] == LineString([(0, 0), (1, 1)])

    def test_combined_type_datetime_geometry(self):
        """Test combining type mapping, datetime and geometry parsing."""
        csv = (
            '"id";"timestamp";"location";"value"\r\n'
            '"1";"2023-01-03T15:29:13Z";"POINT (10 20)";"42.5"'
        )
        result = from_cadenza_csv(
            csv,
            type_mapping={"id": "Int64", "value": "Float64"},
            datetime_columns=["timestamp"],
            geometry_columns=["location"]
        )
        assert result.iloc[0, 0] == 1
        assert result.iloc[0, 1] == pd.Timestamp("2023-01-03T15:29:13Z")
        assert result.iloc[0, 2] == Point(10, 20)
        assert result.iloc[0, 3] == 42.5

    def test_datetime_and_geometry_with_nulls(self):
        """Test datetime and geometry parsing with mix of values and nulls."""
        csv = (
            '"timestamp";"location"\r\n'
            '"2023-01-03T15:29:13Z";"POINT (10 20)"\r\n'
            'x;"POINT (5 5)"\r\n'
            '"2023-06-15T10:00:00Z";y\r\n'
            'a;b'
        )
        result = from_cadenza_csv(
            csv,
            datetime_columns=["timestamp"],
            geometry_columns=["location"]
        )

        # Row 0: both have values
        assert result.iloc[0, 0] == pd.Timestamp("2023-01-03T15:29:13Z")
        assert result.iloc[0, 1] == Point(10, 20)

        # Row 1: timestamp is None, geometry has value
        assert pd.isna(result.iloc[1, 0])
        assert result.iloc[1, 1] == Point(5, 5)

        # Row 2: timestamp has value, geometry is None
        assert result.iloc[2, 0] == pd.Timestamp("2023-06-15T10:00:00Z")
        assert result.iloc[2, 1] is None

        # Row 3: both are None
        assert pd.isna(result.iloc[3, 0])
        assert result.iloc[3, 1] is None

    def test_rows_with_all_nones_empty_strings_and_values(self):
        """Test rows with only None values, only empty strings, and only real values."""
        csv = (
            '"col1";"col2";"col3"\r\n'
            '"value1";"value2";"value3"\r\n'
            '"";"";""\r\n'
            ';;'
        )
        result = from_cadenza_csv(csv)

        # Row 0: all real values
        assert result.iloc[0, 0] == "value1"
        assert result.iloc[0, 1] == "value2"
        assert result.iloc[0, 2] == "value3"

        # Row 1: all empty strings (quoted)
        assert result.iloc[1, 0] == ""
        assert result.iloc[1, 1] == ""
        assert result.iloc[1, 2] == ""

        # Row 2: all None values (unquoted)
        assert result.iloc[2, 0] is None
        assert result.iloc[2, 1] is None
        assert result.iloc[2, 2] is None

    def test_unicode_characters(self):
        """Test handling of various Unicode characters."""
        csv = '"text"\r\n"Hello 世界"\r\n"Emoji: 😀🎉"\r\n"Français: café"'
        result = from_cadenza_csv(csv)
        assert len(result) == 3
        assert result.iloc[0, 0] == "Hello 世界"
        assert result.iloc[1, 0] == "Emoji: 😀🎉"
        assert result.iloc[2, 0] == "Français: café"

    def test_very_long_value(self):
        """Test handling of very long values."""
        long_text = "a" * 10000
        csv = f'"text"\r\n"{long_text}"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == long_text

    def test_many_columns(self):
        """Test handling of many columns."""
        num_cols = 100
        headers = ';'.join([f'"col{i}"' for i in range(num_cols)])
        values = ';'.join([f'"val{i}"' for i in range(num_cols)])
        csv = f'{headers}\r\n{values}'
        result = from_cadenza_csv(csv)
        assert len(result.columns) == num_cols
        assert result.iloc[0, 0] == "val0"
        assert result.iloc[0, 99] == "val99"

    def test_multiple_consecutive_semicolons(self):
        """Test handling of multiple consecutive semicolons (multiple None values)."""
        csv = '"a";"b";"c";"d"\r\n"val1";;;"val4"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "val1"
        assert result.iloc[0, 1] is None
        assert result.iloc[0, 2] is None
        assert result.iloc[0, 3] == "val4"

    def test_quoted_value_with_only_whitespace(self):
        """Test that quoted whitespace is preserved."""
        csv = '"col1";"col2"\r\n"   ";"  \t  "'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "   "
        assert result.iloc[0, 1] == "  \t  "

    def test_mixed_line_endings_in_quoted_values(self):
        """Test handling of different line endings within quoted values."""
        csv = '"text"\r\n"line1\nline2"\r\n"line3\rline4"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "line1\nline2"
        assert result.iloc[1, 0] == "line3\rline4"

    def test_type_mapping_invalid_conversion(self):
        """Test type mapping with invalid values."""
        csv = '"number"\r\n"abc"\r\n"123"'
        with pytest.raises(ValueError):
            from_cadenza_csv(csv, type_mapping={"number": "Int64"})

    def test_geometry_invalid_wkt(self):
        """Test geometry parsing with invalid WKT."""
        csv = '"location"\r\n"INVALID WKT"'
        result = from_cadenza_csv(csv, geometry_columns=["location"])
        # shapely's from_wkt with on_invalid='warn' returns None for invalid WKT
        assert result.iloc[0, 0] is None

    def test_polygon_and_multipoint_geometries(self):
        """Test parsing of more complex geometry types."""
        csv = '"geom"\r\n"POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"\r\n"MULTIPOINT ((0 0), (1 1))"'
        result = from_cadenza_csv(csv, geometry_columns=["geom"])
        assert isinstance(result.iloc[0, 0], Polygon)
        assert isinstance(result.iloc[1, 0], MultiPoint)

    def test_datetime_with_different_timezones(self):
        """Test datetime parsing with different timezone offset formats:
        These inputs are unexpected and will currently not happen from Cadenza, yet we want
        to document the current behavior which will not produce a datetime64 dtype but 'object' dtype."""
        csv = (
            '"timestamp"\r\n'
            '"2023-01-03T15:29:13Z"\r\n'
            '"2023-01-03T15:29:13+00:00"\r\n'
            '"2023-01-03T10:29:13-05:00"'
        )
        result = from_cadenza_csv(csv, datetime_columns=["timestamp"])
        assert not pd.api.types.is_datetime64_any_dtype(result["timestamp"])
        assert result["timestamp"].dtype == "object"
        assert len(result) == 3
        assert pd.notna(result.iloc[0, 0])
        assert pd.notna(result.iloc[1, 0])
        assert pd.notna(result.iloc[2, 0])
        # All three timestamps represent the same UTC moment (when compared)
        # but may have different timezone info preserved
        assert result.iloc[0, 0] == result.iloc[1, 0]
        assert result.iloc[0, 0] == result.iloc[2, 0]

    def test_datetime_with_timezone_and_none_values(self):
        """Test datetime parsing with the same timezone format and None values."""
        csv = (
            '"timestamp";"value"\r\n'
            '"2023-01-03T15:29:13+01:00";"a"\r\n'
            ';""\r\n'
            '"2023-06-15T08:00:00+01:00";"c"\r\n'
            '"2023-12-01T00:00:00+01:00";"d"\r\n'
            ';"e"'
        )
        result = from_cadenza_csv(csv, datetime_columns=["timestamp"])
        assert pd.api.types.is_datetime64_any_dtype(result["timestamp"])
        assert len(result) == 5
        assert pd.notna(result.iloc[0, 0])
        assert pd.isna(result.iloc[1, 0])  # None
        assert pd.notna(result.iloc[2, 0])
        assert pd.notna(result.iloc[3, 0])
        assert pd.isna(result.iloc[4, 0])  # None

    def test_special_characters_in_column_names(self):
        """Test handling of special characters in column names."""
        csv = '"col;1";"col""2";"col\r\n3"\r\n"a";"b";"c"'
        result = from_cadenza_csv(csv)
        assert list(result.columns) == ["col;1", 'col"2', "col\r\n3"]
        assert result.iloc[0, 0] == "a"

    def test_empty_dataframe_with_headers_only(self):
        """Test DataFrame with headers but no data rows."""
        csv = '"col1";"col2";"col3"'
        result = from_cadenza_csv(csv)
        assert list(result.columns) == ["col1", "col2", "col3"]
        assert len(result) == 0

    def test_numeric_string_preservation(self):
        """Test that numeric-looking strings are preserved without conversion."""
        csv = '"code"\r\n"00123"\r\n"001.5"\r\n"+123"\r\n"-456"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "00123"
        assert result.iloc[1, 0] == "001.5"
        assert result.iloc[2, 0] == "+123"
        assert result.iloc[3, 0] == "-456"

    def test_boolean_like_values(self):
        """Test handling of boolean-like values as strings."""
        csv = '"flag"\r\n"true"\r\n"false"\r\n"True"\r\n"False"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "true"
        assert result.iloc[1, 0] == "false"
        assert result.iloc[2, 0] == "True"
        assert result.iloc[3, 0] == "False"

    def test_large_numbers(self):
        """Test handling of very large numbers with type mapping."""
        csv = '"big_int";"big_float"\r\n"9999999999999999";"1.7976931348623157e+308"'
        result = from_cadenza_csv(
            csv,
            type_mapping={"big_int": "Int64", "big_float": "Float64"}
        )
        assert result.iloc[0, 0] == 9999999999999999
        assert result.iloc[0, 1] == pytest.approx(1.7976931348623157e+308)

    def test_mixed_none_types(self):
        """Test DataFrame with mix of None, np.nan, and pd.NA."""
        csv = '"col1";"col2";"col3"\r\n"a";;"c"'
        result = from_cadenza_csv(csv)
        assert result.iloc[0, 0] == "a"
        assert result.iloc[0, 1] is None
        assert result.iloc[0, 2] == "c"

    def test_datetime_precision(self):
        """Test datetime parsing with milliseconds and microseconds."""
        csv = (
            '"timestamp"\r\n'
            '"2023-01-03T15:29:13.123456Z"\r\n'
            '"2023-01-03T15:29:13.000Z"'
        )
        result = from_cadenza_csv(csv, datetime_columns=["timestamp"])
        assert pd.api.types.is_datetime64_any_dtype(result["timestamp"])
        # Check that precision is maintained
        assert result.iloc[0, 0].microsecond == 123456

    def test_all_column_types_combined(self):
        """Comprehensive test with all supported column types."""
        csv = (
            '"id";"name";"score";"active";"timestamp";"location";"notes"\r\n'
            '"1";"Alice";"95.5";"true";"2023-01-03T15:29:13Z";"POINT (10 20)";"First student"\r\n'
            ';"Bob";;;"2023-06-15T10:00:00+01";;""\r\n'
            '"3";;"75.0";"false";;"POINT (30 40)";'
        )
        result = from_cadenza_csv(
            csv,
            type_mapping={"id": "Int64", "score": "Float64"},
            datetime_columns=["timestamp"],
            geometry_columns=["location"]
        )

        # Row 0
        assert result.iloc[0, 0] == 1
        assert result.iloc[0, 1] == "Alice"
        assert result.iloc[0, 2] == 95.5
        assert result.iloc[0, 3] == "true"
        assert result.iloc[0, 4] == pd.Timestamp("2023-01-03T15:29:13Z")
        assert result.iloc[0, 5] == Point(10, 20)
        assert result.iloc[0, 6] == "First student"

        # Row 1 - mix of None and empty string
        assert pd.isna(result.iloc[1, 0])
        assert result.iloc[1, 1] == "Bob"
        assert pd.isna(result.iloc[1, 2])
        assert result.iloc[1, 3] is None
        assert result.iloc[1, 4] == pd.Timestamp("2023-06-15T10:00:00+01")
        assert result.iloc[1, 5] is None
        assert result.iloc[1, 6] == ""

        # Row 2
        assert result.iloc[2, 0] == 3
        assert result.iloc[2, 1] is None
        assert result.iloc[2, 2] == 75.0
        assert result.iloc[2, 3] == "false"
        assert pd.isna(result.iloc[2, 4])
        assert result.iloc[2, 5] == Point(30, 40)
        assert result.iloc[2, 6] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
