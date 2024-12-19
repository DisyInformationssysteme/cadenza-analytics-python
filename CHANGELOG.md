# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
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
