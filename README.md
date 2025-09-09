# CheckMK Wiseways UPS SNMP Plugin

A comprehensive CheckMK SNMP plugin for monitoring Wiseways UPS devices (6000VA, 10kVA and compatible models).

## Overview

This plugin provides complete monitoring of Wiseways UPS systems via SNMP with 18 specialized services covering every aspect of UPS operation:

- **System Information**: Model, serial number, firmware versions, maintenance schedules
- **Battery Monitoring**: Individual services for charge, runtime, status, and alarms
- **Power Monitoring**: Separate services for input/output/bypass/battery voltages
- **Load Management**: Output load percentage, power consumption, and current monitoring
- **Frequency Stability**: Individual monitoring for input/output/bypass frequencies
- **Alarm System**: Comprehensive alarm detection and status reporting

## Features

- **18 Specialized Services**: Each monitoring aspect has its own dedicated service for granular control
- **Automatic Data Normalization**: Converts SNMP values to standard units (decivolts→volts, minutes→seconds)
- **Maintenance Monitoring**: Automatic warnings for expired maintenance and battery service schedules
- **Smart Graph Organization**: Unit-based grouping for combined overview graphs
- **Dynamic Thresholds**: Uses device configuration values as defaults when available
- **Enterprise & Standard MIB Support**: Works with both RFC 1628 standard UPS MIB and Wiseways enterprise OIDs (44782)

## Installation

### Standard Installation (Recommended)

