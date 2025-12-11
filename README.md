# CheckMK Wiseways UPS SNMP Plugin

A CheckMK SNMP plugin for monitoring Wiseways UPS devices (6000VA, 10kVA and compatible models).

## Features

- 19 specialized services for granular monitoring and alerting
- Automatic unit conversion (decivolts→volts, minutes→seconds)
- Dynamic thresholds from device configuration when available
- Maintenance expiration warnings
- Support for RFC 1628 UPS MIB and Wiseways enterprise OIDs (44782)
- THS environmental sensor support (temperature/humidity)

## Installation

### From MKP Package (Recommended)

```bash
# Download from https://github.com/oposs/cmk-oposs_wiseways_ups/releases
cmk -P install oposs_wiseways_ups-<version>.mkp
cmk -II <hostname>
```

### Manual Installation

```bash
cp -r local/* ~/local/
cmk -R
cmk -II <hostname>
```

## SNMP Setup

1. Configure SNMP community string on the UPS
2. Add the UPS as a host in CheckMK with SNMP monitoring enabled
3. Set the appropriate SNMP community in CheckMK host properties

## Services and Thresholds

Configure thresholds under "Setup" > "Services" > "Service monitoring rules" > "OPOSS Wiseways UPS".

| Service | Description | Default Thresholds (Warn/Crit) |
|---------|-------------|-------------------------------|
| **UPS System Info** | Model, serial, firmware, maintenance dates | Warns on expired maintenance |
| **UPS Battery Status** | Battery state and alarms | — |
| **UPS Power Status** | Power source, mode, line failures | — |
| **UPS Alarm Status** | System-wide alarm monitoring | — |
| **UPS Battery Charge** | Battery charge % | Lower: 20%/10% |
| **UPS Battery Runtime** | Remaining runtime | Lower: 10min/5min |
| **UPS Battery Voltage** | DC battery voltage | Lower: 180V/170V |
| **UPS Battery Current** | Charging/discharging current | — |
| **UPS Battery Temperature** | Battery temperature | Upper: 40°C/45°C, Lower: 10°C/5°C |
| **UPS Input Voltage** | AC input voltage | Upper: 250V/260V, Lower: 210V/200V |
| **UPS Output Voltage** | AC output voltage | Upper: 250V/260V, Lower: 210V/200V |
| **UPS Bypass Voltage** | Bypass line voltage | Upper: 250V/260V, Lower: 210V/200V |
| **UPS Input Frequency** | Input frequency | Upper: 51Hz/52Hz, Lower: 49Hz/48Hz |
| **UPS Output Frequency** | Output frequency | Upper: 51Hz/52Hz, Lower: 49Hz/48Hz |
| **UPS Bypass Frequency** | Bypass frequency | Upper: 51Hz/52Hz, Lower: 49Hz/48Hz |
| **UPS Output Load** | Load percentage | Upper: 80%/90% |
| **UPS Output Power** | Power consumption (W) | — |
| **UPS Output Current** | Output current (A) | — |
| **UPS Environment** | THS sensor temp/humidity | Temp: 35°C/40°C (upper), 10°C/5°C (lower); Humidity: 70%/80% (upper), 20%/10% (lower) |

Services marked "—" have no default thresholds but can be configured. Bypass and Environment services only appear when hardware is present.

## Graphs

Each service has its own graph. Additional combined graphs at host level:

- **UPS All Voltages** / **UPS AC Voltages**: Compare voltage sources
- **UPS Frequencies**: All frequencies together
- **UPS Currents**: Output and battery currents
- **UPS Battery Time**: Runtime and time-on-battery
- **UPS Environment**: Temperature and humidity

## Requirements

- CheckMK 2.3 or later
- SNMP v1/v2c access to the UPS
- Wiseways UPS with SNMP support

## Troubleshooting

**No services discovered:**
```bash
# Verify SNMP connectivity (should return string containing "Wiseway3")
snmpwalk -v2c -c <community> <ups_ip> .1.3.6.1.2.1.33.1.1.5.0

# Debug discovery
cmk -vvI --detect-plugins=oposs_wiseways_ups <hostname>
```

**Fewer than 19 services:** Normal - bypass, environment, and some battery metrics only appear when supported by hardware.

**Incorrect values:** The plugin handles enterprise string formats and special value -99998 (unavailable data) automatically.

## License

This plugin is provided as-is for monitoring Wiseways UPS devices in CheckMK environments.
