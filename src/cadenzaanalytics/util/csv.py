import csv
import sys
from io import StringIO
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from shapely import from_wkt, to_wkt


def from_cadenza_csv(
    csv_data: str,
    type_mapping: Optional[Dict[str, str]] = None,
    datetime_columns: Optional[List[str]] = None,
    geometry_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """Parse Cadenza CSV format into a pandas DataFrame.

    Cadenza CSV specs:
    - Text encoding is UTF-8
    - Values are separated by semicolons (;)
    - Values enclosed by double quotes (") are considered present
    - Values not quoted are considered None/Null/missing
    - Numbers are decimal with dot (.) as decimal separator
    - Lines separated by CRLF (\\r\\n)
    - DateTimes follow ISO8601 format (e.g., 2023-01-03T15:29:13Z)
    - Geometries are WKT strings that get parsed to shapely geometries

    Parameters
    ----------
    csv_data : str
        The CSV data as a string
    type_mapping : Optional[Dict[str, type]]
        Optional mapping of column names to pandas dtypes
    datetime_columns : Optional[List[str]]
        List of column names to parse as ISO8601 datetimes
    geometry_columns : Optional[List[str]]
        List of column names to parse as WKT geometries

    Returns
    -------
    pd.DataFrame
        Parsed dataframe with proper None values for unquoted fields
    """
    if not csv_data or not csv_data.strip():
        return pd.DataFrame()

    all_rows =  _parse_csv_with_default_reader(csv_data) \
        if sys.version_info >= (3, 13) \
        else _parse_csv(csv_data)

    if not all_rows:
        return pd.DataFrame()

    # First row is headers
    headers = all_rows[0]
    parsed_rows = all_rows[1:]

    # Create DataFrame, use dtype=object to preserve None values (behavior changes with
    # pandas 3.0.0 where None values without a specified dtype result in <NA> values
    # and a specific dtype is chosen depending on other values in the column)
    df = pd.DataFrame(parsed_rows, columns=headers, dtype=object)

    # Apply type mappings if provided
    if type_mapping:
        for col, dtype in type_mapping.items():
            if col in df.columns:
                df[col] = df[col].astype(dtype)

    # Parse datetime columns
    if datetime_columns:
        for col in datetime_columns:
            if col in df.columns:
                # Parse without format specification to handle various ISO8601 timezone formats
                df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)

    # Parse WKT geometries into shapely geometry objects
    if geometry_columns:
        for col in geometry_columns:
            if col in df.columns:
                values = df[col].to_numpy()
                df[col] = from_wkt(values, on_invalid='warn')

    return df


def _parse_csv_with_default_reader(csv_data: str) -> List[str]:
    # QUOTE_NOTNULL was only fixed for Python 3.13+ in the csv reader
    # see https://github.com/python/cpython/issues/113732
    all_rows = []
    class CadenzaDialect(csv.excel):
        delimiter = ';'
        quotechar = '"'
        doublequote = True
        lineterminator = '\r\n'
        quoting = csv.QUOTE_NOTNULL
        skipinitialspace = False

    reader = csv.reader(StringIO(csv_data), dialect=CadenzaDialect)

    for row in reader:
        all_rows.append(row)
    return all_rows

# pylint: disable=too-many-branches,too-many-nested-blocks,too-many-locals
def _parse_csv(csv_data: str):
    """Parse entire CSV data respecting quoted fields with embedded newlines.

    Returns list of rows, where each row is a list of values.
    """
    rows = []
    pos = 0

    while pos < len(csv_data):
        row = []
        last_was_semicolon = False

        # Parse one row (until we hit CRLF that's not inside a quoted field)
        while pos < len(csv_data):
            # Check for row terminator first
            if csv_data[pos:pos+2] == '\r\n':
                # If last character before CRLF was semicolon, add trailing None
                if last_was_semicolon:
                    row.append(None)
                break

            # Reset flag
            last_was_semicolon = False

            # Check if value is quoted
            if csv_data[pos] == '"':
                # Quoted value - extract content (can contain newlines)
                pos += 1
                value = []
                while pos < len(csv_data):
                    if csv_data[pos] == '"':
                        # Check for escaped quote
                        if pos + 1 < len(csv_data) and csv_data[pos + 1] == '"':
                            value.append('"')
                            pos += 2
                        else:
                            # End of quoted value
                            pos += 1
                            break
                    else:
                        value.append(csv_data[pos])
                        pos += 1
                row.append(''.join(value))

                # Move past semicolon if present
                if pos < len(csv_data) and csv_data[pos] == ';':
                    pos += 1
                    last_was_semicolon = True
            elif csv_data[pos] == ';':
                # Semicolon at current position = unquoted (None) value before it
                row.append(None)
                pos += 1
                last_was_semicolon = True
            else:
                # Any other character at start of field = unquoted = None
                row.append(None)
                while pos < len(csv_data) and csv_data[pos] != ';' and csv_data[pos:pos+2] != '\r\n':
                    pos += 1
                if pos < len(csv_data) and csv_data[pos] == ';':
                    pos += 1
                    last_was_semicolon = True

        # If we ended at EOF and last was semicolon, add trailing None
        if pos >= len(csv_data) and last_was_semicolon:
            row.append(None)

        # Add row (even if empty - empty row means single None value)
        if row or (pos < len(csv_data) and csv_data[pos:pos+2] == '\r\n'):
            rows.append(row if row else [None])

        # Skip CRLF
        if pos < len(csv_data) and csv_data[pos:pos+2] == '\r\n':
            pos += 2

    return rows


