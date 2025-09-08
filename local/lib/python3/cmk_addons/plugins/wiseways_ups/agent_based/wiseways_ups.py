#!/usr/bin/env python3

from typing import Any, Dict, Mapping
from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    SNMPDetectSpecification,
    State,
    check_levels,
    contains,
    exists,
    render,
)


def parse_wiseways_ups(string_table):
    """Parse SNMP data and normalize values"""
    if not string_table or not string_table[0]:
        return {}
    
    row = string_table[0]
    parsed = {}
    
    # Identity information (static)
    parsed["model"] = row[0] if row[0] else "Unknown"
    parsed["software_version"] = row[1] if row[1] else "Unknown"
    
    # Battery status mapping
    battery_status_map = {
        "1": "unknown",
        "2": "batteryNormal", 
        "3": "batteryLow",
        "4": "batteryDepleted",
    }
    parsed["battery_status"] = battery_status_map.get(row[2], "unknown")
    
    # Battery metrics - use most precise values
    parsed["battery_charge_percent"] = float(row[3]) if row[3] else 0.0
    
    # Runtime: prefer enterprise OID (row[4]) over standard (row[5]) if available
    # Convert minutes to seconds for base SI unit
    if row[4] and row[4] != "0":
        parsed["battery_runtime_seconds"] = float(row[4]) * 60
    elif row[5] and row[5] != "0":
        parsed["battery_runtime_seconds"] = float(row[5]) * 60
    else:
        parsed["battery_runtime_seconds"] = 0.0
    
    # Battery voltage - convert decivolts to volts
    parsed["battery_voltage"] = float(row[6]) / 10 if row[6] else 0.0
    
    # Battery temperature - use enterprise OID for better precision
    if row[7] and row[7] != "0":  # Enterprise OID with decimal
        try:
            parsed["battery_temperature"] = float(row[7])
        except ValueError:
            parsed["battery_temperature"] = 0.0
    elif row[8] and row[8] != "0":  # Standard OID
        parsed["battery_temperature"] = float(row[8])
    else:
        parsed["battery_temperature"] = 0.0
    
    # Input metrics
    parsed["input_line_bads"] = int(row[9]) if row[9] else 0
    
    # Input voltage - prefer enterprise OID for precision
    if row[10] and row[10] != "0":  # Enterprise OID (already in volts with decimal)
        try:
            # Handle values like "2329→2298" by taking first value
            voltage_str = row[10].split("→")[0].strip()
            # Convert from centivolt-like format if needed
            if float(voltage_str) > 1000:
                parsed["input_voltage"] = float(voltage_str) / 10
            else:
                parsed["input_voltage"] = float(voltage_str)
        except (ValueError, IndexError):
            parsed["input_voltage"] = 0.0
    elif row[11] and row[11] != "0":  # Standard OID in decivolts
        parsed["input_voltage"] = float(row[11]) / 10
    else:
        parsed["input_voltage"] = 0.0
    
    # Input frequency - convert centihertz to hertz
    parsed["input_frequency"] = float(row[12]) / 100 if row[12] else 0.0
    
    # Output source mapping
    output_source_map = {
        "1": "other",
        "2": "none", 
        "3": "normal",
        "4": "bypass",
        "5": "battery",
        "6": "booster",
        "7": "reducer",
    }
    parsed["output_source"] = output_source_map.get(row[13], "unknown")
    
    # Output voltage - prefer enterprise OID
    if row[14] and row[14] != "0":  # Enterprise OID
        try:
            voltage_str = row[14].split("→")[0].strip()
            if float(voltage_str) > 1000:
                parsed["output_voltage"] = float(voltage_str) / 10
            else:
                parsed["output_voltage"] = float(voltage_str)
        except (ValueError, IndexError):
            parsed["output_voltage"] = 0.0
    elif row[15] and row[15] != "0":  # Standard OID
        parsed["output_voltage"] = float(row[15]) / 10
    else:
        parsed["output_voltage"] = 0.0
    
    # Output frequency - convert centihertz to hertz
    parsed["output_frequency"] = float(row[16]) / 100 if row[16] else 0.0
    
    # Output power metrics
    parsed["output_current"] = float(row[17]) / 10 if row[17] else 0.0  # Deciamps to amps
    parsed["output_power_watts"] = float(row[18]) if row[18] else 0.0
    
    # Output load - prefer enterprise OID for consistency
    if row[19] and row[19] != "0":  # Enterprise OID
        parsed["output_load_percent"] = float(row[19])
    elif row[20] and row[20] != "0":  # Standard OID
        parsed["output_load_percent"] = float(row[20])
    else:
        parsed["output_load_percent"] = 0.0
    
    # Bypass voltage - prefer enterprise OID
    if row[21] and row[21] != "0":  # Enterprise OID
        try:
            voltage_str = row[21].split("→")[0].strip()
            if float(voltage_str) > 1000:
                parsed["bypass_voltage"] = float(voltage_str) / 10
            else:
                parsed["bypass_voltage"] = float(voltage_str)
        except (ValueError, IndexError):
            parsed["bypass_voltage"] = 0.0
    elif row[22] and row[22] != "0":  # Standard OID
        parsed["bypass_voltage"] = float(row[22]) / 10
    else:
        parsed["bypass_voltage"] = 0.0
    
    # Bypass frequency - convert centihertz to hertz
    parsed["bypass_frequency"] = float(row[23]) / 100 if row[23] else 0.0
    
    return parsed