1. Download the latest MKP package from [GitHub Releases](https://github.com/oposs/cmk-oposs_wiseways_ups/releases)

2. Install the MKP in CheckMK:
   ```bash
   cmk -P install oposs_wiseways_ups-<version>.mkp
   ```

3. Run service discovery on your UPS hosts:
   ```bash
   cmk -II <hostname>
   ```

### Manual Installation (Developers)

For development or manual installation:

1. Copy the plugin files to your CheckMK site:
   ```bash
   cp -r local/* ~/local/
   ```

2. Reload CheckMK to recognize the new plugin:
   ```bash
   cmk -R
   ```

3. Run service discovery on your UPS hosts:
   ```bash
   cmk -II <hostname>
   ```

## Configuration

### SNMP Setup

Ensure your Wiseways UPS is accessible via SNMP:

1. Configure SNMP community string on the UPS
2. Add the UPS as a host in CheckMK with SNMP monitoring enabled
3. Set the appropriate SNMP community in CheckMK host properties

### Service Discovery

The plugin will automatically discover up to 18 services per UPS:

#### Information Services
- **UPS System Info**: Model, serial, firmware, maintenance dates
- **UPS Battery Status**: Battery state and alarms (without charge/runtime)
- **UPS Power Status**: Power source, operational mode, line failures
- **UPS Alarm Status**: System-wide alarm monitoring

#### Battery Monitoring Services
- **UPS Battery Charge**: Battery charge percentage
- **UPS Battery Runtime**: Remaining runtime in seconds
- **UPS Battery Voltage**: DC battery voltage
- **UPS Battery Current**: Charging/discharging current
- **UPS Battery Temperature**: Battery temperature monitoring

#### Voltage Monitoring Services  
- **UPS Input Voltage**: AC input voltage
- **UPS Output Voltage**: AC output voltage
- **UPS Bypass Voltage**: Bypass line voltage (when available)

#### Frequency Monitoring Services
- **UPS Input Frequency**: Input frequency stability
- **UPS Output Frequency**: Output frequency stability
- **UPS Bypass Frequency**: Bypass frequency (when available)

#### Load and Power Services
- **UPS Output Load**: Load percentage monitoring
- **UPS Output Power**: Power consumption in watts
- **UPS Output Current**: Output current monitoring

### Threshold Configuration

Configure monitoring thresholds in CheckMK under "Setup" > "Services" > "Service monitoring rules" > "OPOSS Wiseways UPS":

All thresholds can be configured through a single unified ruleset that applies to all relevant services:

#### Battery Thresholds
- **Battery Charge** (`battery_charge_lower`): Warning at 20%, Critical at 10%
- **Battery Runtime** (`battery_runtime_lower`): Warning at 10 minutes, Critical at 5 minutes
- **Battery Voltage** (`battery_voltage_lower`): Warning at 180V, Critical at 170V
- **Battery Temperature** (`temp_upper/temp_lower`): Warning at 40°C/10°C, Critical at 45°C/5°C

#### Voltage Thresholds
- **Input Voltage** (`input_voltage_upper/lower`): Warning at 250V/210V, Critical at 260V/200V
- **Output Voltage** (`output_voltage_upper/lower`): Warning at 250V/210V, Critical at 260V/200V
- **Bypass Voltage** (`bypass_voltage_upper/lower`): Warning at 250V/210V, Critical at 260V/200V

#### Frequency Thresholds
- **All Frequencies** (`frequency_upper/lower`): Warning at 51Hz/49Hz, Critical at 52Hz/48Hz

#### Load and Power Thresholds
- **Output Load** (`load_upper`): Warning at 80%, Critical at 90%
- **Output Current** (`output_current_upper`): Configurable, no default
- **Output Power** (`power_upper`): Configurable, no default

Note: The plugin uses device-reported configuration values as dynamic defaults when available (e.g., input voltage limits from the UPS configuration).

## Metrics and Graphs

### Graph Organization

The plugin provides two types of graphs:

#### Service-Specific Graphs
Each service displays its own dedicated graph with relevant metrics and thresholds.

#### Combined Overview Graphs (Host Level)
These graphs combine metrics from multiple services for comparative analysis:

1. **UPS All Voltages**: All voltages (input, output, bypass, battery) on one graph
2. **UPS AC Voltages**: AC voltages only (input, output, bypass)
3. **UPS Frequencies**: All frequencies (input, output, bypass) together
4. **UPS Currents**: Output and battery currents combined
5. **UPS Battery Time**: Runtime and time-on-battery metrics

### Metric Units

All metrics use base SI units for consistency:
- **Time**: seconds (converted from minutes in SNMP)
- **Voltage**: volts (converted from decivolts or string format)
- **Frequency**: hertz (converted from centihertz or string format)
- **Temperature**: degrees Celsius
- **Power**: watts
- **Current**: amperes
- **Charge**: percentage
- **Load**: percentage

## Supported OIDs

The plugin monitors both standard RFC 1628 UPS MIB OIDs and Wiseways enterprise-specific OIDs:

### Standard MIB (.1.3.6.1.2.1.33)
- UPS identification and status
- Battery metrics
- Input/output electrical parameters
- Bypass parameters

### Enterprise OIDs
- `.1.3.6.1.4.1.935` - Enhanced battery metrics
- `.1.3.6.1.4.1.44782` - Wiseways-specific high-precision values

## Requirements

- CheckMK 2.3 or later
- SNMP v1/v2c access to the UPS
- Wiseways UPS with SNMP support (tested with 6000VA model)

## Troubleshooting

### No Services Discovered

1. Verify SNMP connectivity:
   ```bash
   snmpwalk -v2c -c <community> <ups_ip> .1.3.6.1.2.1.33.1.1.5.0
   ```
   This should return a string containing "Wiseway3" for compatible devices.

2. Check SNMP configuration in CheckMK host settings

3. Ensure the UPS supports standard UPS MIB and/or Wiseways enterprise OIDs

4. Run manual discovery:
   ```bash
   cmk -vvI --detect-plugins=oposs_wiseways_ups <hostname>
   ```

### Fewer Than 18 Services

Not all services may be discovered depending on UPS capabilities:
- Bypass services only appear if bypass voltage/frequency data is available
- Battery current may not be available on all models
- Some older models may not report all metrics

### Incorrect Values

- The plugin automatically converts enterprise string format values (e.g., "231.9") to floats
- Minutes are converted to seconds for all time-based metrics
- Special value -99998 indicates unavailable data and is handled gracefully

### Missing Graphs

- Individual service graphs appear with their respective services
- Combined overview graphs appear at the host level (not under specific services)
- This is the intended behavior for cross-service visualization

## License

This plugin is provided as-is for monitoring Wiseways UPS devices in CheckMK environments.

## Support

For issues or feature requests, please refer to the project documentation or contact your system administrator.