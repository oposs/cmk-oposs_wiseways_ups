# CheckMK Wiseways UPS SNMP Plugin

A comprehensive CheckMK SNMP plugin for monitoring Wiseways UPS devices (6000VA and compatible models).

## Overview

This plugin provides complete monitoring of Wiseways UPS systems via SNMP, including:

- **System Information**: Model identification and software version
- **Battery Status**: Charge level, runtime, voltage, temperature, and health status
- **Power Monitoring**: Input/output/bypass voltages with deviation alerts
- **Load Management**: Output load percentage, power consumption, and current draw
- **Frequency Stability**: Input/output/bypass frequency monitoring

## Features

- **Automatic Data Normalization**: Converts SNMP values to standard units (decivolts→volts, centihertz→Hz)
- **Intelligent OID Selection**: Automatically uses the most precise OID when multiple sources provide the same metric
- **Multi-line Graphs**: Logically groups related metrics (all voltages, all frequencies) for easy comparison
- **Comprehensive Thresholds**: Configurable warning/critical levels for all metrics
- **Enterprise & Standard MIB Support**: Works with both RFC 1628 standard UPS MIB and Wiseways enterprise OIDs

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

The plugin will automatically discover 5 services per UPS:

- **UPS Info**: Static identification information (no thresholds)
- **UPS Battery**: Battery health and status monitoring
- **UPS Power**: Voltage monitoring and power source status
- **UPS Load**: Output load and power consumption
- **UPS Frequency**: Frequency stability monitoring

### Threshold Configuration

Configure monitoring thresholds in CheckMK under "Setup" > "Services" > "Service monitoring rules":

#### UPS Battery Thresholds
- **Battery Charge Lower**: Warning at 20%, Critical at 10%
- **Runtime Lower**: Warning at 10 minutes, Critical at 5 minutes
- **Temperature**: Warning at 40°C/10°C, Critical at 45°C/5°C

#### UPS Power Thresholds
- **Input Voltage**: Warning at 210-250V, Critical at 200-260V
- **Output Voltage**: Warning at 210-250V, Critical at 200-260V

#### UPS Load Thresholds
- **Output Load**: Warning at 80%, Critical at 90%

#### UPS Frequency Thresholds
- **Frequency Range**: Warning at 49-51Hz, Critical at 48-52Hz

## Metrics and Graphs

### Multi-line Graphs

The plugin creates optimized multi-line graphs for related metrics:

1. **UPS Voltages**: Combines input, output, and bypass voltages on a single graph
2. **UPS Frequencies**: Shows input, output, and bypass frequencies together
3. **Battery Status**: Displays charge percentage and runtime remaining
4. **Load & Power**: Combines load percentage, power (watts), and current

### Metric Units

All metrics use base SI units for consistency:
- Time: seconds (not minutes or milliseconds)
- Voltage: volts (converted from decivolts)
- Frequency: hertz (converted from centihertz)
- Temperature: degrees Celsius
- Power: watts
- Current: amperes

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
   snmpwalk -v2c -c <community> <ups_ip> .1.3.6.1.2.1.33.1.1.1.0
   ```

2. Check SNMP configuration in CheckMK host settings

3. Ensure the UPS supports standard UPS MIB

### Incorrect Values

- Check SNMP OID responses manually to verify data
- The plugin automatically normalizes values and selects the most precise OID
- Temperature readings may vary between OIDs; the plugin uses the most stable source

### Missing Metrics

Some metrics (bypass voltage/frequency) may not be available when the UPS is not in bypass mode. These are marked as optional in graphs.

## License

This plugin is provided as-is for monitoring Wiseways UPS devices in CheckMK environments.

## Support

For issues or feature requests, please refer to the project documentation or contact your system administrator.