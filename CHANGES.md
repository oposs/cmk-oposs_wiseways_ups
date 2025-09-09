# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### New

### Changed
- **UPS Battery Status** service now only shows battery status and alarms (charge and runtime moved to dedicated services)
- **UPS System Info** service now displays all key information in the summary instead of notices:
  - Model, manufacturer, and serial number shown in main summary
  - Firmware and agent versions displayed in summary
  - Power ratings and battery configuration visible at a glance
  - Maintenance expiration dates trigger warnings when overdue
- **UPS Battery Temperature** service name corrected from "UPS Temperature"

### Fixed
- Removed duplicate battery charge and runtime metrics from Battery Status service
- System Info service now provides comprehensive visibility of all system details

## 0.3.0 - 2025-09-09
### New
- Added individual battery monitoring services:
  - **UPS Battery Charge** - Dedicated service for battery charge percentage
  - **UPS Battery Runtime** - Dedicated service for remaining runtime
- Added comprehensive graphing definitions with unit-based grouping:
  - Separated voltage graphs (AC voltages, battery voltage, all voltages)
  - Individual graphs for percentages, time metrics, currents, and temperature
  - Added missing metrics: battery_current, time_on_battery
- Expanded physical measurement services to 13 individual monitors:
  - Input/Output/Bypass/Battery voltages
  - Input/Output/Bypass frequencies  
  - Battery/Output currents
  - Temperature, Output power, Output load

### Changed
- Reorganized graphing to group metrics by unit type for better visualization
- Updated ruleset configuration to support all 18 services with appropriate thresholds
- Improved monitored_oids.md documentation with service-based organization
- Made all ruleset parameters optional for flexible configuration
- Enhanced battery voltage service to use device configuration as dynamic defaults

### Fixed
- Fixed temperature metric name (changed from battery_temperature to temperature)
- Corrected ruleset parameter names to match check plugin expectations
- Added missing threshold parameters for bypass voltage, battery voltage, currents, and power

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


