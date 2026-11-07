"""The 19 Wiseway UPS checks, fed with SNMP data as Checkmk fetches it.

The section fetches 58 scalar OIDs in one SNMPTree under .1.3.6.1, so the
string table is one table holding one row of 58 strings, in fetch order.
The values of the sample walk below are the example values of
monitored_oids.md: the enterprise tree 44782 delivers measurements as
decimal strings ("231.9"), the battery time remaining in minutes and the
THS sensor values as integer tenths ("243" is 24.3 C).

The OIDs under 1.3.6.1.2.1.33 are RFC 1628 UPS-MIB. upsBaseOutputStatus
(1.3.6.1.4.1.935.1.1.1.4.1.1) is XPPC-MIB. No public copy of the Wiseway
enterprise MIB (44782) could be found, so those OIDs are checked against
monitored_oids.md only.
"""

import importlib.util
import json
import math
import pathlib
import re
import sys

import pytest
from cmk.agent_based.v2 import (
    CheckPlugin,
    Metric,
    Result,
    Service,
    SimpleSNMPSection,
    State,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECK = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_wiseways_ups/agent_based/oposs_wiseways_ups.py"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

UPS = ".1.3.6.1.2.1.33.1."  # RFC 1628 UPS-MIB
WW = ".1.3.6.1.4.1.44782."  # Wiseway enterprise tree
XPPC = ".1.3.6.1.4.1.935.1.1.1."  # XPPC-MIB

# Every fetched OID, its name and the value of a healthy UPS on mains.
# Values from monitored_oids.md; ups1bypassStatus and ups1testInProgress
# are 0 here although that file lists 1 for both (see the report on the
# onboarding PR: the check turns 1 into WARN).
WALK = {
    UPS + "1.2.0": ("upsIdentModel", "6000VA"),
    WW + "1.4.4.1.2.0": ("ups1equipmentManufacturer", "Others"),
    WW + "1.4.1.5.0": ("systemSerialNumber", "5A1903026810Q9100039"),
    UPS + "1.3.0": ("upsIdentUPSSoftwareVersion", "VER 6.xxx"),
    UPS + "1.4.0": ("upsIdentAgentSoftwareVersion", "2.0.0"),
    WW + "1.4.4.1.11.0": ("ups1ratedPower", "5000"),
    WW + "1.4.4.1.12.0": ("ups1ratedCapacityOfBattery", "100"),
    WW + "1.4.4.1.6.0": ("ups1installationTime", "2020-06-13"),
    WW + "1.4.4.1.8.0": ("ups1maintenanceExpirationTime", "2999-06-13"),
    WW + "1.4.4.1.9.0": ("ups1batteryInstallationReplacementTime", "2021-06-13"),
    WW + "1.4.4.1.10.0": ("ups1nextMaintenanceTimeOfBattery", "2999-06-13"),
    WW + "1.4.4.1.14.0": ("ups1numberOfBatteries", "1"),
    WW + "1.4.4.1.15.0": ("ups1numberOfBatteriesInASingleGroup", "16"),
    UPS + "2.1.0": ("upsBatteryStatus", "2"),
    WW + "1.4.4.1.16.0": ("ups1batteryStatus", "2"),
    UPS + "2.2.0": ("upsSecondsOnBattery", "0"),
    WW + "1.4.4.1.18.0": ("ups1remainingCapacityOfBattery", "100"),
    WW + "1.4.4.1.17.0": ("ups1batteryTimeRemaining", "15"),
    WW + "1.4.4.1.19.0": ("ups1batteryVoltage", "217.9"),
    WW + "1.4.4.1.20.0": ("ups1batteryChargingAndDischargingCurrent", "0.00"),
    WW + "1.4.4.1.21.0": ("ups1batteryTemperature", "28.0"),
    WW + "1.4.4.1.72.0": ("ups1batteryAbnormal", "0"),
    WW + "1.4.4.1.73.0": ("ups1batteryPowered", "0"),
    WW + "1.4.4.1.74.0": ("ups1batteryLowVoltage", "0"),
    UPS + "3.1.0": ("upsInputLineBads", "0"),
    WW + "1.4.4.1.27.0": ("ups1inputUPhaseVoltage", "231.9"),
    WW + "1.4.4.1.24.0": ("ups1inputUPhaseFrequency", "50.0"),
    WW + "1.4.4.1.77.0": ("ups1inputAbnormal", "0"),
    WW + "1.4.4.1.42.0": ("ups1outputUPhaseVoltage", "231.9"),
    WW + "1.4.4.1.40.0": ("ups1outputFrequency", "50.0"),
    WW + "1.4.4.1.45.0": ("ups1outputUPhaseCurrent", "0.00"),
    WW + "1.4.4.1.48.0": ("ups1outputUPhaseActivePower", "0.00"),
    WW + "1.4.4.1.51.0": ("ups1outputUPhaseLoadRate", "0.0"),
    UPS + "4.1.0": ("upsOutputSource", "3"),
    WW + "1.4.4.1.39.0": ("ups1powerSupplyMode", "2"),
    XPPC + "4.1.1.0": ("upsBaseOutputStatus", "2"),
    WW + "1.4.4.1.78.0": ("ups1outputAbnormal", "0"),
    WW + "1.4.4.1.59.0": ("ups1bypassUPhaseVoltage", "232.9"),
    WW + "1.4.4.1.57.0": ("ups1bypassFrequency", "50.0"),
    WW + "1.4.4.1.80.0": ("ups1bypassStatus", "0"),
    WW + "1.4.4.1.71.0": ("ups1abnormalCommunication", "0"),
    WW + "1.4.4.1.76.0": ("ups1temperatureAbnormal", "0"),
    WW + "1.4.4.1.79.0": ("ups1overLoad", "0"),
    WW + "1.4.4.1.81.0": ("ups1fanFailure", "0"),
    WW + "1.4.4.1.85.0": ("ups1shutdownRequest", "0"),
    WW + "1.4.4.1.86.0": ("ups1testInProgress", "0"),
    WW + "1.4.4.1.89.0": ("ups1shutdownImminent", "0"),
    WW + "1.4.4.1.93.0": ("ups1lowBatteryShutdownImminent", "0"),
    WW + "1.4.4.1.94.0": ("ups1systemStatus", "1"),
    WW + "1.1.3.1.0": ("inputVoltUpConfig", ""),
    WW + "1.1.3.2.0": ("inputVoltLowConfig", ""),
    WW + "1.1.3.3.0": ("outputVoltUpConfig", ""),
    WW + "1.1.3.4.0": ("outputVoltLowConfig", ""),
    WW + "1.1.3.5.0": ("upsTempUpConfig", ""),
    WW + "1.1.3.6.0": ("upsOutputLoadUpConfig", ""),
    WW + "1.1.3.7.0": ("upsBatteryVoltLowConfig", ""),
    WW + "1.2.1.1.1.0": ("thsOneTempData", ""),
    WW + "1.2.1.1.2.0": ("thsOneHumiData", ""),
}
NAME_TO_OID = {name: oid for oid, (name, _) in WALK.items()}

SERVICES = [
    "UPS System Info", "UPS Battery Status", "UPS Battery Charge", "UPS Battery Runtime",
    "UPS Power Status", "UPS Alarm Status",
    "UPS Input Voltage", "UPS Output Voltage", "UPS Bypass Voltage", "UPS Battery Voltage",
    "UPS Battery Current", "UPS Output Current", "UPS Battery Temperature",
    "UPS Input Frequency", "UPS Output Frequency", "UPS Bypass Frequency",
    "UPS Output Power", "UPS Output Load", "UPS Environment",
]


@pytest.fixture(scope="module")
def check():
    return load_module(CHECK, "test_oposs_wiseways_ups_check")


def _section_def(check):
    (section,) = [v for v in vars(check).values() if isinstance(v, SimpleSNMPSection)]
    return section


def _plugins(check):
    return {v.service_name: v for v in vars(check).values() if isinstance(v, CheckPlugin)}


def _fetched_oids(check):
    (tree,) = _section_def(check).fetch  # one SNMPTree
    return [f"{tree.base}.{oid.column}" for oid in tree.oids]


def _rows(check, **changes):
    """The string table Checkmk hands the parse function, changed by OID name."""
    values = {oid: value for oid, (_, value) in WALK.items()}
    for name, value in changes.items():
        values[NAME_TO_OID[name]] = value
    return [[values[oid] for oid in _fetched_oids(check)]]


def _parse(check, **changes):
    # Checkmk hands the wrapped parse function one table per SNMPTree
    return _section_def(check).parse_function([_rows(check, **changes)])


def _run(check, service, params=None, **changes):
    """Parse, discover and check one service the way Checkmk does: the rule
    parameters are merged on top of the plugin's default parameters."""
    plugin = _plugins(check)[service]
    section = _parse(check, **changes)
    discovered = list(plugin.discovery_function(section))
    if plugin.check_default_parameters is None:
        out = list(plugin.check_function(section))
    else:
        merged = {**plugin.check_default_parameters, **(params or {})}
        out = list(plugin.check_function(merged, section))
    return discovered, out


def _results(out):
    return [r for r in out if isinstance(r, Result)]


def _summaries(out):
    """The texts in the service summary line; a notice has an empty summary."""
    return [r.summary for r in _results(out) if r.summary]


def _metrics(out):
    return {m.name: m.value for m in out if isinstance(m, Metric)}


def _worst(out):
    return State.worst(*(r.state for r in _results(out)))


def _text(out):
    return " | ".join(r.summary or r.details for r in _results(out))


# --- registration, detection, OIDs ------------------------------------------

def test_every_service_is_registered_once(check):
    names = [v.service_name for v in vars(check).values() if isinstance(v, CheckPlugin)]
    assert sorted(names) == sorted(SERVICES)


def test_every_check_reads_the_one_section(check):
    section = _section_def(check)
    assert section.name == "oposs_wiseways_ups"
    for plugin in _plugins(check).values():
        assert plugin.sections == ["oposs_wiseways_ups"]


def test_detect_requires_wiseway3_in_upsidentname(check):
    detect = _section_def(check).detect
    assert detect == [[(UPS + "1.5.0", ".*Wiseway3.*", True)]]
    ((_, pattern, _),) = detect[0]
    assert re.fullmatch(pattern, "Wiseway3 UPS")
    assert not re.fullmatch(pattern, "Smart-UPS 3000")


def test_fetch_reads_the_documented_oids_in_order(check):
    assert _fetched_oids(check) == list(WALK)


@pytest.mark.parametrize("name, oid", [
    ("upsIdentModel", "1.3.6.1.2.1.33.1.1.2.0"),
    ("upsIdentUPSSoftwareVersion", "1.3.6.1.2.1.33.1.1.3.0"),
    ("upsIdentAgentSoftwareVersion", "1.3.6.1.2.1.33.1.1.4.0"),
    ("upsBatteryStatus", "1.3.6.1.2.1.33.1.2.1.0"),
    ("upsSecondsOnBattery", "1.3.6.1.2.1.33.1.2.2.0"),
    ("upsInputLineBads", "1.3.6.1.2.1.33.1.3.1.0"),
    ("upsOutputSource", "1.3.6.1.2.1.33.1.4.1.0"),
    ("upsBaseOutputStatus", "1.3.6.1.4.1.935.1.1.1.4.1.1.0"),
])
def test_standard_mib_oids(check, name, oid):
    """RFC 1628 UPS-MIB and XPPC-MIB put these objects at these OIDs."""
    assert "." + oid in _fetched_oids(check)
    assert NAME_TO_OID[name] == "." + oid


# --- parsing ----------------------------------------------------------------

def test_parse_empty_table_gives_empty_section(check):
    assert check.parse_oposs_wiseways_ups([]) == {}
    assert check.parse_oposs_wiseways_ups([[]]) == {}


def test_parse_converts_the_sample_walk(check):
    section = _parse(check)
    assert section["model"] == "6000VA"
    assert section["serial_number"] == "5A1903026810Q9100039"
    assert section["battery_status"] == "batteryNormal"
    assert section["output_source"] == "normal"
    assert section["power_supply_mode"] == "online"
    assert section["base_output_status"] == "onLine"
    assert section["battery_runtime_seconds"] == 900.0  # 15 minutes
    assert section["input_voltage"] == 231.9
    assert section["rated_power"] == 5000.0
    assert section["number_of_batteries"] == 1
    # Empty values: 0.0 for numbers, so the THS sensor counts as absent
    assert section["env_temperature"] == 0.0
    assert section["input_volt_up_config"] == 0.0


def test_parse_accepts_a_comma_as_decimal_separator(check):
    assert _parse(check, ups1inputUPhaseVoltage="231,9")["input_voltage"] == 231.9


def test_parse_reads_ths_sensor_values_as_tenths(check):
    section = _parse(check, thsOneTempData="243", thsOneHumiData="456")
    assert section["env_temperature"] == pytest.approx(24.3)
    assert section["env_humidity"] == pytest.approx(45.6)


def test_parse_maps_unknown_enum_values_to_unknown(check):
    section = _parse(check, upsBatteryStatus="9", upsOutputSource="", ups1powerSupplyMode="77")
    assert section["battery_status"] == "unknown"
    assert section["output_source"] == "unknown"
    assert section["power_supply_mode"] == "unknown"


def test_parse_ignores_extra_columns(check):
    (row,) = _rows(check)
    assert check.parse_oposs_wiseways_ups([row + ["surplus"]]) == _parse(check)


# --- discovery --------------------------------------------------------------

def test_discovery_on_the_sample_walk(check):
    section = _parse(check)
    found = {name for name, p in _plugins(check).items() if list(p.discovery_function(section))}
    # Zero current and power, and no THS sensor: these four stay away
    assert found == set(SERVICES) - {
        "UPS Battery Current", "UPS Output Current", "UPS Output Power", "UPS Environment"}


def test_every_discovered_service_has_no_item(check):
    section = _parse(check)
    for plugin in _plugins(check).values():
        assert all(s == Service() for s in plugin.discovery_function(section))


def test_nothing_is_discovered_without_data(check):
    for plugin in _plugins(check).values():
        assert list(plugin.discovery_function({})) == []


@pytest.mark.parametrize("service, changes", [
    ("UPS Battery Current", {"ups1batteryChargingAndDischargingCurrent": "1.5"}),
    ("UPS Output Current", {"ups1outputUPhaseCurrent": "4.2"}),
    ("UPS Output Power", {"ups1outputUPhaseActivePower": "950"}),
    ("UPS Environment", {"thsOneTempData": "243"}),
    ("UPS Environment", {"thsOneHumiData": "456"}),
])
def test_measurement_services_appear_with_a_value(check, service, changes):
    discovered, _ = _run(check, service, **changes)
    assert discovered == [Service()]


@pytest.mark.parametrize("service, name", [
    ("UPS Input Voltage", "ups1inputUPhaseVoltage"),
    ("UPS Bypass Voltage", "ups1bypassUPhaseVoltage"),
    ("UPS Bypass Frequency", "ups1bypassFrequency"),
    ("UPS Battery Temperature", "ups1batteryTemperature"),
])
def test_measurement_services_stay_away_without_a_value(check, service, name):
    discovered, _ = _run(check, service, **{name: ""})
    assert discovered == []


@pytest.mark.parametrize("service", SERVICES)
def test_every_check_says_no_data_on_an_empty_section(check, service):
    plugin = _plugins(check)[service]
    if plugin.check_default_parameters is None:
        out = list(plugin.check_function({}))
    else:
        out = list(plugin.check_function(plugin.check_default_parameters, {}))
    assert out == [Result(state=State.UNKNOWN, summary="No data")]


# --- the sample walk, service by service -------------------------------------

SAMPLE = [
    ("UPS Input Voltage", State.OK, "Input voltage: 231.9V", {"input_voltage": 231.9}),
    ("UPS Output Voltage", State.OK, "Output voltage: 231.9V", {"output_voltage": 231.9}),
    ("UPS Bypass Voltage", State.OK, "Bypass voltage: 232.9V", {"bypass_voltage": 232.9}),
    ("UPS Battery Voltage", State.OK, "Battery voltage: 217.9V", {"battery_voltage": 217.9}),
    ("UPS Battery Temperature", State.OK, "Temperature: 28.0°C", {"temperature": 28.0}),
    ("UPS Input Frequency", State.OK, "Input frequency: 50.0 Hz", {"input_frequency": 50.0}),
    ("UPS Output Frequency", State.OK, "Output frequency: 50.0 Hz", {"output_frequency": 50.0}),
    ("UPS Bypass Frequency", State.OK, "Bypass frequency: 50.0 Hz", {"bypass_frequency": 50.0}),
    ("UPS Output Load", State.OK, "Load: 0%", {"output_load": 0.0}),
    ("UPS Battery Charge", State.OK, "Battery charge: 100.00%", {"battery_charge": 100.0}),
    ("UPS Battery Runtime", State.OK, "Battery runtime: 15 minutes 0 seconds", {"battery_runtime": 900.0}),
    ("UPS Battery Status", State.OK, "Status: batteryNormal", {"time_on_battery": 0}),
    ("UPS Power Status", State.OK, "Power source: normal", {"input_line_bads": 0}),
    ("UPS Alarm Status", State.OK, "No active alarms", {}),
    ("UPS System Info", State.OK,
     "Model: 6000VA, Mfr: Others, S/N: 5A1903026810Q9100039", {}),
]


@pytest.mark.parametrize("service, state, summary, metrics", SAMPLE, ids=[s[0] for s in SAMPLE])
def test_sample_walk(check, service, state, summary, metrics):
    discovered, out = _run(check, service)
    assert discovered == [Service()]
    assert _worst(out) == state
    assert _summaries(out)[0] == summary
    assert _metrics(out) == pytest.approx(metrics)


def test_system_info_shows_versions_ratings_and_batteries(check):
    _, out = _run(check, "UPS System Info")
    summaries = [r.summary for r in _results(out)]
    assert "Versions: FW: VER 6.xxx, Agent: 2.0.0" in summaries
    assert "Ratings: 5000W, 100Ah" in summaries
    assert "Battery config: 1 batteries, 16 per group" in summaries
    assert "Installation: 2020-06-13" in _text(out)


# --- levels -----------------------------------------------------------------

LEVELS = [
    # service, OID name, raw SNMP value, expected state
    ("UPS Input Voltage", "ups1inputUPhaseVoltage", "249.9", State.OK),
    ("UPS Input Voltage", "ups1inputUPhaseVoltage", "250.0", State.WARN),
    ("UPS Input Voltage", "ups1inputUPhaseVoltage", "260.0", State.CRIT),
    ("UPS Input Voltage", "ups1inputUPhaseVoltage", "209.9", State.WARN),
    ("UPS Input Voltage", "ups1inputUPhaseVoltage", "199.9", State.CRIT),
    ("UPS Output Voltage", "ups1outputUPhaseVoltage", "255", State.WARN),
    ("UPS Output Voltage", "ups1outputUPhaseVoltage", "261", State.CRIT),
    ("UPS Output Voltage", "ups1outputUPhaseVoltage", "205", State.WARN),
    ("UPS Output Voltage", "ups1outputUPhaseVoltage", "195", State.CRIT),
    ("UPS Bypass Voltage", "ups1bypassUPhaseVoltage", "255", State.WARN),
    ("UPS Bypass Voltage", "ups1bypassUPhaseVoltage", "265", State.CRIT),
    ("UPS Bypass Voltage", "ups1bypassUPhaseVoltage", "205", State.WARN),
    ("UPS Bypass Voltage", "ups1bypassUPhaseVoltage", "195", State.CRIT),
    ("UPS Battery Voltage", "ups1batteryVoltage", "36.0", State.OK),
    ("UPS Battery Voltage", "ups1batteryVoltage", "31.0", State.WARN),
    ("UPS Battery Voltage", "ups1batteryVoltage", "29.0", State.CRIT),
    ("UPS Battery Temperature", "ups1batteryTemperature", "41", State.WARN),
    ("UPS Battery Temperature", "ups1batteryTemperature", "46", State.CRIT),
    ("UPS Battery Temperature", "ups1batteryTemperature", "8", State.WARN),
    ("UPS Battery Temperature", "ups1batteryTemperature", "4", State.CRIT),
    ("UPS Input Frequency", "ups1inputUPhaseFrequency", "51.5", State.WARN),
    ("UPS Input Frequency", "ups1inputUPhaseFrequency", "52.5", State.CRIT),
    ("UPS Input Frequency", "ups1inputUPhaseFrequency", "48.5", State.WARN),
    ("UPS Input Frequency", "ups1inputUPhaseFrequency", "47.5", State.CRIT),
    ("UPS Output Frequency", "ups1outputFrequency", "51.5", State.WARN),
    ("UPS Output Frequency", "ups1outputFrequency", "47.5", State.CRIT),
    ("UPS Bypass Frequency", "ups1bypassFrequency", "52.5", State.CRIT),
    ("UPS Bypass Frequency", "ups1bypassFrequency", "48.5", State.WARN),
    ("UPS Output Load", "ups1outputUPhaseLoadRate", "79.9", State.OK),
    ("UPS Output Load", "ups1outputUPhaseLoadRate", "85", State.WARN),
    ("UPS Output Load", "ups1outputUPhaseLoadRate", "95", State.CRIT),
    ("UPS Battery Charge", "ups1remainingCapacityOfBattery", "20", State.OK),
    ("UPS Battery Charge", "ups1remainingCapacityOfBattery", "15", State.WARN),
    ("UPS Battery Charge", "ups1remainingCapacityOfBattery", "5", State.CRIT),
    ("UPS Battery Runtime", "ups1batteryTimeRemaining", "10", State.OK),
    ("UPS Battery Runtime", "ups1batteryTimeRemaining", "9", State.WARN),
    ("UPS Battery Runtime", "ups1batteryTimeRemaining", "4", State.CRIT),
]


@pytest.mark.parametrize("service, name, value, state", LEVELS)
def test_default_levels(check, service, name, value, state):
    _, out = _run(check, service, **{name: value})
    assert _worst(out) == state


@pytest.mark.parametrize("service, params, name, value, state", [
    ("UPS Output Current", {"output_current_upper": ("fixed", (10.0, 20.0))},
     "ups1outputUPhaseCurrent", "15", State.WARN),
    ("UPS Output Current", {"output_current_upper": ("fixed", (10.0, 20.0))},
     "ups1outputUPhaseCurrent", "25", State.CRIT),
    ("UPS Output Power", {"power_upper": ("fixed", (4000.0, 4500.0))},
     "ups1outputUPhaseActivePower", "4200", State.WARN),
    ("UPS Battery Voltage", {"battery_voltage_upper": ("fixed", (40.0, 42.0))},
     "ups1batteryVoltage", "43", State.CRIT),
    ("UPS Input Voltage", {"input_voltage_upper": ("no_levels", None),
                           "input_voltage_lower": ("no_levels", None)},
     "ups1inputUPhaseVoltage", "300", State.OK),
    ("UPS Battery Charge", {"battery_charge_lower": ("fixed", (50.0, 30.0))},
     "ups1remainingCapacityOfBattery", "40", State.WARN),
])
def test_rule_levels(check, service, params, name, value, state):
    _, out = _run(check, service, params, **{name: value})
    assert _worst(out) == state


def test_output_current_and_power_have_no_default_levels(check):
    _, out = _run(check, "UPS Output Current", ups1outputUPhaseCurrent="900")
    assert _worst(out) == State.OK
    assert _metrics(out) == {"output_current": 900.0}
    _, out = _run(check, "UPS Output Power", ups1outputUPhaseActivePower="99999")
    assert _worst(out) == State.OK
    assert _metrics(out) == {"output_power": 99999.0}


# --- battery ----------------------------------------------------------------

@pytest.mark.parametrize("raw, state", [("1", State.WARN), ("3", State.CRIT), ("4", State.CRIT)])
def test_battery_status_states(check, raw, state):
    _, out = _run(check, "UPS Battery Status", upsBatteryStatus=raw)
    assert _results(out)[0].state == state


def test_battery_status_on_battery(check):
    _, out = _run(check, "UPS Battery Status", upsSecondsOnBattery="125")
    assert _worst(out) == State.WARN
    assert "On battery: 2 minutes 5 seconds" in _text(out)
    assert _metrics(out) == {"time_on_battery": 125}


@pytest.mark.parametrize("flag, state, text", [
    ("ups1batteryAbnormal", State.WARN, "Alarms: abnormal"),
    ("ups1batteryPowered", State.WARN, "Alarms: battery powered"),
    ("ups1batteryLowVoltage", State.CRIT, "Alarms: low voltage"),
])
def test_battery_status_alarm_flags(check, flag, state, text):
    _, out = _run(check, "UPS Battery Status", **{flag: "1"})
    assert _worst(out) == state
    assert text in _text(out)


@pytest.mark.parametrize("raw, summary, metric", [
    ("1.5", "Charging: 1.5A", 1.5),
    ("-12.3", "Discharging: 12.3A", 12.3),
])
def test_battery_current(check, raw, summary, metric):
    discovered, out = _run(check, "UPS Battery Current",
                           ups1batteryChargingAndDischargingCurrent=raw)
    assert discovered == [Service()]
    assert out == [Metric("battery_current", metric), Result(state=State.OK, summary=summary)]


def test_battery_current_zero_after_discovery(check):
    _, out = _run(check, "UPS Battery Current")
    assert out == [Result(state=State.OK, summary="No current flow"), Metric("battery_current", 0)]


@pytest.mark.parametrize("service, name, summary", [
    ("UPS Battery Charge", "ups1remainingCapacityOfBattery", "Charge data not available"),
    ("UPS Battery Runtime", "ups1batteryTimeRemaining", "Runtime data not available"),
])
@pytest.mark.parametrize("raw", ["-99998", "0", ""])
def test_battery_charge_and_runtime_unavailable(check, service, name, summary, raw):
    """-99998 is how the card says it has no value."""
    discovered, out = _run(check, service, **{name: raw})
    assert discovered == [Service()]
    (result,) = _results(out)
    assert result == Result(state=State.UNKNOWN, summary=summary)
    (value,) = _metrics(out).values()
    assert math.isnan(value)


# --- power and alarms -------------------------------------------------------

@pytest.mark.parametrize("raw, state, source", [
    ("5", State.WARN, "battery"),
    ("4", State.WARN, "bypass"),
    ("2", State.CRIT, "none"),
    ("1", State.CRIT, "other"),
    ("6", State.CRIT, "booster"),
])
def test_power_source(check, raw, state, source):
    _, out = _run(check, "UPS Power Status", upsOutputSource=raw)
    assert _results(out)[0] == Result(state=state, summary=f"Power source: {source}")


def test_power_status_mode_and_base_status_are_notices(check):
    _, out = _run(check, "UPS Power Status")
    assert Result(state=State.OK, notice="Power mode: online") in out
    assert Result(state=State.OK, notice="Base output status: onLine") in out


@pytest.mark.parametrize("raw, state", [("3", State.WARN), ("1", State.OK)])
def test_power_status_base_output_status(check, raw, state):
    _, out = _run(check, "UPS Power Status", upsBaseOutputStatus=raw)
    assert _worst(out) == state


@pytest.mark.parametrize("changes, text", [
    ({"upsInputLineBads": "3"}, "Input line failures: 3"),
    ({"ups1inputAbnormal": "1"}, "Input abnormal alarm"),
    ({"ups1outputAbnormal": "1"}, "Output abnormal alarm"),
    ({"ups1bypassStatus": "1"}, "Bypass active"),
])
def test_power_status_warnings(check, changes, text):
    _, out = _run(check, "UPS Power Status", **changes)
    assert _worst(out) == State.WARN
    assert text in _text(out)


def test_power_status_counts_line_failures(check):
    _, out = _run(check, "UPS Power Status", upsInputLineBads="3")
    assert _metrics(out) == {"input_line_bads": 3}


@pytest.mark.parametrize("flag, state, text", [
    ("ups1shutdownImminent", State.CRIT, "Critical: Shutdown imminent"),
    ("ups1lowBatteryShutdownImminent", State.CRIT, "Critical: Low battery shutdown imminent"),
    ("ups1abnormalCommunication", State.CRIT, "Critical: Communication abnormal"),
    ("ups1temperatureAbnormal", State.WARN, "Warning: Temperature abnormal"),
    ("ups1overLoad", State.WARN, "Warning: Overload condition"),
    ("ups1fanFailure", State.WARN, "Warning: Fan failure"),
    ("ups1shutdownRequest", State.WARN, "Warning: Shutdown request"),
    ("ups1testInProgress", State.WARN, "Warning: Test in progress"),
])
def test_alarm_flags(check, flag, state, text):
    _, out = _run(check, "UPS Alarm Status", **{flag: "1"})
    assert _worst(out) == state
    assert text in _text(out)


@pytest.mark.parametrize("raw, state, text", [
    ("2", State.WARN, "Warning: System status: Warning"),
    ("3", State.CRIT, "Critical: System status: Critical"),
])
def test_alarm_system_status(check, raw, state, text):
    _, out = _run(check, "UPS Alarm Status", ups1systemStatus=raw)
    assert _worst(out) == state
    assert text in _text(out)


def test_alarm_status_lists_several_alarms(check):
    _, out = _run(check, "UPS Alarm Status", ups1overLoad="1", ups1fanFailure="1",
                  ups1shutdownImminent="1")
    assert _summaries(out) == [
        "Critical: Shutdown imminent", "Warning: Overload condition, Fan failure"]


# --- system info dates --------------------------------------------------------

@pytest.mark.parametrize("name, text", [
    ("ups1maintenanceExpirationTime", "Maintenance expired: 2000-01-01"),
    ("ups1nextMaintenanceTimeOfBattery", "Battery maintenance due: 2000-01-01"),
])
def test_system_info_warns_on_past_dates(check, name, text):
    _, out = _run(check, "UPS System Info", **{name: "2000-01-01"})
    assert Result(state=State.WARN, summary=text) in out


def test_system_info_keeps_unreadable_dates_as_notices(check):
    _, out = _run(check, "UPS System Info", ups1maintenanceExpirationTime="13/06/2022")
    assert _worst(out) == State.OK
    assert Result(state=State.OK, notice="Maintenance expiration: 13/06/2022") in out


def test_system_info_without_identity(check):
    _, out = _run(check, "UPS System Info", ups1equipmentManufacturer="", systemSerialNumber="",
                  ups1ratedPower="", ups1ratedCapacityOfBattery="")
    assert _results(out)[0].summary == "Model: 6000VA"
    assert not any(r.summary.startswith("Ratings") for r in _results(out))


# --- environment (THS sensor) -----------------------------------------------

def test_environment_sensor(check):
    discovered, out = _run(check, "UPS Environment", thsOneTempData="243", thsOneHumiData="456")
    assert discovered == [Service()]
    assert [r.summary for r in _results(out)] == ["Temperature: 24.3°C", "Humidity: 46%"]
    assert _metrics(out) == pytest.approx({"env_temperature": 24.3, "env_humidity": 45.6})


@pytest.mark.parametrize("temp, humi, state", [
    ("360", "456", State.WARN),
    ("410", "456", State.CRIT),
    ("90", "456", State.WARN),
    ("243", "750", State.WARN),
    ("243", "850", State.CRIT),
    ("243", "150", State.WARN),
    ("243", "50", State.CRIT),
])
def test_environment_levels(check, temp, humi, state):
    _, out = _run(check, "UPS Environment", thsOneTempData=temp, thsOneHumiData=humi)
    assert _worst(out) == state


def test_environment_sensor_gone_after_discovery(check):
    section = _parse(check)
    plugin = _plugins(check)["UPS Environment"]
    out = list(plugin.check_function(plugin.check_default_parameters, section))
    assert out == [Result(state=State.UNKNOWN, summary="No environmental sensor data")]


# --- bugs the tests found (xfail strict, owner decides) ----------------------

@pytest.mark.xfail(strict=True, reason="BUG: the device's own voltage thresholds "
                   "(inputVoltUpConfig etc.) never apply, the default parameters always win")
def test_device_thresholds_are_the_default_levels(check):
    """README: 'Dynamic thresholds from device configuration when available'.
    Checkmk always passes the plugin's default parameters, so params.get()
    never falls back to the device values."""
    _, out = _run(check, "UPS Input Voltage", ups1inputUPhaseVoltage="245",
                  inputVoltUpConfig="242", inputVoltLowConfig="187")
    assert _worst(out) == State.WARN


@pytest.mark.xfail(strict=True, reason="BUG: upsBaseOutputStatus is read with the APC "
                   "enumeration, XPPC-MIB defines 9 = onBuck, 8 = standBy, 7 = rebooting")
@pytest.mark.parametrize("raw, name", [("9", "onBuck"), ("8", "standBy"), ("7", "rebooting"),
                                       ("6", "onBypass"), ("5", "sleeping"), ("4", "onBoost")])
def test_base_output_status_follows_xppc_mib(check, raw, name):
    _, out = _run(check, "UPS Power Status", upsBaseOutputStatus=raw)
    assert f"Base output status: {name}" in _text(out)


MEASUREMENTS = [
    # service, OID name, label in the summary
    ("UPS Input Voltage", "ups1inputUPhaseVoltage", "Input voltage"),
    ("UPS Output Voltage", "ups1outputUPhaseVoltage", "Output voltage"),
    ("UPS Bypass Voltage", "ups1bypassUPhaseVoltage", "Bypass voltage"),
    ("UPS Battery Voltage", "ups1batteryVoltage", "Battery voltage"),
    ("UPS Battery Current", "ups1batteryChargingAndDischargingCurrent", "Battery current"),
    ("UPS Output Current", "ups1outputUPhaseCurrent", "Output current"),
    ("UPS Battery Temperature", "ups1batteryTemperature", "Temperature"),
    ("UPS Input Frequency", "ups1inputUPhaseFrequency", "Input frequency"),
    ("UPS Output Frequency", "ups1outputFrequency", "Output frequency"),
    ("UPS Bypass Frequency", "ups1bypassFrequency", "Bypass frequency"),
    ("UPS Output Power", "ups1outputUPhaseActivePower", "Output power"),
    ("UPS Output Load", "ups1outputUPhaseLoadRate", "Output load"),
]


@pytest.mark.parametrize("service, name, label", MEASUREMENTS)
def test_no_value_marker_is_not_a_reading(check, service, name, label):
    """-99998 is the card's 'no value': UNKNOWN like Battery Charge and
    Battery Runtime, no metric."""
    _, out = _run(check, service, **{name: "-99998"})
    assert out == [Result(state=State.UNKNOWN, summary=f"{label} data not available")]


def test_non_numeric_runtime_does_not_crash(check):
    _, out = _run(check, "UPS Battery Runtime", ups1batteryTimeRemaining="N/A")
    assert out == [Result(state=State.UNKNOWN,
                          summary="Battery runtime: cannot read 'N/A' as a number")]


def test_parse_keeps_the_text_it_could_not_read(check):
    section = _parse(check, ups1batteryTimeRemaining="N/A", ups1inputUPhaseVoltage="231.9")
    assert section["_unreadable"] == {"battery_runtime_seconds": "N/A"}
    assert "_unreadable" not in _parse(check)


@pytest.mark.parametrize("service, name, label", [
    *MEASUREMENTS,
    ("UPS Battery Charge", "ups1remainingCapacityOfBattery", "Battery charge"),
])
@pytest.mark.parametrize("raw", ["N/A", "abc"])
def test_non_numeric_value_is_unknown(check, service, name, label, raw):
    _, out = _run(check, service, **{name: raw})
    assert out == [Result(state=State.UNKNOWN,
                          summary=f"{label}: cannot read {raw!r} as a number")]


def test_non_numeric_environment_values_are_unknown(check):
    _, out = _run(check, "UPS Environment", thsOneTempData="N/A", thsOneHumiData="456")
    assert _results(out) == [
        Result(state=State.UNKNOWN, summary="Temperature: cannot read 'N/A' as a number"),
        Result(state=State.OK, summary="Humidity: 46%"),
    ]
    assert _metrics(out) == pytest.approx({"env_humidity": 45.6})
    _, out = _run(check, "UPS Environment", thsOneTempData="243", thsOneHumiData="--")
    assert _worst(out) == State.UNKNOWN
    assert "Humidity: cannot read '--' as a number" in _text(out)


# --- version ----------------------------------------------------------------

def test_check_carries_the_released_version():
    # The publish check fails on main when a version file disagrees with
    # the newest released CHANGES.md heading.
    released = re.search(r"^## (\d+\.\d+\.\d+)", (ROOT / "CHANGES.md").read_text(),
                         flags=re.MULTILINE).group(1)
    assert re.search(rf'^__version__ = "{re.escape(released)}"$', CHECK.read_text(),
                     flags=re.MULTILINE)


def test_release_writes_version_into_check(tmp_path):
    """Apply the version_files entry of .github/repo-infra.json to the check
    module, as Create release PR does (a multiline regex, first match)"""
    config = json.loads((ROOT / ".github/repo-infra.json").read_text())
    (spec,) = [f for f in config["version_files"] if (ROOT / f["path"]) == CHECK]
    stamped = re.sub(spec["pattern"], spec["replacement"].replace("$VERSION", "9.8.7"),
                     CHECK.read_text(), count=1, flags=re.MULTILINE)
    assert re.search(spec["verify"].replace("$VERSION", re.escape("9.8.7")), stamped,
                     flags=re.MULTILINE)
    copy = tmp_path / "stamped_check.py"
    copy.write_text(stamped)
    module = load_module(copy, "stamped_check")
    assert module.__version__ == "9.8.7"
