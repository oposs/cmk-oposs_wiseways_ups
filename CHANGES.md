# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### New

### Changed

### Fixed

## 0.2.0 - 2025-09-08
### New
- Added support for ALL OIDs from monitored_oids.md:
  - upsSecondsOnBattery (.1.3.6.1.2.1.33.1.2.2.0)
  - upsBatteryCurrent (.1.3.6.1.2.1.33.1.2.6.0)
  - upsInputNumLines (.1.3.6.1.2.1.33.1.3.2.0) - displayed in info service
  - upsOutputNumLines (.1.3.6.1.2.1.33.1.4.3.0) - displayed in info service
  - upsSmartBatteryRunTimeRemaining (.1.3.6.1.4.1.935.1.1.1.2.2.4.0) - alternative runtime metric
  - upsBaseOutputStatus (.1.3.6.1.4.1.935.1.1.1.4.1.1.0) - detailed output status with 15 states
  - ups1powerSupplyMode (.1.3.6.1.4.1.44782.1.4.4.1.39.0)
  - ups1remainingCapacityOfBattery (.1.3.6.1.4.1.44782.1.4.4.1.18.0)
- Added enterprise battery voltage OID (.1.3.6.1.4.1.44782.1.4.4.1.19.0) as primary source

### Changed
- Improved handling of special SNMP value -99998 (indicates unknown/unavailable)
- All converter functions now properly handle -99998 and return -1 for unknown values
- Battery runtime and charge now display "unknown" instead of crashing when unavailable

### Fixed
- Fixed crash when battery runtime returns negative values (-99998)
- Fixed parsing of enterprise voltage OIDs to handle -99998 special value
- Battery check now gracefully handles unknown charge percentage and runtime

## 0.1.5 - 2025-09-08
### Fixed
- use HostCondition since we have no service items

## 0.1.4 - 2025-09-08
### Fixed
- return one unified rule

## 0.1.3 - 2025-09-08
## 0.1.2 - 2025-09-08
### Fixed
- fixed package nameing to contain oposs prefix

## 0.1.1 - 2025-09-08
### Changed
- Refactored SNMP OID handling to use metadata-driven approach with OIDDefinition dataclass
- Improved code maintainability by centralizing OID configuration, scaling functions, and value mappings

### Fixed
- Noted mkp installation in README.md

## 0.1.0 - 2025-09-08
### New
- Initial Release


