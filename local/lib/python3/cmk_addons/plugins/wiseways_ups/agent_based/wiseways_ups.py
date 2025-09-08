#!/usr/bin/env python3

from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple
from dataclasses import dataclass
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


# Scaling/conversion functions
def decivolts_to_volts(value: str) -> float:
    """Convert decivolts to volts"""
    return float(value) / 10 if value else 0.0

def centihertz_to_hertz(value: str) -> float:
    """Convert centihertz to hertz"""
    return float(value) / 100 if value else 0.0

def deciamps_to_amps(value: str) -> float:
    """Convert deciamps to amps"""
    return float(value) / 10 if value else 0.0

def minutes_to_seconds(value: str) -> float:
    """Convert minutes to seconds"""
    return float(value) * 60 if value else 0.0

def parse_enterprise_voltage(value: str) -> float:
    """Parse voltage value handling enterprise OID format"""
    if not value or value == "0":
        return 0.0
    
    try:
        # Handle values like "2329→2298" by taking first value
        voltage_str = value.split("→")[0].strip()
        voltage_float = float(voltage_str)
        
        # Convert from centivolt-like format if needed
        if voltage_float > 1000:
            return voltage_float / 10
        return voltage_float
    except (ValueError, IndexError):
        return 0.0

def identity_str(value: str) -> str:
    """Return string as-is or default"""
    return value or "Unknown"

def identity_float(value: str) -> float:
    """Convert to float directly"""
    return float(value) if value else 0.0

def identity_int(value: str) -> int:
    """Convert to int directly"""
    return int(value) if value else 0


# Value mappers
BATTERY_STATUS_MAP = {
    "1": "unknown",
    "2": "batteryNormal",
    "3": "batteryLow",
    "4": "batteryDepleted",
}

OUTPUT_SOURCE_MAP = {
    "1": "other",
    "2": "none",
    "3": "normal",
    "4": "bypass",
    "5": "battery",
    "6": "booster",
    "7": "reducer",
}


@dataclass
class OIDDefinition:
    """Complete definition for an OID including all metadata"""
    key: str                # Key name in parsed dict
    oid: str                # OID suffix
    description: str        # Human-readable description
    output_key: str         # Key name in final parsed output
    converter: Optional[Callable] = None  # Conversion function
    mapper: Optional[Dict] = None         # Value mapping dict
    fallback_for: Optional[str] = None    # Key this is a fallback for


# OID definitions with all metadata - order matters!
OID_DEFINITIONS: List[OIDDefinition] = [
    # Identity information
    OIDDefinition("model", "2.1.33.1.1.2.0", "upsIdentModel", 
                  "model", converter=identity_str),
    OIDDefinition("firmware_version", "2.1.33.1.1.3.0", "upsIdentUPSSoftwareVersion", 
                  "firmware_version", converter=identity_str),
    OIDDefinition("agent_version", "2.1.33.1.1.4.0", "upsIdentAgentSoftwareVersion",
                  "agent_version", converter=identity_str),
    
    # Battery metrics
    OIDDefinition("battery_status", "2.1.33.1.2.1.0", "upsBatteryStatus",
                  "battery_status", mapper=BATTERY_STATUS_MAP),
    OIDDefinition("battery_charge", "4.1.935.1.1.1.2.2.1.0", "upsSmartBatteryCapacity (precise)",
                  "battery_charge_percent", converter=identity_float),
    OIDDefinition("battery_runtime_enterprise", "4.1.44782.1.4.4.1.17.0", "ups1batteryTimeRemaining (minutes)",
                  "battery_runtime_seconds", converter=minutes_to_seconds),
    OIDDefinition("battery_runtime_standard", "2.1.33.1.2.3.0", "upsEstimatedMinutesRemaining (fallback)",
                  "battery_runtime_seconds", converter=minutes_to_seconds, 
                  fallback_for="battery_runtime_enterprise"),
    OIDDefinition("battery_voltage", "2.1.33.1.2.5.0", "upsBatteryVoltage (decivolts)",
                  "battery_voltage", converter=decivolts_to_volts),
    OIDDefinition("battery_temp_enterprise", "4.1.44782.1.4.4.1.21.0", "ups1batteryTemperature (precise)",
                  "battery_temperature", converter=identity_float),
    OIDDefinition("battery_temp_standard", "2.1.33.1.2.7.0", "upsBatteryTemperature (fallback)",
                  "battery_temperature", converter=identity_float,
                  fallback_for="battery_temp_enterprise"),
    
    # Input metrics
    OIDDefinition("input_line_bads", "2.1.33.1.3.1.0", "upsInputLineBads",
                  "input_line_bads", converter=identity_int),
    OIDDefinition("input_voltage_enterprise", "4.1.44782.1.4.4.1.27.0", "ups1inputUPhaseVoltage (precise)",
                  "input_voltage", converter=parse_enterprise_voltage),
    OIDDefinition("input_voltage_standard", "2.1.33.1.3.3.1.3.1", "upsInputVoltage (fallback)",
                  "input_voltage", converter=decivolts_to_volts,
                  fallback_for="input_voltage_enterprise"),
    OIDDefinition("input_frequency", "2.1.33.1.3.3.1.2.1", "upsInputFrequency (centihertz)",
                  "input_frequency", converter=centihertz_to_hertz),
    
    # Output metrics
    OIDDefinition("output_source", "2.1.33.1.4.1.0", "upsOutputSource",
                  "output_source", mapper=OUTPUT_SOURCE_MAP),
    OIDDefinition("output_voltage_enterprise", "4.1.44782.1.4.4.1.42.0", "ups1outputUPhaseVoltage (precise)",
                  "output_voltage", converter=parse_enterprise_voltage),
    OIDDefinition("output_voltage_standard", "2.1.33.1.4.4.1.2.1", "upsOutputVoltage (fallback)",
                  "output_voltage", converter=decivolts_to_volts,
                  fallback_for="output_voltage_enterprise"),
    OIDDefinition("output_frequency", "2.1.33.1.4.2.0", "upsOutputFrequency (centihertz)",
                  "output_frequency", converter=centihertz_to_hertz),
    OIDDefinition("output_current", "2.1.33.1.4.4.1.3.1", "upsOutputCurrent (deciamps)",
                  "output_current", converter=deciamps_to_amps),
    OIDDefinition("output_power", "2.1.33.1.4.4.1.4.1", "upsOutputPower (watts)",
                  "output_power_watts", converter=identity_float),
    OIDDefinition("output_load_enterprise", "4.1.44782.1.4.4.1.51.0", "ups1outputPhaseLoadRate (precise)",
                  "output_load_percent", converter=identity_float),
    OIDDefinition("output_load_standard", "2.1.33.1.4.4.1.5.1", "upsOutputPercentLoad (fallback)",
                  "output_load_percent", converter=identity_float,
                  fallback_for="output_load_enterprise"),
    
    # Bypass metrics
    OIDDefinition("bypass_voltage_enterprise", "4.1.44782.1.4.4.1.59.0", "ups1bypassUPhaseVoltage (precise)",
                  "bypass_voltage", converter=parse_enterprise_voltage),
    OIDDefinition("bypass_voltage_standard", "2.1.33.1.5.3.1.3.1", "upsBypassVoltage (fallback)",
                  "bypass_voltage", converter=decivolts_to_volts,
                  fallback_for="bypass_voltage_enterprise"),
    OIDDefinition("bypass_frequency", "2.1.33.1.5.1.0", "upsBypassFrequency (centihertz)",
                  "bypass_frequency", converter=centihertz_to_hertz),
]