snmp_section_wiseways_ups = SimpleSNMPSection(
    name="wiseways_ups",
    parse_function=parse_wiseways_ups,
    fetch=SNMPTree(
        base=".1.3.6.1",
        oids=[
            "2.1.33.1.1.2.0",   # upsIdentModel
            "2.1.33.1.1.3.0",   # upsIdentUPSSoftwareVersion
            "2.1.33.1.2.1.0",   # upsBatteryStatus
            "4.1.935.1.1.1.2.2.1.0",  # upsSmartBatteryCapacity (prefer for precision)
            "4.1.44782.1.4.4.1.17.0", # ups1batteryTimeRemaining (minutes, enterprise)
            "2.1.33.1.2.3.0",   # upsEstimatedMinutesRemaining (fallback)
            "2.1.33.1.2.5.0",   # upsBatteryVoltage (decivolts)
            "4.1.44782.1.4.4.1.21.0", # ups1batteryTemperature (more precise)
            "2.1.33.1.2.7.0",   # upsBatteryTemperature (fallback)
            "2.1.33.1.3.1.0",   # upsInputLineBads
            "4.1.44782.1.4.4.1.27.0", # ups1inputUPhaseVoltage (precise)
            "2.1.33.1.3.3.1.3.1", # upsInputVoltage (fallback)
            "2.1.33.1.3.3.1.2.1", # upsInputFrequency (centihertz)
            "2.1.33.1.4.1.0",   # upsOutputSource
            "4.1.44782.1.4.4.1.42.0", # ups1outputUPhaseVoltage (precise)
            "2.1.33.1.4.4.1.2.1", # upsOutputVoltage (fallback)
            "2.1.33.1.4.2.0",   # upsOutputFrequency (centihertz)
            "2.1.33.1.4.4.1.3.1", # upsOutputCurrent (deciamps)
            "2.1.33.1.4.4.1.4.1", # upsOutputPower (watts)
            "4.1.44782.1.4.4.1.51.0", # ups1outputPhaseLoadRate (precise)
            "2.1.33.1.4.4.1.5.1", # upsOutputPercentLoad (fallback)
            "4.1.44782.1.4.4.1.59.0", # ups1bypassUPhaseVoltage (precise)
            "2.1.33.1.5.3.1.3.1", # upsBypassVoltage (fallback)
            "2.1.33.1.5.1.0",   # upsBypassFrequency (centihertz)
        ],
    ),
    detect=SNMPDetectSpecification(
        exists(".1.3.6.1.2.1.33.1.1.1.0")  # upsIdentManufacturer
    ),
)


