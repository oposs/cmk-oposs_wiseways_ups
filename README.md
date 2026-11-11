# CheckMK Wiseways UPS SNMP Plugin

A CheckMK SNMP plugin for monitoring Wiseways UPS devices (6000VA, 10kVA and compatible models).

## Features

- 19 services, one per measurement and one per status group
- Battery time remaining converted from minutes to seconds, THS sensor values from tenths
- Warnings on expired UPS maintenance and on due battery maintenance
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

The rule "OPOSS Wiseways UPS" under "Setup" > "Services" > "Service monitoring
rules" sets the levels of every service marked "yes" in the Rule column. It
applies per host. Its frequency levels apply to all three frequency services,
and its "Temperature" levels to UPS Battery Temperature.

| Service | Shows | Metrics | Default levels (warn/crit) | Rule | Discovered |
|---------|-------|---------|----------------------------|------|------------|
| **UPS System Info** | Model, serial, firmware, ratings, maintenance dates; WARN on expired maintenance or due battery maintenance | none | none | no | always |
| **UPS Battery Status** | Battery status (CRIT on low or depleted, WARN on any other status than normal), time on battery (WARN), battery alarm flags (WARN, CRIT on low voltage) | `time_on_battery` | none | no | always |
| **UPS Power Status** | Power source (WARN on bypass or battery, CRIT on any other source than normal), base output status, input line failures, input, output and bypass flags (WARN) | `input_line_bads` | none | no | always |
| **UPS Alarm Status** | System alarm flags and system status | none | none | no | always |
| **UPS Battery Charge** | Battery charge | `battery_charge` | lower 20/10 % | yes | always |
| **UPS Battery Runtime** | Remaining runtime | `battery_runtime` | lower 10/5 min | yes | always |
| **UPS Battery Voltage** | DC battery voltage | `battery_voltage` | lower 32/30 V | yes | value above 0 |
| **UPS Battery Current** | Charging or discharging current | `battery_current` | none | no | value other than 0 |
| **UPS Battery Temperature** | Battery temperature | `temperature` | upper 40/45 °C, lower 10/5 °C | yes | value above 0 |
| **UPS Input Voltage** | AC input voltage | `input_voltage` | upper 250/260 V, lower 210/200 V | yes | value above 0 |
| **UPS Output Voltage** | AC output voltage | `output_voltage` | upper 250/260 V, lower 210/200 V | yes | value above 0 |
| **UPS Bypass Voltage** | Bypass line voltage | `bypass_voltage` | upper 250/260 V, lower 210/200 V | yes | value above 0 |
| **UPS Input Frequency** | Input frequency | `input_frequency` | upper 51/52 Hz, lower 49/48 Hz | yes | value above 0 |
| **UPS Output Frequency** | Output frequency | `output_frequency` | upper 51/52 Hz, lower 49/48 Hz | yes | value above 0 |
| **UPS Bypass Frequency** | Bypass frequency | `bypass_frequency` | upper 51/52 Hz, lower 49/48 Hz | yes | value above 0 |
| **UPS Output Load** | Load percentage | `output_load` | upper 80/90 % | yes | always |
| **UPS Output Power** | Active output power | `output_power` | none | yes | value above 0 |
| **UPS Output Current** | Output current | `output_current` | none | yes | value above 0 |
| **UPS Environment** | THS sensor temperature and humidity | `env_temperature`, `env_humidity` | temperature upper 35/40 °C, lower 10/5 °C; humidity upper 70/80 %, lower 20/10 % | yes | temperature or humidity above 0 |

A service that is discovered only with a value is found by the service
discovery only while the UPS reports that value. UPS Battery Current, UPS
Output Current and UPS Output Power can read 0 on a UPS on mains without load
and with a charged battery, so they appear only when discovery runs while the
UPS carries a load, charges or runs on battery. Once discovered, a service stays, and UPS Battery Current shows "No
current flow" at 0.

When the UPS sends -99998 (no value) for a measurement, the service goes
UNKNOWN with "... data not available". When it sends text that is not a
number, the service goes UNKNOWN with "...: cannot read 'N/A' as a number".

## Graphs

Checkmk draws each graph in the service given after its name:

- **UPS Battery Charge**: UPS Battery Charge
- **UPS Battery Time Metrics**: UPS Battery Runtime
- **UPS Battery Voltage**: UPS Battery Voltage
- **UPS Battery Temperature**: UPS Battery Temperature
- **UPS Output Load**: UPS Output Load
- **UPS Output Power**: UPS Output Power
- **UPS Currents**: UPS Output Current
- **UPS Environment Temperature**: UPS Environment
- **UPS Environment Humidity**: UPS Environment
- **UPS Alarm Counters**: UPS Power Status

The other measurement services show the standard graph of their metric.

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

**Fewer than 19 services:** The measurement services marked "value above 0" or
"value other than 0" above appear only when the UPS reports that value. Run the
service discovery again while the UPS carries a load to get UPS Output Current
and UPS Output Power, and while it charges or discharges its battery to get UPS
Battery Current.

## License

GNU General Public License v2 - OETIKER+PARTNER AG. See [LICENSE](LICENSE).
