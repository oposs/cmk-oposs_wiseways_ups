# Wiseway UPS - Monitored OIDs

## Overview
This document lists the SNMP OIDs monitored by the CheckMK plugin for Wiseway UPS devices. The plugin supports both standard RFC 1628 UPS MIB OIDs and enterprise-specific OIDs from vendor 44782.

## Implemented OIDs by Service

### System Information Service
Shows static UPS system information and configuration.

| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.2.1.33.1.1.2.0 | upsIdentModel | "6000VA" | - |
| .1.3.6.1.2.1.33.1.1.3.0 | upsIdentUPSSoftwareVersion | "VER 6.xxx" | - |
| .1.3.6.1.2.1.33.1.1.4.0 | upsIdentAgentSoftwareVersion | "2.0.0" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.2.0 | ups1equipmentManufacturer | "Others" | - |
| .1.3.6.1.4.1.44782.1.4.1.5.0 | systemSerialNumber | "5A1903026810Q9100039" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.6.0 | ups1installationTime | "2020-06-13" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.8.0 | ups1maintenanceExpirationTime | "2022-06-13" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.9.0 | ups1batteryInstallationReplacementTime | "2021-06-13" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.10.0 | ups1nextMaintenanceTimeOfBattery | "2025-06-13" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.11.0 | ups1ratedPower | 5000 | W |
| .1.3.6.1.4.1.44782.1.4.4.1.12.0 | ups1ratedCapacityOfBattery | 100 | Ah |
| .1.3.6.1.4.1.44782.1.4.4.1.14.0 | ups1numberOfBatteries | 1 | - |
| .1.3.6.1.4.1.44782.1.4.4.1.15.0 | ups1numberOfBatteriesInASingleGroup | 16 | - |

### Battery Status Service
Monitors battery health, charge level, and runtime.

| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.2.1.33.1.2.1.0 | upsBatteryStatus | 2 (batteryNormal) | - | - |
| .1.3.6.1.2.1.33.1.2.2.0 | upsSecondsOnBattery | 0 | seconds | - |
| .1.3.6.1.4.1.44782.1.4.4.1.16.0 | ups1batteryStatus (enterprise) | 2 | - | - |
| .1.3.6.1.4.1.44782.1.4.4.1.17.0 | ups1batteryTimeRemaining | 15 | minutes → seconds | WARN: 600s, CRIT: 300s |
| .1.3.6.1.4.1.44782.1.4.4.1.18.0 | ups1remainingCapacityOfBattery | 100 | % | WARN: 20%, CRIT: 10% |
| .1.3.6.1.4.1.44782.1.4.4.1.72.0 | ups1batteryAbnormal | 0 | flag | - |
| .1.3.6.1.4.1.44782.1.4.4.1.73.0 | ups1batteryPowered | 0 | flag | - |
| .1.3.6.1.4.1.44782.1.4.4.1.74.0 | ups1batteryLowVoltage | 0 | flag | - |

### Power Status Service  
Monitors power source, operational mode, and power failures.

| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.2.1.33.1.4.1.0 | upsOutputSource | 3 (normal) | - |
| .1.3.6.1.4.1.44782.1.4.4.1.39.0 | ups1powerSupplyMode | 2 (online) | - |
| .1.3.6.1.4.1.935.1.1.1.4.1.1.0 | upsBaseOutputStatus | 2 (onLine) | - |
| .1.3.6.1.2.1.33.1.3.1.0 | upsInputLineBads | 0 | count |
| .1.3.6.1.4.1.44782.1.4.4.1.77.0 | ups1inputAbnormal | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.78.0 | ups1outputAbnormal | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.80.0 | ups1bypassStatus | 1 | flag |

### Alarm Status Service
Monitors system alarms and critical conditions.

| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.4.1.44782.1.4.4.1.71.0 | ups1abnormalCommunication | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.76.0 | ups1temperatureAbnormal | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.79.0 | ups1overLoad | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.81.0 | ups1fanFailure | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.85.0 | ups1shutdownRequest | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.86.0 | ups1testInProgress | 1 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.89.0 | ups1shutdownImminent | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.93.0 | ups1lowBatteryShutdownImminent | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.94.0 | ups1systemStatus | 1 | status |

### Physical Measurement Services

#### Input Voltage Service
| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.27.0 | ups1inputUPhaseVoltage | 231.9 | V | WARN: 250V/210V, CRIT: 260V/200V |

#### Output Voltage Service  
| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.42.0 | ups1outputUPhaseVoltage | 231.9 | V | WARN: 250V/210V, CRIT: 260V/200V |

#### Bypass Voltage Service
| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.59.0 | ups1bypassUPhaseVoltage | 232.9 | V | WARN: 250V/210V, CRIT: 260V/200V |

#### Battery Voltage Service
| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.19.0 | ups1batteryVoltage | 217.9 | V | WARN: 180V, CRIT: 170V |

#### Battery Current Service
| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.4.1.44782.1.4.4.1.20.0 | ups1batteryChargingAndDischargingCurrent | 0.00 | A |

