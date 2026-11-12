# Wiseway UPS - Monitored OIDs

## Overview
This document lists the SNMP OIDs monitored by the CheckMK plugin for Wiseway UPS devices. The plugin reads standard RFC 1628 UPS MIB OIDs, one XPPC-MIB OID (upsBaseOutputStatus) and enterprise-specific OIDs from vendor 44782.

## Implemented OIDs by Service

### System Info Service
Shows static UPS system information and configuration. A maintenance
expiration or next battery maintenance date in the past makes the service
WARN ("Maintenance expired: ...", "Battery maintenance due: ...").
The card reads 2032-01-01 for a date nobody entered; the service shows such
a date as "not configured" and never warns on it. A rated power of 0 is left
out of "Ratings".

| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.2.1.33.1.1.2.0 | upsIdentModel | "6000VA" | - |
| .1.3.6.1.2.1.33.1.1.3.0 | upsIdentUPSSoftwareVersion | "VER 6.xxx" | - |
| .1.3.6.1.2.1.33.1.1.4.0 | upsIdentAgentSoftwareVersion | "2.0.0" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.2.0 | ups1equipmentManufacturer | "Others" | - |
| .1.3.6.1.4.1.44782.1.4.1.5.0 | systemSerialNumber | "5A1903026810Q9100039" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.6.0 | ups1installationTime | "2020-06-13" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.8.0 | ups1maintenanceExpirationTime | "2030-06-13" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.9.0 | ups1batteryInstallationReplacementTime | "2021-06-13" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.10.0 | ups1nextMaintenanceTimeOfBattery | "2029-06-13" | - |
| .1.3.6.1.4.1.44782.1.4.4.1.11.0 | ups1ratedPower | 5000 | W |
| .1.3.6.1.4.1.44782.1.4.4.1.12.0 | ups1ratedCapacityOfBattery | 100 | Ah |
| .1.3.6.1.4.1.44782.1.4.4.1.14.0 | ups1numberOfBatteries | 1 | - |
| .1.3.6.1.4.1.44782.1.4.4.1.15.0 | ups1numberOfBatteriesInASingleGroup | 16 | - |

### Battery Status Service
Monitors battery status, time on battery and the battery alarm flags.

| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.2.1.33.1.2.1.0 | upsBatteryStatus | 2 (batteryNormal) | - |
| .1.3.6.1.2.1.33.1.2.2.0 | upsSecondsOnBattery | 0 | seconds |
| .1.3.6.1.4.1.44782.1.4.4.1.16.0 | ups1batteryStatus (enterprise, not evaluated) | 2 | - |
| .1.3.6.1.4.1.44782.1.4.4.1.72.0 | ups1batteryAbnormal | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.73.0 | ups1batteryPowered | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.74.0 | ups1batteryLowVoltage | 0 | flag |

upsBatteryStatus 2 (batteryNormal) is OK, 3 (batteryLow) and 4
(batteryDepleted) make the service CRIT, any other value WARN.
upsSecondsOnBattery above 0 makes it WARN. ups1batteryAbnormal or
ups1batteryPowered at 1 makes it WARN, ups1batteryLowVoltage at 1 CRIT.
The plugin fetches ups1batteryStatus, but no service evaluates it.

### Battery Charge Service

| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.18.0 | ups1remainingCapacityOfBattery | 100 | % | WARN: 20%, CRIT: 10% |

### Battery Runtime Service

| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.17.0 | ups1batteryTimeRemaining | 15 | minutes → seconds | WARN: 600s, CRIT: 300s |

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
| .1.3.6.1.4.1.44782.1.4.4.1.80.0 | ups1bypassStatus | 0 | flag |

The example values are those of a UPS on mains, for which the service is OK.
upsOutputSource 4 (bypass) or 5 (battery) makes it WARN, any other value than
3 (normal) makes it CRIT. upsBaseOutputStatus 2 (onLine) is OK, 1 (unknown)
is ignored, 3, 4, 6, 9, 12, 13 and 15 make it WARN, and 5, 7, 8, 10, 11 and 14
make it CRIT (names under "Base Output Status" below).
upsInputLineBads counts the mains failures since the card started. The
service shows the total and goes WARN when the count rose since the last
check; the first check and a count that went down (card restart) stay OK.
Any of the three flags at 1 makes it WARN: ups1bypassStatus 1 shows as
"Bypass active".

### Alarm Status Service
Monitors system alarms and critical conditions.

| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.4.1.44782.1.4.4.1.71.0 | ups1abnormalCommunication | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.76.0 | ups1temperatureAbnormal | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.79.0 | ups1overLoad | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.81.0 | ups1fanFailure | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.85.0 | ups1shutdownRequest | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.86.0 | ups1testInProgress | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.89.0 | ups1shutdownImminent | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.93.0 | ups1lowBatteryShutdownImminent | 0 | flag |
| .1.3.6.1.4.1.44782.1.4.4.1.94.0 | ups1systemStatus | 1 | status |