def parse_wiseways_ups(string_table):
    """Parse SNMP data and normalize values using OID definitions"""
    if not string_table or not string_table[0]:
        return {}
    
    # Build raw data mapping
    raw_data = {}
    for idx, value in enumerate(string_table[0]):
        if idx < len(OID_DEFINITIONS):
            raw_data[OID_DEFINITIONS[idx].key] = value
    
    # Process each OID definition
    parsed = {}
    fallback_keys = {}  # Track which keys are fallbacks
    
    for oid_def in OID_DEFINITIONS:
        value = raw_data.get(oid_def.key, "")
        
        # Skip if this is a fallback and we should check primary first
        if oid_def.fallback_for:
            fallback_keys[oid_def.output_key] = oid_def.fallback_for
            continue
        
        # Process value
        if not value or value == "0":
            # Check if there's a fallback
            if oid_def.output_key in fallback_keys:
                fallback_def = next((d for d in OID_DEFINITIONS 
                                   if d.key == fallback_keys[oid_def.output_key]), None)
                if fallback_def:
                    fallback_value = raw_data.get(fallback_def.key, "")
                    if fallback_value and fallback_value != "0":
                        value = fallback_value
                        oid_def = fallback_def
        
        # Apply conversion or mapping
        if value and value != "0":
            if oid_def.mapper:
                parsed[oid_def.output_key] = oid_def.mapper.get(value, "unknown")
            elif oid_def.converter:
                try:
                    parsed[oid_def.output_key] = oid_def.converter(value)
                except (ValueError, TypeError):
                    # Set default based on converter type
                    if oid_def.converter in [identity_float, decivolts_to_volts, 
                                            centihertz_to_hertz, deciamps_to_amps,
                                            minutes_to_seconds, parse_enterprise_voltage]:
                        parsed[oid_def.output_key] = 0.0
                    elif oid_def.converter == identity_int:
                        parsed[oid_def.output_key] = 0
                    else:
                        parsed[oid_def.output_key] = ""
            else:
                parsed[oid_def.output_key] = value
        else:
            # Set defaults for empty values
            if oid_def.mapper:
                parsed[oid_def.output_key] = "unknown"
            elif oid_def.converter == identity_str:
                parsed[oid_def.output_key] = "Unknown"
            elif oid_def.converter in [identity_float, decivolts_to_volts, 
                                      centihertz_to_hertz, deciamps_to_amps,
                                      minutes_to_seconds, parse_enterprise_voltage]:
                parsed[oid_def.output_key] = 0.0
            elif oid_def.converter == identity_int:
                parsed[oid_def.output_key] = 0
            else:
                parsed[oid_def.output_key] = ""
    
    # Handle any remaining fallbacks that weren't processed
    for output_key, primary_key in fallback_keys.items():
        if output_key not in parsed or parsed[output_key] == 0.0:
            # Find the fallback definition
            fallback_def = next((d for d in OID_DEFINITIONS 
                               if d.fallback_for == primary_key and d.output_key == output_key), None)
            if fallback_def:
                value = raw_data.get(fallback_def.key, "")
                if value and value != "0":
                    if fallback_def.converter:
                        try:
                            parsed[output_key] = fallback_def.converter(value)
                        except (ValueError, TypeError):
                            pass  # Keep existing value
    
    return parsed


snmp_section_wiseways_ups = SimpleSNMPSection(
    name="wiseways_ups",
    parse_function=parse_wiseways_ups,
    fetch=SNMPTree(
        base=".1.3.6.1",
        # OIDs are fetched in the exact order defined
        oids=[oid_def.oid for oid_def in OID_DEFINITIONS],
    ),
    detect=SNMPDetectSpecification(
        contains(".1.3.6.1.2.1.33.1.1.5.0", "Wiseway3")  # upsIdentName must contain "Wiseway3"
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
        summary=f"Model: {section['model']}, Firmware: {section['firmware_version']}, Agent: {section['agent_version']}"
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