# Check plugin for UPS Info (static information)
def discover_wiseways_ups_info(section: Dict[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def check_wiseways_ups_info(section: Dict[str, Any]) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    yield Result(
        state=State.OK,
        summary=f"Model: {section['model']}, Software: {section['software_version']}"
    )


check_plugin_wiseways_ups_info = CheckPlugin(
    name="wiseways_ups_info",
    service_name="UPS Info",
    sections=["wiseways_ups"],
    discovery_function=discover_wiseways_ups_info,
    check_function=check_wiseways_ups_info,
)


# Check plugin for UPS Battery
def discover_wiseways_ups_battery(section: Dict[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def check_wiseways_ups_battery(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    # Battery status
    status = section.get("battery_status", "unknown")
    if status == "batteryNormal":
        state = State.OK
    elif status in ["batteryLow", "batteryDepleted"]:
        state = State.CRIT
    else:
        state = State.WARN
    yield Result(state=state, summary=f"Status: {status}")
    
    # Battery charge
    yield from check_levels(
        section.get("battery_charge_percent", 0),
        levels_lower=params.get("battery_charge_lower"),
        metric_name="battery_charge",
        label="Charge",
        render_func=render.percent,
        boundaries=(0, 100),
    )
    
    # Runtime (in seconds)
    yield from check_levels(
        section.get("battery_runtime_seconds", 0),
        levels_lower=params.get("battery_runtime_lower"),
        metric_name="battery_runtime",
        label="Runtime",
        render_func=render.timespan,
    )
    
    # Battery voltage
    voltage = section.get("battery_voltage", 0)
    if voltage > 0:
        yield Metric("battery_voltage", voltage)
        yield Result(state=State.OK, notice=f"Battery voltage: {voltage:.1f}V")
    
    # Temperature
    yield from check_levels(
        section.get("battery_temperature", 0),
        levels_upper=params.get("battery_temp_upper"),
        levels_lower=params.get("battery_temp_lower"),
        metric_name="battery_temperature",
        label="Temperature",
        render_func=lambda v: f"{v:.1f}°C",
    )


check_plugin_wiseways_ups_battery = CheckPlugin(
    name="wiseways_ups_battery",
    service_name="UPS Battery",
    sections=["wiseways_ups"],
    discovery_function=discover_wiseways_ups_battery,
    check_function=check_wiseways_ups_battery,
    check_ruleset_name="wiseways_ups_battery",
    check_default_parameters={
        "battery_charge_lower": ("fixed", (20.0, 10.0)),
        "battery_runtime_lower": ("fixed", (600.0, 300.0)),  # 10min, 5min in seconds
        "battery_temp_upper": ("fixed", (40.0, 45.0)),
        "battery_temp_lower": ("fixed", (10.0, 5.0)),
    },
)


# Check plugin for UPS Power (voltages)
def discover_wiseways_ups_power(section: Dict[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def check_wiseways_ups_power(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    # Output source status
    source = section.get("output_source", "unknown")
    if source == "normal":
        state = State.OK
    elif source in ["battery", "bypass"]:
        state = State.WARN
    else:
        state = State.CRIT
    yield Result(state=state, summary=f"Power source: {source}")
    
    # Input voltage
    yield from check_levels(
        section.get("input_voltage", 0),
        levels_upper=params.get("input_voltage_upper"),
        levels_lower=params.get("input_voltage_lower"),
        metric_name="input_voltage",
        label="Input voltage",
        render_func=lambda v: f"{v:.1f}V",
    )
    
    # Output voltage
    yield from check_levels(
        section.get("output_voltage", 0),
        levels_upper=params.get("output_voltage_upper"),
        levels_lower=params.get("output_voltage_lower"),
        metric_name="output_voltage",
        label="Output voltage",
        render_func=lambda v: f"{v:.1f}V",
    )
    
    # Bypass voltage
    bypass_v = section.get("bypass_voltage", 0)
    if bypass_v > 0:
        yield Metric("bypass_voltage", bypass_v)
        yield Result(state=State.OK, notice=f"Bypass voltage: {bypass_v:.1f}V")
    
    # Input line failures
    line_bads = section.get("input_line_bads", 0)
    if line_bads > 0:
        yield Result(state=State.WARN, summary=f"Input line failures: {line_bads}")
    yield Metric("input_line_bads", line_bads)


check_plugin_wiseways_ups_power = CheckPlugin(
    name="wiseways_ups_power",
    service_name="UPS Power",
    sections=["wiseways_ups"],
    discovery_function=discover_wiseways_ups_power,
    check_function=check_wiseways_ups_power,
    check_ruleset_name="wiseways_ups_power",
    check_default_parameters={
        "input_voltage_upper": ("fixed", (250.0, 260.0)),
        "input_voltage_lower": ("fixed", (210.0, 200.0)),
        "output_voltage_upper": ("fixed", (250.0, 260.0)),
        "output_voltage_lower": ("fixed", (210.0, 200.0)),
    },
)


# Check plugin for UPS Load
def discover_wiseways_ups_load(section: Dict[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def check_wiseways_ups_load(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    # Output load percentage
    yield from check_levels(
        section.get("output_load_percent", 0),
        levels_upper=params.get("load_upper"),
        metric_name="output_load",
        label="Load",
        render_func=render.percent,
        boundaries=(0, 100),
    )
    
    # Output power
    power = section.get("output_power_watts", 0)
    yield Metric("output_power", power)
    if power > 0:
        yield Result(state=State.OK, notice=f"Output power: {power:.0f}W")
    
    # Output current
    current = section.get("output_current", 0)
    yield Metric("output_current", current)
    if current > 0:
        yield Result(state=State.OK, notice=f"Output current: {current:.1f}A")


check_plugin_wiseways_ups_load = CheckPlugin(
    name="wiseways_ups_load",
    service_name="UPS Load",
    sections=["wiseways_ups"],
    discovery_function=discover_wiseways_ups_load,
    check_function=check_wiseways_ups_load,
    check_ruleset_name="wiseways_ups_load",
    check_default_parameters={
        "load_upper": ("fixed", (80.0, 90.0)),
    },
)


# Check plugin for UPS Frequency
def discover_wiseways_ups_frequency(section: Dict[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def check_wiseways_ups_frequency(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    # Input frequency
    yield from check_levels(
        section.get("input_frequency", 0),
        levels_upper=params.get("frequency_upper"),
        levels_lower=params.get("frequency_lower"),
        metric_name="input_frequency",
        label="Input frequency",
        render_func=lambda v: f"{v:.1f} Hz",
    )
    
    # Output frequency
    yield from check_levels(
        section.get("output_frequency", 0),
        levels_upper=params.get("frequency_upper"),
        levels_lower=params.get("frequency_lower"),
        metric_name="output_frequency",
        label="Output frequency",
        render_func=lambda v: f"{v:.1f} Hz",
    )
    
    # Bypass frequency
    bypass_freq = section.get("bypass_frequency", 0)
    if bypass_freq > 0:
        yield Metric("bypass_frequency", bypass_freq)
        yield Result(state=State.OK, notice=f"Bypass frequency: {bypass_freq:.1f} Hz")


check_plugin_wiseways_ups_frequency = CheckPlugin(
    name="wiseways_ups_frequency",
    service_name="UPS Frequency",
    sections=["wiseways_ups"],
    discovery_function=discover_wiseways_ups_frequency,
    check_function=check_wiseways_ups_frequency,
    check_ruleset_name="wiseways_ups_frequency",
    check_default_parameters={
        "frequency_upper": ("fixed", (51.0, 52.0)),
        "frequency_lower": ("fixed", (49.0, 48.0)),
    },
)