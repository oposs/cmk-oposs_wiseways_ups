# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### New

### Changed
- All metrics of the UPS services now start with `oposs_wiseways_ups_`,
  for example `oposs_wiseways_ups_input_voltage`, and the battery
  temperature metric is `oposs_wiseways_ups_battery_temperature`, so the
  plugin keeps working on Checkmk 3.0, which refuses metric names that
  clash with built-in ones. The graphs show the history recorded under the
  old names; custom graphs, dashboards or exports that name the old
  metrics must be updated.

### Fixed
- "UPS Environment" took a THS sensor reading of 0.0 °C or below as "no
  sensor": the temperature was left out of the service, which then showed
  only the humidity, or "No environmental sensor data" when the humidity
  read 0 % as well. A temperature of 0 °C or frost, and a humidity of 0 %,
  are now shown and checked against the levels; only an empty value or
  -99998 counts as no sensor.
- "UPS Battery Current", "UPS Output Current" and "UPS Output Power" were
  missing on a UPS that ran on mains without load during the service
  discovery, because they appeared only while the reading was not 0. They
  are now discovered whenever the UPS sends a number, 0 included; a reading
  of -99998 or text such as "N/A" no longer creates "UPS Battery Current",
  which then went UNKNOWN.
- "UPS Battery Voltage" did not warn when the battery voltage sank: the
  default lower levels were 32/30 V, while the battery string of these UPS
  floats at about 218 V. The defaults and the prefill of the "Battery
  voltage lower levels" rule field are now 180/170 V, so a discharging
  battery shows WARN below 180 V and CRIT below 170 V.

## 0.5.0 - 2026-11-08
### New
- The package carries the release version in its check plugin (`__version__`).

### Changed
- Licence is now GNU General Public License v2, aligning this plugin
  with the rest of the OPOSS Checkmk plugin set. The repository
  previously carried no LICENSE file at all.

### Fixed
- When the UPS has no reading, it sends -99998, and the measurement
  services showed that as a value: "UPS Battery Current" said
  "Discharging: 99998.0A" and "UPS Input Voltage" went CRIT on
  -99998.0V. These services now go UNKNOWN with "... data not
  available", as "UPS Battery Charge" and "UPS Battery Runtime" already
  did; this covers the voltage, current, frequency, battery temperature,
  output power and output load services.
- "UPS Battery Runtime" crashed when the UPS sent text such as "N/A"
  instead of a number for the battery time remaining. The service now
  goes UNKNOWN with "Battery runtime: cannot read 'N/A' as a number".
- When the UPS sent text such as "N/A" instead of a number, the
  measurement services showed OK with "nan" (for example "Input voltage:
  nanV") and "UPS Environment" showed no result at all. They now go
  UNKNOWN and quote the text, for example "Input voltage: cannot read
  'N/A' as a number"; this covers "UPS Battery Charge", "UPS Battery
  Current", the voltage, frequency, temperature, output and environment
  services.

## 0.4.3 - 2026-04-28
### Changed
- Battery and environment temperature graphs now also render as filled
  areas

## 0.4.2 - 2026-04-28
### Changed
- Single-metric graphs with a meaningful zero baseline (battery charge,
  battery voltage, output load, output power, environment humidity, alarm
  counters) now render as filled areas instead of lines

## 0.4.1 - 2026-04-15
## 0.4.0 - 2025-12-11
### New
- Added **UPS Environment** service for THS environmental sensor monitoring:
  - Temperature monitoring (thsOneTempData - .1.3.6.1.4.1.44782.1.2.1.1.1.0)
  - Humidity monitoring (thsOneHumiData - .1.3.6.1.4.1.44782.1.2.1.1.2.0)
  - Configurable thresholds for both upper and lower limits
  - Service auto-discovered only when THS sensor is connected
- Added graphing metrics for environmental data (env_temperature, env_humidity)
- Added environment-specific graphs (temperature, humidity, combined)

## 0.3.1 - 2025-09-09
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