#### Output Current Service
| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.4.1.44782.1.4.4.1.45.0 | ups1outputUPhaseCurrent | 0.00 | A |

#### Temperature Service
| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.21.0 | ups1batteryTemperature | 28.0 | °C | WARN: 40°C/10°C, CRIT: 45°C/5°C |

#### Input Frequency Service
| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.24.0 | ups1inputUPhaseFrequency | 50.0 | Hz | WARN: 51Hz/49Hz, CRIT: 52Hz/48Hz |

#### Output Frequency Service
| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.40.0 | ups1outputFrequency | 50.0 | Hz | WARN: 51Hz/49Hz, CRIT: 52Hz/48Hz |

#### Bypass Frequency Service
| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.57.0 | ups1bypassFrequency | 50.0 | Hz | WARN: 51Hz/49Hz, CRIT: 52Hz/48Hz |

#### Output Power Service
| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.4.1.44782.1.4.4.1.48.0 | ups1outputUPhaseActivePower | 0.00 | W |

#### Output Load Service
| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.51.0 | ups1outputUPhaseLoadRate | 0.0 | % | WARN: 80%, CRIT: 90%

## Configuration OIDs (Used for Dynamic Defaults)

The device provides configuration thresholds that the plugin uses as dynamic defaults when available:

| OID | Description | Example Value | Used In Service |
|-----|-------------|---------------|-----------------|
| .1.3.6.1.4.1.44782.1.1.3.1.0 | inputVoltUpConfig | 242 | Input Voltage |
| .1.3.6.1.4.1.44782.1.1.3.2.0 | inputVoltLowConfig | 187 | Input Voltage |
| .1.3.6.1.4.1.44782.1.1.3.3.0 | outputVoltUpConfig | 225 | Output Voltage |
| .1.3.6.1.4.1.44782.1.1.3.4.0 | outputVoltLowConfig | 215 | Output Voltage |
| .1.3.6.1.4.1.44782.1.1.3.5.0 | upsTempUpConfig | 40 | Temperature |
| .1.3.6.1.4.1.44782.1.1.3.6.0 | upsOutputLoadUpConfig | 0 | Output Load |
| .1.3.6.1.4.1.44782.1.1.3.7.0 | upsBatteryVoltLowConfig | 180 | Battery Voltage |

## Data Conversions

The plugin performs the following conversions:

- **Enterprise string values**: Parsed as floats (e.g., "231.9" → 231.9)
- **Minutes to seconds**: Battery runtime converted for consistent time metrics
- **Status mappings**: Integer values mapped to descriptive strings
- **Alarm flags**: 0/1 values interpreted as normal/alarm states

## Status Value Mappings

### Battery Status (upsBatteryStatus)
- 1: unknown
- 2: batteryNormal
- 3: batteryLow  
- 4: batteryDepleted

### Output Source (upsOutputSource)
- 1: other
- 2: none
- 3: normal
- 4: bypass
- 5: battery
- 6: booster
- 7: reducer

### Power Supply Mode (ups1powerSupplyMode)
- 1: standby
- 2: online
- 3: battery
- 4: bypass
- 5: eco

### Base Output Status (upsBaseOutputStatus)
- 1: unknown
- 2: onLine
- 3: onBattery
- 4: onSmartBoost
- 5: timedSleeping
- 6: softwareBypass
- 7: off
- 8: rebooting
- 9: switchedBypass
- 10: hardwareFailureBypass
- 11: sleepingUntilPowerReturn
- 12: onSmartTrim
- 13: ecoMode
- 14: hotStandby
- 15: onBatteryTest

## Service Summary

The plugin creates 18 CheckMK services:

1. **UPS System Info** - Static information and configuration
2. **UPS Battery Status** - Combined battery health, charge, runtime, and alarms
3. **UPS Battery Charge** - Individual battery charge percentage monitoring
4. **UPS Battery Runtime** - Individual battery runtime remaining monitoring
5. **UPS Power Status** - Power source and operational mode
6. **UPS Alarm Status** - System alarms and warnings
7. **UPS Input Voltage** - AC input voltage monitoring
8. **UPS Output Voltage** - AC output voltage monitoring
9. **UPS Bypass Voltage** - Bypass line voltage monitoring
10. **UPS Battery Voltage** - DC battery voltage monitoring
11. **UPS Battery Current** - Battery charging/discharging current
12. **UPS Output Current** - Output current monitoring
13. **UPS Temperature** - System temperature monitoring
14. **UPS Input Frequency** - Input frequency monitoring
15. **UPS Output Frequency** - Output frequency monitoring
16. **UPS Bypass Frequency** - Bypass frequency monitoring
17. **UPS Output Power** - Power consumption in watts
18. **UPS Output Load** - Load percentage monitoring

## Notes

- The plugin uses enterprise OIDs (44782) as primary data source with RFC 1628 OIDs as fallback
- All time metrics are stored in seconds (SI base unit)
- Thresholds can be customized via CheckMK WATO interface
- Device configuration values are used as dynamic defaults when available
- Model identified as Wiseway UPS with various capacity ratings (6000VA, 10kVA)