def to_cadenza_csv(
    df: pd.DataFrame,
    datetime_columns: Optional[List[str]] = None,
    geometry_columns: Optional[List[str]] = None,
    float_columns: Optional[List[str]] = None,
    int_columns: Optional[List[str]] = None
) -> str:
    """Convert a pandas DataFrame to Cadenza CSV format.

    Cadenza CSV specs:
    - Text encoding is UTF-8
    - Values are separated by semicolons (;)
    - Values enclosed by double quotes (") are considered present
    - Values not quoted are considered None/Null/missing
    - Numbers are decimal with dot (.) as decimal separator
    - Lines separated by CRLF (\\r\\n)
    - DateTimes follow ISO8601 format (e.g., 2023-01-03T15:29:13Z)
    - Geometries are converted to WKT strings
    - Float columns with NaN values output as the literal string "NaN" (quoted)
    - Int columns with None values output as empty/unquoted (not "NaN")

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to convert
    datetime_columns : Optional[List[str]]
        List of column names to format as ISO8601 datetimes
    geometry_columns : Optional[List[str]]
        List of column names to convert from shapely geometries to WKT
    float_columns : Optional[List[str]]
        List of column names that are float types (NaN will be output as "NaN")
    int_columns : Optional[List[str]]
        List of column names that are int types (None will be output as empty)

    Returns
    -------
    str
        CSV data as a string
    """
    if df.empty and len(df.columns) == 0:
        return ""

    # Build CSV string
    lines = []

    # Write header (no special formatting for header row)
    columns_list = df.columns.tolist()
    lines.append(_format_row(columns_list, columns_list, None, None, None, None))

    # Write data rows
    for _, row in df.iterrows():
        lines.append(_format_row(
            row.tolist(),
            columns_list,
            float_columns,
            int_columns,
            datetime_columns,
            geometry_columns))

    return '\r\n'.join(lines) + '\r\n'


def _format_row(
    values: List,
    columns: List[str],
    float_columns: Optional[List[str]] = None,
    int_columns: Optional[List[str]] = None,
    datetime_columns: Optional[List[str]] = None,
    geometry_columns: Optional[List[str]] = None
) -> str:
    """Format a row of values according to Cadenza CSV rules.

    - None/NaN/pd.NA values are unquoted for non-float types (represented as empty)
    - For float type columns, NaN values are output as the literal string "NaN" (quoted)
    - For int type columns, None values are explicitly output as empty (unquoted)
    - All other values are quoted
    - Quotes within values are escaped by doubling them
    - Datetime values are formatted as ISO8601 strings
    - Geometry values are converted to WKT strings
    """
    formatted_values = []
    float_cols_set = set(float_columns) if float_columns else set()
    int_cols_set = set(int_columns) if int_columns else set()
    datetime_cols_set = set(datetime_columns) if datetime_columns else set()
    geometry_cols_set = set(geometry_columns) if geometry_columns else set()

    for i, value in enumerate(values):
        col_name = columns[i] if i < len(columns) else None

        # Check for None/NaN/pd.NA first (before checking column type)
        if value is None or (isinstance(value, float) and np.isnan(value)) or pd.isna(value):
            # For float columns, output literal "NaN"; for int/others, unquoted empty
            if col_name and col_name in float_cols_set:
                formatted_values.append('"NaN"')
            else:
                # Int columns and all other types output empty for None/NaN
                formatted_values.append('')
        # Handle datetime columns
        elif col_name and col_name in datetime_cols_set:
            # Use isoformat() and replace microseconds
            iso_str = value.isoformat(timespec='seconds')
            # Normalize +00:00 to Z for consistency
            if iso_str.endswith('+00:00'):
                iso_str = iso_str[:-6] + 'Z'
            formatted_values.append(f'"{iso_str}"')
        # Handle geometry columns
        elif col_name and col_name in geometry_cols_set:
            str_value = to_wkt(value)
            formatted_values.append(f'"{str_value}"')
        # Handle int columns - convert float to int if needed
        elif col_name and col_name in int_cols_set:
            # Convert to int first (handles case where pandas converted int to float due to None)
            if isinstance(value, float):
                int_value = int(value)
            else:
                int_value = value
            formatted_values.append(f'"{int_value}"')
        else:
            # Convert to string and quote it
            str_value = str(value)
            # Escape quotes by doubling them
            str_value = str_value.replace('"', '""')
            formatted_values.append(f'"{str_value}"')

    return ';'.join(formatted_values)
