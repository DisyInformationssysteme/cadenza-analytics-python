# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Unreleased

## 10.4.0 - 2025-12-05
### Added
- New visual response of type text (TextResponse)
- New visual response of type url (UrlResponse)
- New response for type data (DataResponse)
- New response for type enrichment (EnrichmentResponse)
- Basic column metadata validation for data and enrichment responses
- Handling of missing column metadata can be set via MissingMetadataStrategy
- Parameter form the Cadenza view of visual analytics request can now be retrieved as ViewParameter object
- Method to retrieve enrichment ID column
- Values of type zoned date time send by Cadenza are parsed as pandas Timestamps (pandas equivalent for python datetime.datetime) in ISO8701 format
- Analytics request object was introduced. This builds new foundation for further extension of requests send from cadenza

### Changed
- Function signature of analytics function has changed form (metadata: ca.RequestMetadata, data: pd.DataFrame) to (request: ca.AnalyticsRequest). This changes access to data, metadata and parameters
- Constructor arguments of AttributeGroup, ColumnMetadata and Parameter are new keyword only arguments
- Extension types has been renamed. From visualization to visual and calculation to data
- Response of type CsvResponse was changed as library internal. Please use DataResponse or EnrichmentResponse instead
- Development status of library was set to `5 - Production/Stable`

### Removed
- Response of type RowWiseMappingCsvResponse was removed. Pleas use EnrichmentResponse instead

## 10.3.0 - 2025-11-06
### Added
- Adds basic logging and version information

### Changed
- The version scheme on cadenzaanalytics is now based on the Cadenza main version (starting with Cadenza 10.3). New versions have the format x.x.y, where x.x is the Cadenza main version and y a functional change or bugfix.

## 0.1.26 - 2025-03-11
- Support multipart/form-data that is parsed as files and not as forms

## 0.1.25 - 2024-12-19

## 0.1.24 - 2024-12-19
- Important: Flask version and Werkzeug version set explicitly as latest flask 2.x pulls in an incompatible Werkzeug 3.1.x version where the form request limit was changed from unlimited to 50kb and cannot be configured yet via flask

## 0.1.23 - 2024-08-05
- Breaking API changes in RequestMetadata for column metadata access
- Updates examples, split into separate standalone directories

## 0.1.22 - 2024-08-05

## 0.1.21 - 2024-03-06
- Row wise mapped results can now be list of values instead of pandas Series if they respect the index order

## 0.1.20 - 2024-03-06
### Added
- Support for closure in row wise mapping result so that logging or validation can happen to the final result before sending

## 0.1.19 - 2024-03-06
### Added
- Support for common use case which maps one input row to one output row, especially interesting for extensions of type ENRICHMENT

## 0.1.10 - 2024-02-28
### Fixed
- Compatibility problem when using cadenzaanalytics with python 3.8

## 0.1.9 - 2024-02-28
### Added
- First beta version of cadenzaanalytics python library that is also available on PyPi
