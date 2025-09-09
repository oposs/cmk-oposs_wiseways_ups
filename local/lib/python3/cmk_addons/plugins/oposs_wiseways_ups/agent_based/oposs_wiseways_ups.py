#!/usr/bin/env python3

from typing import Any, Callable, Dict, List, Mapping, Optional
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
    render,
)


# Scaling/conversion functions
def parse_enterprise_string(value: str) -> float:
    """Parse enterprise OID string format values like '231.9'"""
    if not value:
        return float('NaN')
    try:
        return float(value)
    except (ValueError, TypeError):
        return float('NaN')

def minutes_to_seconds(value: str) -> float:
    """Convert minutes to seconds"""
    if not value:
        return float('NaN')
    try:
        val = float(value)
        return val * 60
    except (ValueError, TypeError):
        return float('NaN')

def identity_str(value: str) -> str:
    """Return string as-is or default"""
    return value or "Unknown"

def identity_float(value: str) -> float:
    """Convert to float directly"""
    if not value:
        return float('NaN')
    try:
        return float(value)
    except (ValueError, TypeError):
        return float('NaN')

def identity_int(value: str) -> int:
    """Convert to int directly"""
    if not value:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


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

POWER_SUPPLY_MODE_MAP = {
    "1": "standby",
    "2": "online",
    "3": "battery",
    "4": "bypass",
    "5": "eco",
}

