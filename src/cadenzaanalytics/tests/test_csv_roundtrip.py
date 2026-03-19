"""Roundtrip tests for Cadenza CSV reader and writer.

Tests that write -> read -> write yields the same results.
"""
from datetime import timedelta
from shapely.geometry import Point, LineString, Polygon, MultiPoint

import pandas as pd
import numpy as np
import pytest
from cadenzaanalytics.util.csv import from_cadenza_csv, to_cadenza_csv

#pylint: disable=too-many-public-methods
class TestCadenzaCsvRoundtrip:
    """Test suite for CSV roundtrip (write-read-write)."""

    def test_simple_values_roundtrip(self):
        """Simple values should roundtrip correctly."""
        df1 = pd.DataFrame({"col1": ["a", "b"], "col2": ["c", "d"]})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2

    def test_none_values_roundtrip(self):
        """None values should roundtrip correctly."""
        df1 = pd.DataFrame({"col1": [None, "value"], "col2": ["value2", None]})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2

    def test_empty_strings_roundtrip(self):
        """Empty strings should roundtrip correctly (different from None)."""
        df1 = pd.DataFrame({"col1": ["", "value"], "col2": ["value2", ""]})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        # Verify empty strings are preserved
        assert df2.iloc[0, 0] == ""
        assert df2.iloc[1, 1] == ""

    def test_mixed_none_and_empty_roundtrip(self):
        """Mix of None and empty strings should roundtrip correctly."""
        df1 = pd.DataFrame({
            "col1": ["", None, "value"],
            "col2": [None, "", "value2"],
            "col3": ["v1", "v2", "v3"]
        })
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        # Verify distinction is preserved
        assert df2.iloc[0, 0] == ""  # Empty string
        assert df2.iloc[0, 1] is None  # None
        assert df2.iloc[1, 0] is None  # None
        assert df2.iloc[1, 1] == ""  # Empty string

    def test_escaped_quotes_roundtrip(self):
        """Escaped quotes should roundtrip correctly."""
        df1 = pd.DataFrame({"text": ['He said "hello"', 'She replied "hi"']})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2.iloc[0, 0] == 'He said "hello"'

    def test_semicolons_roundtrip(self):
        """Semicolons in values should roundtrip correctly."""
        df1 = pd.DataFrame({"col": ["a;b;c", "x;y"]})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2

    def test_newlines_roundtrip(self):
        """Newlines in values should roundtrip correctly."""
        df1 = pd.DataFrame({"text": ["line1\r\nline2", "line3\r\nline4"]})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2

    def test_numbers_roundtrip(self):
        """Numbers should roundtrip as strings (default behavior)."""
        df1 = pd.DataFrame({"int": ["123", "456"], "float": ["45.67", "89.01"]})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2

    def test_typed_numbers_roundtrip(self):
        """Typed numbers should roundtrip with type mapping."""
        df1 = pd.DataFrame({"int": [123, 456], "float": [45.67, 89.01]})
        df1 = df1.astype({"int": "Int64", "float": "Float64"})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1, type_mapping={"int": "Int64", "float": "Float64"})
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        # Verify types are preserved
        assert df2["int"].dtype == "Int64"
        assert df2["float"].dtype == "Float64"

    def test_datetime_roundtrip(self):
        """Datetime values should roundtrip correctly."""
        df1 = pd.DataFrame({
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13Z"), pd.Timestamp("2024-06-15T10:00:00Z")],
            "value": ["a", "b"]
        })
        csv1 = to_cadenza_csv(df1, datetime_columns=["timestamp"])
        df2 = from_cadenza_csv(csv1, datetime_columns=["timestamp"])
        csv2 = to_cadenza_csv(df2, datetime_columns=["timestamp"])
        assert csv1 == csv2
        # Verify datetime type is preserved (all same timezone -> pandas datetime dtype)
        assert pd.api.types.is_datetime64_any_dtype(df2["timestamp"])

    def test_datetime_with_none_roundtrip(self):
        """Datetime with None values should roundtrip correctly."""
        df1 = pd.DataFrame({
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13Z"), None]
        })
        csv1 = to_cadenza_csv(df1, datetime_columns=["timestamp"])
        df2 = from_cadenza_csv(csv1, datetime_columns=["timestamp"])
        csv2 = to_cadenza_csv(df2, datetime_columns=["timestamp"])
        assert csv1 == csv2
        assert pd.isna(df2.iloc[1, 0])

    def test_datetime_with_none_and_timezoneoffset_roundtrip(self):
        """Datetime with None values (and/or time zone offsets) should roundtrip correctly."""
        df1 = pd.DataFrame({
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13Z"), None, pd.Timestamp("2024-06-15T10:00:00+01:00")]
        })
        csv1 = to_cadenza_csv(df1, datetime_columns=["timestamp"])
        df2 = from_cadenza_csv(csv1, datetime_columns=["timestamp"])
        csv2 = to_cadenza_csv(df2, datetime_columns=["timestamp"])
        df3 = from_cadenza_csv(csv2, datetime_columns=["timestamp"])
        csv3 = to_cadenza_csv(df3, datetime_columns=["timestamp"])
        assert '2024-06-15T10:00:00+01:00' in csv1  # still contains timezone offset when sending to cadenza
        assert csv2 == csv3 # stabilizing on second roundtrip, as cadenzanalytics converts timezone offsets to utc
        assert pd.isna(df2.iloc[1, 0])
        assert pd.isna(df3.iloc[1, 0])

    def test_datetime_with_none_and_same_timezoneoffset_roundtrip(self):
        """Datetime with None values (and/or SAME time zone offsets) should roundtrip correctly."""
        df1 = pd.DataFrame({
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13+01:00"), None, pd.Timestamp("2024-06-15T10:00:00+01:00")]
        })
        csv1 = to_cadenza_csv(df1, datetime_columns=["timestamp"])
        df2 = from_cadenza_csv(csv1, datetime_columns=["timestamp"])
        csv2 = to_cadenza_csv(df2, datetime_columns=["timestamp"])
        df3 = from_cadenza_csv(csv2, datetime_columns=["timestamp"])
        csv3 = to_cadenza_csv(df3, datetime_columns=["timestamp"])
        assert csv2 == csv3 # stabilizing on second roundtrip, as cadenzanalytics converts timezone offsets to utc
        assert pd.isna(df2.iloc[1, 0])
        assert pd.isna(df3.iloc[1, 0])

    def test_datetime_with_none_and_utc_roundtrip(self):
        """Datetime with None values (and/or SAME time zone offsets) should roundtrip correctly."""
        df1 = pd.DataFrame({
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13Z"), None, pd.Timestamp("2024-06-15T10:00:00Z")]
        })
        csv1 = to_cadenza_csv(df1, datetime_columns=["timestamp"])
        df2 = from_cadenza_csv(csv1, datetime_columns=["timestamp"])
        csv2 = to_cadenza_csv(df2, datetime_columns=["timestamp"])
        assert csv1 == csv2
        assert pd.isna(df2.iloc[1, 0])

    def test_geometry_roundtrip(self):
        """Geometry values should roundtrip correctly."""
        df1 = pd.DataFrame({
            "location": [Point(1, 2), Point(3, 4)],
            "name": ["A", "B"]
        })
        csv1 = to_cadenza_csv(df1, geometry_columns=["location"])
        df2 = from_cadenza_csv(csv1, geometry_columns=["location"])
        csv2 = to_cadenza_csv(df2, geometry_columns=["location"])
        assert csv1 == csv2
        # Verify geometries are preserved
        assert df2.iloc[0, 0] == Point(1, 2)
        assert df2.iloc[1, 0] == Point(3, 4)

    def test_geometry_with_none_roundtrip(self):
        """Geometry with None values should roundtrip correctly."""
        df1 = pd.DataFrame({
            "location": [Point(1, 2), None, Point(5, 6)]
        })
        csv1 = to_cadenza_csv(df1, geometry_columns=["location"])
        df2 = from_cadenza_csv(csv1, geometry_columns=["location"])
        csv2 = to_cadenza_csv(df2, geometry_columns=["location"])
        assert csv1 == csv2
        assert df2.iloc[1, 0] is None

    def test_complex_roundtrip(self):
        """Complex data with all types should roundtrip correctly."""
        df1 = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "", None],
            "timestamp": [pd.Timestamp("2023-01-03T15:29:13Z"), None, pd.Timestamp("2024-01-01T00:00:00Z")],
            "location": [Point(10, 20), None, Point(30, 40)],
            "score": [95.5, 75.0, None]
        })
        df1 = df1.astype({"id": "Int64", "score": "Float64"})

        csv1 = to_cadenza_csv(
            df1,
            datetime_columns=["timestamp"],
            geometry_columns=["location"]
        )
        df2 = from_cadenza_csv(
            csv1,
            type_mapping={"id": "Int64", "score": "Float64"},
            datetime_columns=["timestamp"],
            geometry_columns=["location"]
        )
        csv2 = to_cadenza_csv(
            df2,
            datetime_columns=["timestamp"],
            geometry_columns=["location"]
        )

        assert csv1 == csv2

        # Verify all values are preserved correctly
        assert df2.iloc[0, 1] == "Alice"
        assert df2.iloc[1, 1] == ""
        assert df2.iloc[2, 1] is None
        assert df2.iloc[1, 2] is pd.NaT or pd.isna(df2.iloc[1, 2])
        assert df2.iloc[1, 3] is None
        assert pd.isna(df2.iloc[2, 4])

    def test_all_none_row_roundtrip(self):
        """Row with all None values should roundtrip correctly."""
        df1 = pd.DataFrame({
            "a": ["val1", None, "val3"],
            "b": ["val2", None, "val4"],
            "c": ["val3", None, "val5"]
        })
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        # Verify all-None row
        assert df2.iloc[1, 0] is None
        assert df2.iloc[1, 1] is None
        assert df2.iloc[1, 2] is None

    def test_single_column_roundtrip(self):
        """Single column should roundtrip correctly."""
        df1 = pd.DataFrame({"only": ["val1", None, ""]})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2.iloc[1, 0] is None
        assert df2.iloc[2, 0] == ""

    def test_unicode_roundtrip(self):
        """Unicode characters should roundtrip correctly."""
        df1 = pd.DataFrame({
            "text": ["Hello 世界", "Emoji: 😀🎉", "Français: café", "Русский: привет"]
        })
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2.iloc[0, 0] == "Hello 世界"
        assert df2.iloc[1, 0] == "Emoji: 😀🎉"

    def test_large_dataset_roundtrip(self):
        """Large dataset should roundtrip correctly."""
        num_rows = 1000
        df1 = pd.DataFrame({
            "id": list(range(num_rows)),
            "value": [f"val{i}" for i in range(num_rows)],
            "nullable": [None if i % 3 == 0 else f"data{i}" for i in range(num_rows)]
        })
        df1 = df1.astype({"id": "Int64"})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1, type_mapping={"id": "Int64"})
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert len(df2) == num_rows

    def test_many_columns_roundtrip(self):
        """Many columns should roundtrip correctly."""
        num_cols = 100
        data = {f"col{i}": [f"val{i}", None, ""] for i in range(num_cols)}
        df1 = pd.DataFrame(data)
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert len(df2.columns) == num_cols

    def test_special_characters_in_headers_roundtrip(self):
        """Special characters in column names should roundtrip correctly."""
        df1 = pd.DataFrame({
            "col;1": ["a", "b"],
            'col"2': ["c", "d"],
            "col\r\n3": ["e", "f"]
        })
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert list(df2.columns) == ["col;1", 'col"2', "col\r\n3"]

    def test_whitespace_values_roundtrip(self):
        """Whitespace values should roundtrip correctly."""
        df1 = pd.DataFrame({
            "spaces": ["   ", " a ", ""],
            "tabs": ["\t\t", "a\tb", None]
        })
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2.iloc[0, 0] == "   "
        assert df2.iloc[0, 1] == "\t\t"

    def test_multiple_consecutive_none_roundtrip(self):
        """Multiple consecutive None values should roundtrip correctly."""
        df1 = pd.DataFrame({
            "col1": ["a", None, None, None, "b"],
            "col2": [None, None, "c", None, None],
            "col3": [None, None, None, None, None]
        })
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2.iloc[2, 2] is None
        assert df2.iloc[4, 2] is None

    def test_numeric_strings_roundtrip(self):
        """Numeric-looking strings should roundtrip without type conversion."""
        df1 = pd.DataFrame({
            "codes": ["00123", "001.5", "+123", "-456"],
            "scientific": ["1.5e-10", "3.14e+20", "1e5", "2E-3"]
        })
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2.iloc[0, 0] == "00123"
        assert df2.iloc[1, 1] == "3.14e+20"

    def test_mixed_geometry_types_roundtrip(self):
        """Mix of different geometry types should roundtrip correctly."""
        df1 = pd.DataFrame({
            "geom": [
                Point(1, 2),
                LineString([(0, 0), (1, 1)]),
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
                MultiPoint([(0, 0), (1, 1)]),
                None
            ]
        })
        csv1 = to_cadenza_csv(df1, geometry_columns=["geom"])
        df2 = from_cadenza_csv(csv1, geometry_columns=["geom"])
        csv2 = to_cadenza_csv(df2, geometry_columns=["geom"])
        assert csv1 == csv2
        assert df2.iloc[0, 0] == Point(1, 2)
        assert df2.iloc[4, 0] is None

    def test_datetime_with_different_timezones_roundtrip(self):
        """Datetime values with different timezone offsets should roundtrip correctly."""
        # Input CSV with mixed timezone formats
        # Note: +00:00 gets normalized to Z on output for consistency
        csv_input = (
            '"timestamp"\r\n'
            '"2023-01-03T15:29:13Z"\r\n'
            '"2023-01-03T15:30:13+00:00"\r\n'
            '"2023-01-03T10:29:13-05:00"\r\n'
            '\r\n'  # None value
        )

        # Parse preserves timezone information
        df1 = from_cadenza_csv(csv_input, datetime_columns=["timestamp"])
        csv1 = to_cadenza_csv(df1, datetime_columns=["timestamp"])

        # Check that output normalizes +00:00 to Z but preserves other offsets
        assert '"2023-01-03T15:30:13Z"' in csv1  # First two become Z
        assert '"2023-01-03T15:29:13Z"' in csv1  # -05:00 converted to utc

        # Second roundtrip should be stable
        df2 = from_cadenza_csv(csv1, datetime_columns=["timestamp"])
        csv2 = to_cadenza_csv(df2, datetime_columns=["timestamp"])

        assert csv1 == csv2
        assert len(df2) == 4
        # Mixed timezones result in object dtype with Timestamp values (not pandas datetime dtype)
        # This is expected behavior when not all values have the same timezone
        assert pd.api.types.is_datetime64_any_dtype(df2["timestamp"])
        assert df2.iloc[1, 0] - df2.iloc[0, 0] == timedelta(minutes=1)
        assert df2.iloc[0, 0] == df2.iloc[2, 0]
        assert pd.isna(df2.iloc[3, 0])

    def test_mixed_numeric_types_roundtrip(self):
        """Mix of Int64, Float64, and None should roundtrip correctly."""
        df1 = pd.DataFrame({
            "int_col": [1, 2, None, 4, None],
            "float_col": [1.1, None, 3.3, None, 5.5]
        })
        df1 = df1.astype({"int_col": "Int64", "float_col": "Float64"})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1, type_mapping={"int_col": "Int64", "float_col": "Float64"})
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2["int_col"].dtype == "Int64"
        assert df2["float_col"].dtype == "Float64"

    def test_consecutive_quotes_roundtrip(self):
        """Multiple consecutive quotes should roundtrip correctly."""
        df1 = pd.DataFrame({
            "text": ['He said ""hello""', '"""', 'A "word" here', '""""""']
        })
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2.iloc[0, 0] == 'He said ""hello""'
        assert df2.iloc[1, 0] == '"""'

    def test_complex_mixed_data_roundtrip(self):
        """Complex real-world scenario with all data types mixed."""
        df1 = pd.DataFrame({
            "id": [1, 2, None, 4, 5],
            "name": ["Alice", "", None, "Bob", "Charlie"],
            "score": [95.5, None, 88.0, 75.0, None],
            "timestamp": [
                pd.Timestamp("2023-01-03T15:29:13Z"),
                None,
                pd.Timestamp("2023-06-15T10:00:00Z"),
                pd.Timestamp("2023-12-01T00:00:00Z"),
                None
            ],
            "location": [Point(10, 20), None, LineString([(0, 0), (1, 1)]), Point(30, 40), None],
            "notes": ['Contains "quotes"', "Has\r\nnewlines", "", None, "Normal text"],
            "code": ["00123", "+456", None, "", "-789"]
        })
        df1 = df1.astype({"id": "Int64", "score": "Float64"})

        csv1 = to_cadenza_csv(
            df1,
            datetime_columns=["timestamp"],
            geometry_columns=["location"]
        )
        df2 = from_cadenza_csv(
            csv1,
            type_mapping={"id": "Int64", "score": "Float64"},
            datetime_columns=["timestamp"],
            geometry_columns=["location"]
        )
        csv2 = to_cadenza_csv(
            df2,
            datetime_columns=["timestamp"],
            geometry_columns=["location"]
        )

        assert csv1 == csv2

        # Verify specific values are preserved
        assert df2.iloc[0, 0] == 1
        assert df2.iloc[1, 1] == ""
        assert df2.iloc[2, 1] is None
        assert df2.iloc[1, 2] is pd.NA or pd.isna(df2.iloc[1, 2])
        assert df2.iloc[3, 4] == Point(30, 40)
        assert df2.iloc[0, 5] == 'Contains "quotes"'

    def test_zero_and_negative_numbers_roundtrip(self):
        """Zero and negative numbers should roundtrip correctly."""
        df1 = pd.DataFrame({
            "int_val": [0, -1, -999, None],
            "float_val": [0.0, -1.5, -999.99, None]
        })
        df1 = df1.astype({"int_val": "Int64", "float_val": "Float64"})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1, type_mapping={"int_val": "Int64", "float_val": "Float64"})
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2.iloc[0, 0] == 0
        assert df2.iloc[1, 1] == -1.5

    def test_empty_rows_pattern_roundtrip(self):
        """Pattern of values and empty rows should roundtrip correctly."""
        df1 = pd.DataFrame({
            "col1": ["a", None, "c", None, "e"],
            "col2": [None, "b", None, "d", None]
        })
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2.iloc[1, 0] is None
        assert df2.iloc[1, 1] == "b"

    def test_very_long_value_roundtrip(self):
        """Very long values should roundtrip correctly."""
        long_text = "a" * 10000
        df1 = pd.DataFrame({"text": [long_text, "short", None]})
        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df2)
        assert csv1 == csv2
        assert df2.iloc[0, 0] == long_text

    def test_datetime_all_none_roundtrip(self):
        """Datetime column with all None values should roundtrip correctly."""
        df1 = pd.DataFrame({
            "timestamp": [None, None, None],
            "value": ["a", "b", "c"]
        })
        df1["timestamp"] = pd.to_datetime(df1["timestamp"])

        csv1 = to_cadenza_csv(df1, datetime_columns=["timestamp"])
        df2 = from_cadenza_csv(csv1, datetime_columns=["timestamp"])
        csv2 = to_cadenza_csv(df2, datetime_columns=["timestamp"])

        assert csv1 == csv2
        # Verify all datetime values are None/NaT
        assert pd.isna(df2.iloc[0, 0])
        assert pd.isna(df2.iloc[1, 0])
        assert pd.isna(df2.iloc[2, 0])

    def test_float_nan_roundtrip(self):
        """Float NaN values should roundtrip as None (not preserved as NaN)."""
        df1 = pd.DataFrame({
            "values": [1.5, np.nan, 3.7, np.nan, 5.2]
        })

        csv1 = to_cadenza_csv(df1)
        df2 = from_cadenza_csv(csv1, type_mapping={"values": "Float64"})
        csv2 = to_cadenza_csv(df2)

        # CSV roundtrip should be identical
        assert csv1 == csv2

        # Values should be preserved
        assert df2.iloc[0, 0] == 1.5
        assert pd.isna(df2.iloc[1, 0])  # NaN becomes pd.NA
        assert df2.iloc[2, 0] == 3.7
        assert pd.isna(df2.iloc[3, 0])  # NaN becomes pd.NA
        assert df2.iloc[4, 0] == 5.2

    def test_literal_nan_string_roundtrip(self):
        """Literal string 'NaN' should be preserved as a string, not treated as missing value."""
        # Start with CSV containing quoted "NaN" as a string value
        csv1 = '"text";"number"\r\n"NaN";"123"\r\n"normal";"456"\r\n'

        df1 = from_cadenza_csv(csv1)
        csv2 = to_cadenza_csv(df1)

        # CSV should roundtrip identically
        assert csv1 == csv2

        # "NaN" should be treated as a regular string, not as missing value
        assert df1.iloc[0, 0] == "NaN"
        assert df1.iloc[1, 0] == "normal"
        assert df1.iloc[0, 1] == "123"
        assert df1.iloc[1, 1] == "456"

        # Verify it roundtrips again
        df2 = from_cadenza_csv(csv2)
        csv3 = to_cadenza_csv(df2)
        assert csv2 == csv3

    def test_nan_string_as_float_roundtrip(self):
        """Quoted 'NaN' string parsed as Float64 should become actual NaN."""
        # CSV with quoted "NaN" - should be treated as the string "NaN"
        # When parsed as Float64, pandas converts the string "NaN" to actual np.nan
        csv1 = '"values"\r\n"1.5"\r\n"NaN"\r\n"3.7"\r\n'

        # Parse with Float64 type - pandas will convert string "NaN" to actual NaN
        df1 = from_cadenza_csv(csv1, type_mapping={"values": "Float64"})

        # First value should be 1.5, second should be NaN (from string "NaN"), third should be 3.7
        assert df1.iloc[0, 0] == 1.5
        assert pd.isna(df1.iloc[1, 0])  # String "NaN" becomes actual NaN when converting to Float64
        assert df1.iloc[2, 0] == 3.7

        # Write it back - NaN becomes unquoted (None in CSV)
        # The expected CSV is different from input because "NaN" string became actual NaN
        csv2 = to_cadenza_csv(df1)
        expected_csv2 = '"values"\r\n"1.5"\r\n\r\n"3.7"\r\n'  # NaN becomes unquoted
        assert csv2 == expected_csv2

        # Read it back again with Float64
        df2 = from_cadenza_csv(csv2, type_mapping={"values": "Float64"})
        csv3 = to_cadenza_csv(df2)

        # Should be stable after first conversion
        assert csv2 == csv3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