The example values are those of a UPS without alarm, for which the service
shows "No active alarms". A flag at 1 makes the service WARN, except
ups1abnormalCommunication, ups1shutdownImminent and
ups1lowBatteryShutdownImminent, which make it CRIT. ups1testInProgress 1 shows
as "Warning: Test in progress". ups1systemStatus 1 is normal, 2 makes the
service WARN and 3 makes it CRIT.

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
| .1.3.6.1.4.1.44782.1.4.4.1.19.0 | ups1batteryVoltage | 41.2 | V | WARN: 32V, CRIT: 30V |

#### Battery Current Service
| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.4.1.44782.1.4.4.1.20.0 | ups1batteryChargingAndDischargingCurrent | 0.00 | A |

#### Output Current Service
| OID | Description | Example Value | Unit |
|-----|-------------|---------------|------|
| .1.3.6.1.4.1.44782.1.4.4.1.45.0 | ups1outputUPhaseCurrent | 0.00 | A |

#### Battery Temperature Service
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
| .1.3.6.1.4.1.44782.1.4.4.1.48.0 | ups1outputUPhaseActivePower | 0.00 | kW (the service shows W) |

#### Output Load Service
| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.4.4.1.51.0 | ups1outputUPhaseLoadRate | 0.0 | % | WARN: 80%, CRIT: 90% |

#### Environment Service
Appears only with a THS sensor. The card sends the values in tenths.

| OID | Description | Example Value | Unit | Thresholds |
|-----|-------------|---------------|------|------------|
| .1.3.6.1.4.1.44782.1.2.1.1.1.0 | thsOneTempData | 243 | 0.1 °C → °C | WARN: 35°C/10°C, CRIT: 40°C/5°C |
| .1.3.6.1.4.1.44782.1.2.1.1.2.0 | thsOneHumiData | 456 | 0.1 % → % | WARN: 70%/20%, CRIT: 80%/10% |

## Configuration OIDs

The device provides configuration thresholds, and the plugin fetches them.
They do not change the levels at present: the default levels of the
"OPOSS Wiseways UPS" rule always apply.

| OID | Description | Example Value | Used In Service |
|-----|-------------|---------------|-----------------|
| .1.3.6.1.4.1.44782.1.1.3.1.0 | inputVoltUpConfig | 242 | Input Voltage |
| .1.3.6.1.4.1.44782.1.1.3.2.0 | inputVoltLowConfig | 187 | Input Voltage |
| .1.3.6.1.4.1.44782.1.1.3.3.0 | outputVoltUpConfig | 225 | Output Voltage |
| .1.3.6.1.4.1.44782.1.1.3.4.0 | outputVoltLowConfig | 215 | Output Voltage |
| .1.3.6.1.4.1.44782.1.1.3.5.0 | upsTempUpConfig | 40 | Temperature |
| .1.3.6.1.4.1.44782.1.1.3.6.0 | upsOutputLoadUpConfig | 0 | Output Load |
| .1.3.6.1.4.1.44782.1.1.3.7.0 | upsBatteryVoltLowConfig | 33 | Battery Voltage |

## Data Conversions

The plugin performs the following conversions:

- **Enterprise string values**: Parsed as floats, for example "231.9" → 231.9; a comma is accepted as decimal separator
- **Minutes to seconds**: Battery runtime converted for consistent time metrics
- **Tenths**: THS sensor values, for example 243 → 24.3 °C
- **No value**: -99998 means the UPS has no value; the measurement services go UNKNOWN with "... data not available", and an empty value or -99998 counts as no THS sensor
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

The plugin creates 19 CheckMK services:

1. **UPS System Info** - Static information and configuration
2. **UPS Battery Status** - Battery status, time on battery and battery alarms
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
13. **UPS Battery Temperature** - Battery temperature monitoring
14. **UPS Input Frequency** - Input frequency monitoring
15. **UPS Output Frequency** - Output frequency monitoring
16. **UPS Bypass Frequency** - Bypass frequency monitoring
17. **UPS Output Power** - Power consumption in watts
18. **UPS Output Load** - Load percentage monitoring
19. **UPS Environment** - THS sensor temperature and humidity

## Notes

- Each value comes from the one OID listed for it; there is no fallback between the enterprise OIDs (44782) and RFC 1628
- All time metrics are stored in seconds (SI base unit)
- Thresholds can be customized with the rule "OPOSS Wiseways UPS" under Setup > Services > Service monitoring rules
- Model identified as Wiseway UPS with various capacity ratings (6000VA, 10kVA)