BASE_OUTPUT_STATUS_MAP = {
    "1": "unknown",
    "2": "onLine",
    "3": "onBattery",
    "4": "onSmartBoost",
    "5": "timedSleeping",
    "6": "softwareBypass",
    "7": "off",
    "8": "rebooting",
    "9": "switchedBypass",
    "10": "hardwareFailureBypass",
    "11": "sleepingUntilPowerReturn",
    "12": "onSmartTrim",
    "13": "ecoMode",
    "14": "hotStandby",
    "15": "onBatteryTest",
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


# OID definitions with all metadata - order matters!
OID_DEFINITIONS: List[OIDDefinition] = [
    # Identity information - System Info service
    OIDDefinition("model", "2.1.33.1.1.2.0", "upsIdentModel",
                  "model", converter=identity_str),
    OIDDefinition("manufacturer", "4.1.44782.1.4.4.1.2.0", "ups1equipmentManufacturer",
                  "manufacturer", converter=identity_str),
    OIDDefinition("serial_number", "4.1.44782.1.4.1.5.0", "systemSerialNumber",
                  "serial_number", converter=identity_str),
    OIDDefinition("firmware_version", "2.1.33.1.1.3.0", "upsIdentUPSSoftwareVersion",
                  "firmware_version", converter=identity_str),
    OIDDefinition("agent_version", "2.1.33.1.1.4.0", "upsIdentAgentSoftwareVersion",
                  "agent_version", converter=identity_str),
    OIDDefinition("rated_power", "4.1.44782.1.4.4.1.11.0", "ups1ratedPower",
                  "rated_power", converter=identity_float),
    OIDDefinition("rated_battery_capacity", "4.1.44782.1.4.4.1.12.0", "ups1ratedCapacityOfBattery",
                  "rated_battery_capacity", converter=identity_float),
    OIDDefinition("installation_time", "4.1.44782.1.4.4.1.6.0", "ups1installationTime",
                  "installation_time", converter=identity_str),
    OIDDefinition("maintenance_expiration", "4.1.44782.1.4.4.1.8.0", "ups1maintenanceExpirationTime",
                  "maintenance_expiration", converter=identity_str),
    OIDDefinition("battery_installation", "4.1.44782.1.4.4.1.9.0", "ups1batteryInstallationReplacementTime",
                  "battery_installation", converter=identity_str),
    OIDDefinition("battery_next_maintenance", "4.1.44782.1.4.4.1.10.0", "ups1nextMaintenanceTimeOfBattery",
                  "battery_next_maintenance", converter=identity_str),
    OIDDefinition("number_of_batteries", "4.1.44782.1.4.4.1.14.0", "ups1numberOfBatteries",
                  "number_of_batteries", converter=identity_int),
    OIDDefinition("batteries_per_group", "4.1.44782.1.4.4.1.15.0", "ups1numberOfBatteriesInASingleGroup",
                  "batteries_per_group", converter=identity_int),
    
    # Battery Status service metrics
    OIDDefinition("battery_status", "2.1.33.1.2.1.0", "upsBatteryStatus",
                  "battery_status", mapper=BATTERY_STATUS_MAP),
    OIDDefinition("battery_status_enterprise", "4.1.44782.1.4.4.1.16.0", "ups1batteryStatus",
                  "battery_status_enterprise", converter=identity_int),
    OIDDefinition("seconds_on_battery", "2.1.33.1.2.2.0", "upsSecondsOnBattery",
                  "seconds_on_battery", converter=identity_int),
    OIDDefinition("battery_charge", "4.1.44782.1.4.4.1.18.0", "ups1remainingCapacityOfBattery",
                  "battery_charge_percent", converter=identity_float),
    OIDDefinition("battery_runtime", "4.1.44782.1.4.4.1.17.0", "ups1batteryTimeRemaining (minutes)",
                  "battery_runtime_seconds", converter=minutes_to_seconds),
    
    # Battery physical measurements
    OIDDefinition("battery_voltage", "4.1.44782.1.4.4.1.19.0", "ups1batteryVoltage",
                  "battery_voltage", converter=parse_enterprise_string),
    OIDDefinition("battery_current", "4.1.44782.1.4.4.1.20.0", "ups1batteryChargingAndDischargingCurrent",
                  "battery_current", converter=parse_enterprise_string),
    OIDDefinition("battery_temperature", "4.1.44782.1.4.4.1.21.0", "ups1batteryTemperature",
                  "battery_temperature", converter=parse_enterprise_string),
    
    # Battery alarm flags
    OIDDefinition("battery_abnormal", "4.1.44782.1.4.4.1.72.0", "ups1batteryAbnormal",
                  "battery_abnormal", converter=identity_int),
    OIDDefinition("battery_powered", "4.1.44782.1.4.4.1.73.0", "ups1batteryPowered",
                  "battery_powered", converter=identity_int),
    OIDDefinition("battery_low_voltage", "4.1.44782.1.4.4.1.74.0", "ups1batteryLowVoltage",
                  "battery_low_voltage", converter=identity_int),
    
    # Input physical measurements
    OIDDefinition("input_line_bads", "2.1.33.1.3.1.0", "upsInputLineBads",
                  "input_line_bads", converter=identity_int),
    OIDDefinition("input_voltage", "4.1.44782.1.4.4.1.27.0", "ups1inputUPhaseVoltage",
                  "input_voltage", converter=parse_enterprise_string),
    OIDDefinition("input_frequency", "4.1.44782.1.4.4.1.24.0", "ups1inputUPhaseFrequency",
                  "input_frequency", converter=parse_enterprise_string),
    OIDDefinition("input_abnormal", "4.1.44782.1.4.4.1.77.0", "ups1inputAbnormal",
                  "input_abnormal", converter=identity_int),
    
    # Output physical measurements
    OIDDefinition("output_voltage", "4.1.44782.1.4.4.1.42.0", "ups1outputUPhaseVoltage",
                  "output_voltage", converter=parse_enterprise_string),
    OIDDefinition("output_frequency", "4.1.44782.1.4.4.1.40.0", "ups1outputFrequency",
                  "output_frequency", converter=parse_enterprise_string),
    OIDDefinition("output_current", "4.1.44782.1.4.4.1.45.0", "ups1outputUPhaseCurrent",
                  "output_current", converter=parse_enterprise_string),
    OIDDefinition("output_power", "4.1.44782.1.4.4.1.48.0", "ups1outputUPhaseActivePower",
                  "output_power_watts", converter=parse_enterprise_string),
    OIDDefinition("output_load", "4.1.44782.1.4.4.1.51.0", "ups1outputUPhaseLoadRate",
                  "output_load_percent", converter=parse_enterprise_string),
    
    # Power Status service metrics
    OIDDefinition("output_source", "2.1.33.1.4.1.0", "upsOutputSource",
                  "output_source", mapper=OUTPUT_SOURCE_MAP),
    OIDDefinition("power_supply_mode", "4.1.44782.1.4.4.1.39.0", "ups1powerSupplyMode",
                  "power_supply_mode", mapper=POWER_SUPPLY_MODE_MAP),
    OIDDefinition("base_output_status", "4.1.935.1.1.1.4.1.1.0", "upsBaseOutputStatus",
                  "base_output_status", mapper=BASE_OUTPUT_STATUS_MAP),
    OIDDefinition("output_abnormal", "4.1.44782.1.4.4.1.78.0", "ups1outputAbnormal",
                  "output_abnormal", converter=identity_int),
    
    # Bypass physical measurements
    OIDDefinition("bypass_voltage", "4.1.44782.1.4.4.1.59.0", "ups1bypassUPhaseVoltage",
                  "bypass_voltage", converter=parse_enterprise_string),
    OIDDefinition("bypass_frequency", "4.1.44782.1.4.4.1.57.0", "ups1bypassFrequency",
                  "bypass_frequency", converter=parse_enterprise_string),
    OIDDefinition("bypass_status", "4.1.44782.1.4.4.1.80.0", "ups1bypassStatus",
                  "bypass_status", converter=identity_int),
    
    # Alarm Status service metrics
    OIDDefinition("abnormal_communication", "4.1.44782.1.4.4.1.71.0", "ups1abnormalCommunication",
                  "abnormal_communication", converter=identity_int),
    OIDDefinition("temperature_abnormal", "4.1.44782.1.4.4.1.76.0", "ups1temperatureAbnormal",
                  "temperature_abnormal", converter=identity_int),
    OIDDefinition("overload", "4.1.44782.1.4.4.1.79.0", "ups1overLoad",
                  "overload", converter=identity_int),
    OIDDefinition("fan_failure", "4.1.44782.1.4.4.1.81.0", "ups1fanFailure",
                  "fan_failure", converter=identity_int),
    OIDDefinition("shutdown_request", "4.1.44782.1.4.4.1.85.0", "ups1shutdownRequest",
                  "shutdown_request", converter=identity_int),
    OIDDefinition("test_in_progress", "4.1.44782.1.4.4.1.86.0", "ups1testInProgress",
                  "test_in_progress", converter=identity_int),
    OIDDefinition("shutdown_imminent", "4.1.44782.1.4.4.1.89.0", "ups1shutdownImminent",
                  "shutdown_imminent", converter=identity_int),
    OIDDefinition("low_battery_shutdown_imminent", "4.1.44782.1.4.4.1.93.0", "ups1lowBatteryShutdownImminent",
                  "low_battery_shutdown_imminent", converter=identity_int),
    OIDDefinition("system_status", "4.1.44782.1.4.4.1.94.0", "ups1systemStatus",
                  "system_status", converter=identity_int),
    
    # Device configuration thresholds (for reference/defaults)
    OIDDefinition("input_volt_up_config", "4.1.44782.1.1.3.1.0", "inputVoltUpConfig",
                  "input_volt_up_config", converter=identity_float),
    OIDDefinition("input_volt_low_config", "4.1.44782.1.1.3.2.0", "inputVoltLowConfig",
                  "input_volt_low_config", converter=identity_float),
    OIDDefinition("output_volt_up_config", "4.1.44782.1.1.3.3.0", "outputVoltUpConfig",
                  "output_volt_up_config", converter=identity_float),
    OIDDefinition("output_volt_low_config", "4.1.44782.1.1.3.4.0", "outputVoltLowConfig",
                  "output_volt_low_config", converter=identity_float),
    OIDDefinition("temp_up_config", "4.1.44782.1.1.3.5.0", "upsTempUpConfig",
                  "temp_up_config", converter=identity_float),
    OIDDefinition("output_load_up_config", "4.1.44782.1.1.3.6.0", "upsOutputLoadUpConfig",
                  "output_load_up_config", converter=identity_float),
    OIDDefinition("battery_volt_low_config", "4.1.44782.1.1.3.7.0", "upsBatteryVoltLowConfig",
                  "battery_volt_low_config", converter=identity_float),
]


def parse_oposs_wiseways_ups(string_table):
    """Parse SNMP data and normalize values using OID definitions"""
    if not string_table or not string_table[0]:
        return {}
    
    # Build parsed data mapping
    parsed = {}
    for idx, value in enumerate(string_table[0]):
        if idx < len(OID_DEFINITIONS):
            oid_def = OID_DEFINITIONS[idx]
            
            # Apply conversion or mapping
            if value:
                if oid_def.mapper:
                    parsed[oid_def.output_key] = oid_def.mapper.get(value, "unknown")
                elif oid_def.converter:
                    try:
                        parsed[oid_def.output_key] = oid_def.converter(value)
                    except (ValueError, TypeError):
                        # Set sensible defaults
                        if oid_def.converter == identity_str:
                            parsed[oid_def.output_key] = "Unknown"
                        elif oid_def.converter in [identity_float, parse_enterprise_string]:
                            parsed[oid_def.output_key] = 0.0
                        elif oid_def.converter == identity_int:
                            parsed[oid_def.output_key] = 0
                        elif oid_def.converter == minutes_to_seconds:
                            parsed[oid_def.output_key] = 0.0
                else:
                    parsed[oid_def.output_key] = value
            else:
                # Set defaults for empty values
                if oid_def.mapper:
                    parsed[oid_def.output_key] = "unknown"
                elif oid_def.converter == identity_str:
                    parsed[oid_def.output_key] = "Unknown"
                elif oid_def.converter in [identity_float, parse_enterprise_string, minutes_to_seconds]:
                    parsed[oid_def.output_key] = 0.0
                elif oid_def.converter == identity_int:
                    parsed[oid_def.output_key] = 0
                else:
                    parsed[oid_def.output_key] = ""
    
    return parsed


snmp_section_oposs_wiseways_ups = SimpleSNMPSection(
    name="oposs_wiseways_ups",
    parse_function=parse_oposs_wiseways_ups,
    fetch=SNMPTree(
        base=".1.3.6.1",
        # OIDs are fetched in the exact order defined
        oids=[oid_def.oid for oid_def in OID_DEFINITIONS],
    ),
    detect=SNMPDetectSpecification(
        contains(".1.3.6.1.2.1.33.1.1.5.0", "Wiseway3")  # upsIdentName must contain "Wiseway3"
    ),
)


# ============================================================================
# Physical Measurement Services (Individual)
# ============================================================================

# Check plugin for UPS Input Voltage
def discover_oposs_wiseways_ups_input_voltage(section: Dict[str, Any]) -> DiscoveryResult:
    if section and section.get("input_voltage", 0) > 0:
        yield Service()


def check_oposs_wiseways_ups_input_voltage(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    voltage = section.get("input_voltage", 0)
    
    # Use device config thresholds as defaults if available
    device_upper = section.get("input_volt_up_config", 0)
    device_lower = section.get("input_volt_low_config", 0)
    
    if device_upper > 0 and device_lower > 0:
        default_levels_upper = ("fixed", (device_upper, device_upper + 10))
        default_levels_lower = ("fixed", (device_lower, device_lower - 10))
    else:
        default_levels_upper = ("fixed", (250.0, 260.0))
        default_levels_lower = ("fixed", (210.0, 200.0))
    
    yield from check_levels(
        voltage,
        levels_upper=params.get("input_voltage_upper", default_levels_upper),
        levels_lower=params.get("input_voltage_lower", default_levels_lower),
        metric_name="input_voltage",
        label="Input voltage",
        render_func=lambda v: f"{v:.1f}V",
    )


check_plugin_oposs_wiseways_ups_input_voltage = CheckPlugin(
    name="oposs_wiseways_ups_input_voltage",
    service_name="UPS Input Voltage",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_input_voltage,
    check_function=check_oposs_wiseways_ups_input_voltage,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "input_voltage_upper": ("fixed", (250.0, 260.0)),
        "input_voltage_lower": ("fixed", (210.0, 200.0)),
    },
)


# Check plugin for UPS Output Voltage
def discover_oposs_wiseways_ups_output_voltage(section: Dict[str, Any]) -> DiscoveryResult:
    if section and section.get("output_voltage", 0) > 0:
        yield Service()


def check_oposs_wiseways_ups_output_voltage(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    voltage = section.get("output_voltage", 0)
    
    # Use device config thresholds as defaults if available
    device_upper = section.get("output_volt_up_config", 0)
    device_lower = section.get("output_volt_low_config", 0)
    
    if device_upper > 0 and device_lower > 0:
        default_levels_upper = ("fixed", (device_upper, device_upper + 10))
        default_levels_lower = ("fixed", (device_lower, device_lower - 10))
    else:
        default_levels_upper = ("fixed", (250.0, 260.0))
        default_levels_lower = ("fixed", (210.0, 200.0))
    
    yield from check_levels(
        voltage,
        levels_upper=params.get("output_voltage_upper", default_levels_upper),
        levels_lower=params.get("output_voltage_lower", default_levels_lower),
        metric_name="output_voltage",
        label="Output voltage",
        render_func=lambda v: f"{v:.1f}V",
    )


check_plugin_oposs_wiseways_ups_output_voltage = CheckPlugin(
    name="oposs_wiseways_ups_output_voltage",
    service_name="UPS Output Voltage",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_output_voltage,
    check_function=check_oposs_wiseways_ups_output_voltage,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "output_voltage_upper": ("fixed", (250.0, 260.0)),
        "output_voltage_lower": ("fixed", (210.0, 200.0)),
    },
)


# Check plugin for UPS Bypass Voltage
def discover_oposs_wiseways_ups_bypass_voltage(section: Dict[str, Any]) -> DiscoveryResult:
    if section and section.get("bypass_voltage", 0) > 0:
        yield Service()


def check_oposs_wiseways_ups_bypass_voltage(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    voltage = section.get("bypass_voltage", 0)
    
    yield from check_levels(
        voltage,
        levels_upper=params.get("bypass_voltage_upper"),
        levels_lower=params.get("bypass_voltage_lower"),
        metric_name="bypass_voltage",
        label="Bypass voltage",
        render_func=lambda v: f"{v:.1f}V",
    )


check_plugin_oposs_wiseways_ups_bypass_voltage = CheckPlugin(
    name="oposs_wiseways_ups_bypass_voltage",
    service_name="UPS Bypass Voltage",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_bypass_voltage,
    check_function=check_oposs_wiseways_ups_bypass_voltage,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "bypass_voltage_upper": ("fixed", (250.0, 260.0)),
        "bypass_voltage_lower": ("fixed", (210.0, 200.0)),
    },
)


# Check plugin for UPS Battery Voltage
def discover_oposs_wiseways_ups_battery_voltage(section: Dict[str, Any]) -> DiscoveryResult:
    if section and section.get("battery_voltage", 0) > 0:
        yield Service()


def check_oposs_wiseways_ups_battery_voltage(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    voltage = section.get("battery_voltage", 0)
    
    # Use device config threshold as default if available
    device_lower = section.get("battery_volt_low_config", 0)
    
    if device_lower > 0:
        default_levels_lower = ("fixed", (device_lower, device_lower - 10))
    else:
        default_levels_lower = ("fixed", (180.0, 170.0))
    
    yield from check_levels(
        voltage,
        levels_upper=params.get("battery_voltage_upper"),
        levels_lower=params.get("battery_voltage_lower", default_levels_lower),
        metric_name="battery_voltage",
        label="Battery voltage",
        render_func=lambda v: f"{v:.1f}V",
    )


check_plugin_oposs_wiseways_ups_battery_voltage = CheckPlugin(
    name="oposs_wiseways_ups_battery_voltage",
    service_name="UPS Battery Voltage",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_battery_voltage,
    check_function=check_oposs_wiseways_ups_battery_voltage,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "battery_voltage_lower": ("fixed", (180.0, 170.0)),
    },
)


# Check plugin for UPS Battery Current
def discover_oposs_wiseways_ups_battery_current(section: Dict[str, Any]) -> DiscoveryResult:
    current = section.get("battery_current", 0)
    if section and current != 0:
        yield Service()


def check_oposs_wiseways_ups_battery_current(
    section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    current = section.get("battery_current", 0)
    if current == 0:
        yield Result(state=State.OK, summary="No current flow")
        yield Metric("battery_current", 0)
    else:
        yield Metric("battery_current", abs(current))
        if current > 0:
            yield Result(state=State.OK, summary=f"Charging: {current:.1f}A")
        else:
            yield Result(state=State.OK, summary=f"Discharging: {abs(current):.1f}A")


check_plugin_oposs_wiseways_ups_battery_current = CheckPlugin(
    name="oposs_wiseways_ups_battery_current",
    service_name="UPS Battery Current",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_battery_current,
    check_function=check_oposs_wiseways_ups_battery_current,
)


# Check plugin for UPS Output Current
def discover_oposs_wiseways_ups_output_current(section: Dict[str, Any]) -> DiscoveryResult:
    if section and section.get("output_current", 0) > 0:
        yield Service()


def check_oposs_wiseways_ups_output_current(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    current = section.get("output_current", 0)
    
    yield from check_levels(
        current,
        levels_upper=params.get("output_current_upper"),
        metric_name="output_current",
        label="Output current",
        render_func=lambda v: f"{v:.1f}A",
    )


check_plugin_oposs_wiseways_ups_output_current = CheckPlugin(
    name="oposs_wiseways_ups_output_current",
    service_name="UPS Output Current",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_output_current,
    check_function=check_oposs_wiseways_ups_output_current,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={},
)


# Check plugin for UPS Temperature
def discover_oposs_wiseways_ups_temperature(section: Dict[str, Any]) -> DiscoveryResult:
    if section and section.get("battery_temperature", 0) > 0:
        yield Service()


def check_oposs_wiseways_ups_temperature(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    temperature = section.get("battery_temperature", 0)
    
    # Use device config threshold as default if available
    device_upper = section.get("temp_up_config", 0)
    
    if device_upper > 0:
        default_levels_upper = ("fixed", (device_upper, device_upper + 5))
    else:
        default_levels_upper = ("fixed", (40.0, 45.0))
    
    yield from check_levels(
        temperature,
        levels_upper=params.get("temp_upper", default_levels_upper),
        levels_lower=params.get("temp_lower", ("fixed", (10.0, 5.0))),
        metric_name="temperature",
        label="Temperature",
        render_func=lambda v: f"{v:.1f}°C",
    )


check_plugin_oposs_wiseways_ups_temperature = CheckPlugin(
    name="oposs_wiseways_ups_temperature",
    service_name="UPS Battery Temperature",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_temperature,
    check_function=check_oposs_wiseways_ups_temperature,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "temp_upper": ("fixed", (40.0, 45.0)),
        "temp_lower": ("fixed", (10.0, 5.0)),
    },
)


# Check plugin for UPS Input Frequency
def discover_oposs_wiseways_ups_input_frequency(section: Dict[str, Any]) -> DiscoveryResult:
    if section and section.get("input_frequency", 0) > 0:
        yield Service()


def check_oposs_wiseways_ups_input_frequency(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    frequency = section.get("input_frequency", 0)
    
    yield from check_levels(
        frequency,
        levels_upper=params.get("frequency_upper", ("fixed", (51.0, 52.0))),
        levels_lower=params.get("frequency_lower", ("fixed", (49.0, 48.0))),
        metric_name="input_frequency",
        label="Input frequency",
        render_func=lambda v: f"{v:.1f} Hz",
    )


check_plugin_oposs_wiseways_ups_input_frequency = CheckPlugin(
    name="oposs_wiseways_ups_input_frequency",
    service_name="UPS Input Frequency",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_input_frequency,
    check_function=check_oposs_wiseways_ups_input_frequency,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "frequency_upper": ("fixed", (51.0, 52.0)),
        "frequency_lower": ("fixed", (49.0, 48.0)),
    },
)


# Check plugin for UPS Output Frequency
def discover_oposs_wiseways_ups_output_frequency(section: Dict[str, Any]) -> DiscoveryResult:
    if section and section.get("output_frequency", 0) > 0:
        yield Service()


def check_oposs_wiseways_ups_output_frequency(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    frequency = section.get("output_frequency", 0)
    
    yield from check_levels(
        frequency,
        levels_upper=params.get("frequency_upper", ("fixed", (51.0, 52.0))),
        levels_lower=params.get("frequency_lower", ("fixed", (49.0, 48.0))),
        metric_name="output_frequency",
        label="Output frequency",
        render_func=lambda v: f"{v:.1f} Hz",
    )


check_plugin_oposs_wiseways_ups_output_frequency = CheckPlugin(
    name="oposs_wiseways_ups_output_frequency",
    service_name="UPS Output Frequency",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_output_frequency,
    check_function=check_oposs_wiseways_ups_output_frequency,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "frequency_upper": ("fixed", (51.0, 52.0)),
        "frequency_lower": ("fixed", (49.0, 48.0)),
    },
)


# Check plugin for UPS Bypass Frequency
def discover_oposs_wiseways_ups_bypass_frequency(section: Dict[str, Any]) -> DiscoveryResult:
    if section and section.get("bypass_frequency", 0) > 0:
        yield Service()


def check_oposs_wiseways_ups_bypass_frequency(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    frequency = section.get("bypass_frequency", 0)
    
    yield from check_levels(
        frequency,
        levels_upper=params.get("frequency_upper", ("fixed", (51.0, 52.0))),
        levels_lower=params.get("frequency_lower", ("fixed", (49.0, 48.0))),
        metric_name="bypass_frequency",
        label="Bypass frequency",
        render_func=lambda v: f"{v:.1f} Hz",
    )


check_plugin_oposs_wiseways_ups_bypass_frequency = CheckPlugin(
    name="oposs_wiseways_ups_bypass_frequency",
    service_name="UPS Bypass Frequency",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_bypass_frequency,
    check_function=check_oposs_wiseways_ups_bypass_frequency,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "frequency_upper": ("fixed", (51.0, 52.0)),
        "frequency_lower": ("fixed", (49.0, 48.0)),
    },
)


# Check plugin for UPS Output Power
def discover_oposs_wiseways_ups_output_power(section: Dict[str, Any]) -> DiscoveryResult:
    if section and section.get("output_power_watts", 0) > 0:
        yield Service()


def check_oposs_wiseways_ups_output_power(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    power = section.get("output_power_watts", 0)
    
    yield from check_levels(
        power,
        levels_upper=params.get("power_upper"),
        metric_name="output_power",
        label="Output power",
        render_func=lambda v: f"{v:.0f}W",
    )


check_plugin_oposs_wiseways_ups_output_power = CheckPlugin(
    name="oposs_wiseways_ups_output_power",
    service_name="UPS Output Power",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_output_power,
    check_function=check_oposs_wiseways_ups_output_power,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={},
)


# Check plugin for UPS Output Load
def discover_oposs_wiseways_ups_output_load(section: Dict[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def check_oposs_wiseways_ups_output_load(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    load = section.get("output_load_percent", 0)
    
    # Use device config threshold as default if available
    device_upper = section.get("output_load_up_config", 0)
    
    if device_upper > 0:
        default_levels_upper = ("fixed", (device_upper, device_upper + 10))
    else:
        default_levels_upper = ("fixed", (80.0, 90.0))
    
    yield from check_levels(
        load,
        levels_upper=params.get("load_upper", default_levels_upper),
        metric_name="output_load",
        label="Load",
        render_func=render.percent,
        boundaries=(0, 100),
    )


check_plugin_oposs_wiseways_ups_output_load = CheckPlugin(
    name="oposs_wiseways_ups_output_load",
    service_name="UPS Output Load",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_output_load,
    check_function=check_oposs_wiseways_ups_output_load,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "load_upper": ("fixed", (80.0, 90.0)),
    },
)


# ============================================================================
# Battery Services
# ============================================================================

# Check plugin for UPS Battery Charge (individual service)
def discover_oposs_wiseways_ups_battery_charge(section: Dict[str, Any]) -> DiscoveryResult:
    if section and "battery_charge_percent" in section:
        yield Service()


def check_oposs_wiseways_ups_battery_charge(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    charge_percent = section.get("battery_charge_percent", 0)
    if charge_percent <= 0:
        yield Result(state=State.UNKNOWN, summary="Charge data not available")
        yield Metric("battery_charge", float('nan'))
    else:
        yield from check_levels(
            charge_percent,
            levels_lower=params.get("battery_charge_lower"),
            metric_name="battery_charge",
            label="Battery charge",
            render_func=render.percent,
            boundaries=(0, 100),
        )


check_plugin_oposs_wiseways_ups_battery_charge = CheckPlugin(
    name="oposs_wiseways_ups_battery_charge",
    service_name="UPS Battery Charge",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_battery_charge,
    check_function=check_oposs_wiseways_ups_battery_charge,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "battery_charge_lower": ("fixed", (20.0, 10.0)),
    },
)


# Check plugin for UPS Battery Runtime (individual service)
def discover_oposs_wiseways_ups_battery_runtime(section: Dict[str, Any]) -> DiscoveryResult:
    if section and "battery_runtime_seconds" in section:
        yield Service()


def check_oposs_wiseways_ups_battery_runtime(
    params: Mapping[str, Any], section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    runtime = section.get("battery_runtime_seconds", 0)
    if runtime <= 0:
        yield Result(state=State.UNKNOWN, summary="Runtime data not available")
        yield Metric("battery_runtime", float('nan'))
    else:
        yield from check_levels(
            runtime,
            levels_lower=params.get("battery_runtime_lower"),
            metric_name="battery_runtime",
            label="Battery runtime",
            render_func=render.timespan,
        )


check_plugin_oposs_wiseways_ups_battery_runtime = CheckPlugin(
    name="oposs_wiseways_ups_battery_runtime",
    service_name="UPS Battery Runtime",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_battery_runtime,
    check_function=check_oposs_wiseways_ups_battery_runtime,
    check_ruleset_name="oposs_wiseways_ups",
    check_default_parameters={
        "battery_runtime_lower": ("fixed", (600.0, 300.0)),  # 10min, 5min in seconds
    },
)


# ============================================================================
# Subsystem Status Services (Combined)
# ============================================================================

# Check plugin for UPS Battery Status (status and alarms only)
def discover_oposs_wiseways_ups_battery_status(section: Dict[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def check_oposs_wiseways_ups_battery_status(section: Dict[str, Any]) -> CheckResult:
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
    
    # Time on battery
    time_on_battery = section.get("seconds_on_battery", 0)
    if time_on_battery > 0:
        yield Metric("time_on_battery", time_on_battery)
        yield Result(state=State.WARN, summary=f"On battery: {render.timespan(time_on_battery)}")
    
    # Alarm flags
    alarms = []
    if section.get("battery_abnormal", 0) == 1:
        alarms.append("abnormal")
    
    if section.get("battery_powered", 0) == 1:
        alarms.append("battery powered")
    
    if section.get("battery_low_voltage", 0) == 1:
        alarms.append("low voltage")
    
    if alarms:
        alarm_state = State.CRIT if "low voltage" in alarms else State.WARN
        yield Result(state=alarm_state, summary=f"Alarms: {', '.join(alarms)}")


check_plugin_oposs_wiseways_ups_battery_status = CheckPlugin(
    name="oposs_wiseways_ups_battery_status",
    service_name="UPS Battery Status",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_battery_status,
    check_function=check_oposs_wiseways_ups_battery_status,
)


# Check plugin for UPS Power Status
def discover_oposs_wiseways_ups_power_status(section: Dict[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def check_oposs_wiseways_ups_power_status(
    section: Dict[str, Any]
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
    
    # Power supply mode (enterprise-specific)
    power_mode = section.get("power_supply_mode", "unknown")
    if power_mode != "unknown":
        yield Result(state=State.OK, notice=f"Power mode: {power_mode}")
    
    # Base output status (enterprise-specific)
    base_status = section.get("base_output_status", "unknown")
    if base_status != "unknown":
        # Determine state based on status
        if base_status == "onLine":
            state = State.OK
        elif base_status in ["onBattery", "onSmartBoost", "softwareBypass", "switchedBypass", "onSmartTrim", "ecoMode", "onBatteryTest"]:
            state = State.WARN
        else:
            state = State.CRIT
        yield Result(state=state, notice=f"Base output status: {base_status}")
    
    # Input line failures
    line_bads = section.get("input_line_bads", 0)
    if line_bads > 0:
        yield Result(state=State.WARN, summary=f"Input line failures: {line_bads}")
    yield Metric("input_line_bads", line_bads)
    
    # Alarm flags
    if section.get("input_abnormal", 0) == 1:
        yield Result(state=State.WARN, summary="Input abnormal alarm")
    
    if section.get("output_abnormal", 0) == 1:
        yield Result(state=State.WARN, summary="Output abnormal alarm")
    
    if section.get("bypass_status", 0) == 1:
        yield Result(state=State.WARN, summary="Bypass active")


check_plugin_oposs_wiseways_ups_power_status = CheckPlugin(
    name="oposs_wiseways_ups_power_status",
    service_name="UPS Power Status",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_power_status,
    check_function=check_oposs_wiseways_ups_power_status,
)


# Check plugin for UPS Alarm Status
def discover_oposs_wiseways_ups_alarm_status(section: Dict[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def check_oposs_wiseways_ups_alarm_status(
    section: Dict[str, Any]
) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    warnings = []
    criticals = []
    
    # Critical alarms
    if section.get("shutdown_imminent", 0) == 1:
        criticals.append("Shutdown imminent")
    
    if section.get("low_battery_shutdown_imminent", 0) == 1:
        criticals.append("Low battery shutdown imminent")
    
    if section.get("abnormal_communication", 0) == 1:
        criticals.append("Communication abnormal")
    
    # Warning alarms
    if section.get("temperature_abnormal", 0) == 1:
        warnings.append("Temperature abnormal")
    
    if section.get("overload", 0) == 1:
        warnings.append("Overload condition")
    
    if section.get("fan_failure", 0) == 1:
        warnings.append("Fan failure")
    
    if section.get("shutdown_request", 0) == 1:
        warnings.append("Shutdown request")
    
    if section.get("test_in_progress", 0) == 1:
        warnings.append("Test in progress")
    
    # Overall system status
    system_status = section.get("system_status", 0)
    if system_status == 1:
        yield Result(state=State.OK, notice="System status: Normal")
    elif system_status == 2:
        warnings.append("System status: Warning")
    elif system_status == 3:
        criticals.append("System status: Critical")
    
    # Generate results
    if criticals:
        yield Result(state=State.CRIT, summary=f"Critical: {', '.join(criticals)}")
    
    if warnings:
        yield Result(state=State.WARN, summary=f"Warning: {', '.join(warnings)}")
    
    if not criticals and not warnings:
        yield Result(state=State.OK, summary="No active alarms")


check_plugin_oposs_wiseways_ups_alarm_status = CheckPlugin(
    name="oposs_wiseways_ups_alarm_status",
    service_name="UPS Alarm Status",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_alarm_status,
    check_function=check_oposs_wiseways_ups_alarm_status,
)


# Check plugin for UPS System Info (static/inventory)
def discover_oposs_wiseways_ups_system_info(section: Dict[str, Any]) -> DiscoveryResult:
    if section:
        yield Service()


def check_oposs_wiseways_ups_system_info(section: Dict[str, Any]) -> CheckResult:
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data")
        return
    
    # Collect all information
    model = section.get("model", "Unknown")
    manufacturer = section.get("manufacturer", "Unknown")
    serial = section.get("serial_number", "Unknown")
    fw_version = section.get("firmware_version", "Unknown")
    agent_version = section.get("agent_version", "Unknown")
    
    # Build main summary with key information
    summary_parts = []
    summary_parts.append(f"Model: {model}")
    if manufacturer != "Unknown":
        summary_parts.append(f"Mfr: {manufacturer}")
    if serial != "Unknown":
        summary_parts.append(f"S/N: {serial}")
    
    yield Result(state=State.OK, summary=", ".join(summary_parts))
    
    # Software versions
    if fw_version != "Unknown" or agent_version != "Unknown":
        version_parts = []
        if fw_version != "Unknown":
            version_parts.append(f"FW: {fw_version}")
        if agent_version != "Unknown":
            version_parts.append(f"Agent: {agent_version}")
        yield Result(state=State.OK, summary="Versions: " + ", ".join(version_parts))
    
    # Power ratings
    rated_power = section.get("rated_power", 0)
    rated_battery = section.get("rated_battery_capacity", 0)
    
    if rated_power > 0 or rated_battery > 0:
        rating_parts = []
        if rated_power > 0:
            rating_parts.append(f"{rated_power:.0f}W")
        if rated_battery > 0:
            rating_parts.append(f"{rated_battery:.0f}Ah")
        yield Result(state=State.OK, summary="Ratings: " + ", ".join(rating_parts))
    
    # Battery configuration
    num_batteries = section.get("number_of_batteries", 0)
    batteries_per_group = section.get("batteries_per_group", 0)
    
    if num_batteries > 0 or batteries_per_group > 0:
        battery_parts = []
        if num_batteries > 0:
            battery_parts.append(f"{num_batteries} batteries")
        if batteries_per_group > 0:
            battery_parts.append(f"{batteries_per_group} per group")
        yield Result(state=State.OK, summary="Battery config: " + ", ".join(battery_parts))
    
    # Installation and maintenance dates as notices for less clutter
    installation = section.get("installation_time", "Unknown")
    maintenance_exp = section.get("maintenance_expiration", "Unknown")
    battery_install = section.get("battery_installation", "Unknown")
    battery_next_maint = section.get("battery_next_maintenance", "Unknown")
    
    if installation != "Unknown":
        yield Result(state=State.OK, notice=f"Installation: {installation}")
    if maintenance_exp != "Unknown":
        # Check if maintenance has expired
        from datetime import datetime
        try:
            exp_date = datetime.strptime(maintenance_exp, "%Y-%m-%d")
            if exp_date < datetime.now():
                yield Result(state=State.WARN, summary=f"Maintenance expired: {maintenance_exp}")
            else:
                yield Result(state=State.OK, notice=f"Maintenance expiration: {maintenance_exp}")
        except:
            yield Result(state=State.OK, notice=f"Maintenance expiration: {maintenance_exp}")
    
    if battery_install != "Unknown":
        yield Result(state=State.OK, notice=f"Battery installation: {battery_install}")
    if battery_next_maint != "Unknown":
        # Check if battery maintenance is due
        from datetime import datetime
        try:
            maint_date = datetime.strptime(battery_next_maint, "%Y-%m-%d")
            if maint_date < datetime.now():
                yield Result(state=State.WARN, summary=f"Battery maintenance due: {battery_next_maint}")
            else:
                yield Result(state=State.OK, notice=f"Battery next maintenance: {battery_next_maint}")
        except:
            yield Result(state=State.OK, notice=f"Battery next maintenance: {battery_next_maint}")


check_plugin_oposs_wiseways_ups_system_info = CheckPlugin(
    name="oposs_wiseways_ups_system_info",
    service_name="UPS System Info",
    sections=["oposs_wiseways_ups"],
    discovery_function=discover_oposs_wiseways_ups_system_info,
    check_function=check_oposs_wiseways_ups_system_info,
)