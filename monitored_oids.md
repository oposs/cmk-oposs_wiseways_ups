# Wiseway UPS - Monitored OIDs

## Overview
This document lists the SNMP OIDs that need to be monitored for the Wiseway UPS device (Model: 6000VA). These OIDs are highlighted in yellow in the source documentation and will be implemented in the CheckMK SNMP plugin.

## Standard UPS MIB OIDs (RFC 1628)

### UPS Identity
- **upsIdentModel** (.1.3.6.1.2.1.33.1.1.2.0) - "6000VA"
- **upsIdentUPSSoftwareVersion** (.1.3.6.1.2.1.33.1.1.3.0) - "VER 6.xxx"

### UPS Battery Status
- **upsBatteryStatus** (.1.3.6.1.2.1.33.1.2.1.0) - 2 (batteryNormal)
- **upsSecondsOnBattery** (.1.3.6.1.2.1.33.1.2.2.0) - 0
- **upsEstimatedMinutesRemaining** (.1.3.6.1.2.1.33.1.2.3.0) - 15 minutes

### UPS Battery Measurements
- **upsBatteryVoltage** (.1.3.6.1.2.1.33.1.2.5.0) - 2179 (217.9V)
- **upsBatteryCurrent** (.1.3.6.1.2.1.33.1.2.6.0) - 0
- **upsBatteryTemperature** (.1.3.6.1.2.1.33.1.2.7.0) - 28 to -29°C

### UPS Input
- **upsInputLineBads** (.1.3.6.1.2.1.33.1.3.1.0) - 0
- **upsInputNumLines** (.1.3.6.1.2.1.33.1.3.2.0) - 1
- **upsInputFrequency** (.1.3.6.1.2.1.33.1.3.3.1.2.1) - 500 (50.0 Hz)
- **upsInputVoltage** (.1.3.6.1.2.1.33.1.3.3.1.3.1) - 233 to 229V

### UPS Output  
- **upsOutputSource** (.1.3.6.1.2.1.33.1.4.1.0) - 3 (normal)
- **upsOutputFrequency** (.1.3.6.1.2.1.33.1.4.2.0) - 500 (50.0 Hz)
- **upsOutputNumLines** (.1.3.6.1.2.1.33.1.4.3.0) - 1
- **upsOutputVoltage** (.1.3.6.1.2.1.33.1.4.4.1.2.1) - 233 to 229V
- **upsOutputCurrent** (.1.3.6.1.2.1.33.1.4.4.1.3.1) - 0
- **upsOutputPower** (.1.3.6.1.2.1.33.1.4.4.1.4.1) - 0W
- **upsOutputPercentLoad** (.1.3.6.1.2.1.33.1.4.4.1.5.1) - 0%

### UPS Bypass
- **upsBypassFrequency** (.1.3.6.1.2.1.33.1.5.1.0) - 500 (50.0 Hz)

## Enterprise-Specific OIDs

### Additional Battery Information
- **upsBaseBatteryStatus** (.1.3.6.1.4.1.935.1.1.1.2.1.1.0) - 2
- **upsBaseBatteryTimeOnBattery** (.1.3.6.1.4.1.935.1.1.1.2.1.2.0) - 0
- **upsSmartBatteryCapacity** (.1.3.6.1.4.1.935.1.1.1.2.2.1.0) - 100%
- **upsSmartBatteryRunTimeRemaining** (.1.3.6.1.4.1.935.1.1.1.2.2.4.0) - 900 (15 min)
- **upsSmartInputLineVoltage** (.1.3.6.1.4.1.935.1.1.1.3.2.1.0) - 2329 to 2298
- **upsBaseOuputStatus** (.1.3.6.1.4.1.935.1.1.1.4.1.1.0) - 1

### Additional System Status (Proprietary OIDs)
- **ups1batteryStatus** (.1.3.6.1.4.1.44782.1.4.4.1.16.0) - "2"
- **ups1batteryTimeRemaining** (.1.3.6.1.4.1.44782.1.4.4.1.17.0) - "15"
- **ups1remainingCapacityOfBattery** (.1.3.6.1.4.1.44782.1.4.4.1.18.0) - "100"
- **ups1batteryTemperature** (.1.3.6.1.4.1.44782.1.4.4.1.21.0) - "28.0" to "29.0"
- **ups1inputUPhaseVoltage** (.1.3.6.1.4.1.44782.1.4.4.1.27.0) - "231.9" to "229.4"
- **ups1powerSupplyMode** (.1.3.6.1.4.1.44782.1.4.4.1.39.0) - "3"
- **ups1outputUPhaseVoltage** (.1.3.6.1.4.1.44782.1.4.4.1.42.0) - "231.9" to "229.4"
- **ups1outputPhaseLoadRate** (.1.3.6.1.4.1.44782.1.4.4.1.51.0) - "0"
- **ups1bypassUPhaseVoltage** (.1.3.6.1.4.1.44782.1.4.4.1.59.0) - "232.9" to "229.8"

## Key Metrics to Monitor

Based on the highlighted OIDs, the following metrics should be monitored:

1. **Battery Health**
   - Battery status (normal/charging/discharging)
   - Battery charge percentage
   - Battery runtime remaining
   - Battery voltage
   - Battery temperature

2. **Power Input**
   - Input voltage
   - Input frequency
   - Input line failures

3. **Power Output**
   - Output voltage
   - Output frequency
   - Output current
   - Output power (watts)
   - Output load percentage

4. **System Status**
   - UPS operational status
   - Power supply mode
   - Bypass voltage and frequency

## Notes
- Values are provided in various units (decivolts, centihertz, etc.) and need conversion
- Temperature readings show some variation between different OIDs
- The device supports both standard RFC 1628 MIB and proprietary OIDs
- Model identified as "6000VA" Wiseway UPS