"""The checks fed with a walk of a real Wiseway network adapter.

The values come from one production device, a 1000 VA online UPS with
three 12 V batteries, walked while it ran on mains. Only the OIDs the
plugin fetches are kept, plus sysDescr, sysObjectID and upsIdentName for
the detection; the serial number is replaced. Values are as Checkmk hands
them to the parse function: upsIdentUPSSoftwareVersion arrives with the
padding and the carriage return the card sends.

All Wiseway adapters of that site report the same sysDescr and the
sysObjectID ".0.1.3.6.1.2.1.33".
"""

import re

import pytest
from cmk.agent_based.v2 import Metric, Result, Service, State
from test_check import (
    CHECK,
    SERVICES,
    _fetched_oids,
    _metrics,
    _plugins,
    _section_def,
    _summaries,
    _text,
    _worst,
    load_module,
)


@pytest.fixture(scope="module")
def check():
    return load_module(CHECK, "test_oposs_wiseways_ups_real_walk")


SYS_DESCR = ".1.3.6.1.2.1.1.1.0"
SYS_OBJECT_ID = ".1.3.6.1.2.1.1.2.0"

REAL = {
    '.1.3.6.1.2.1.1.1.0': 'Wiseway network adapter realizes real-time web monitoring and management of UPS equipment',
    '.1.3.6.1.2.1.1.2.0': '.0.1.3.6.1.2.1.33',
    '.1.3.6.1.2.1.33.1.1.5.0': 'Wiseway3.0',
    '.1.3.6.1.2.1.33.1.1.2.0': '1000VA     ',  # upsIdentModel
    '.1.3.6.1.4.1.44782.1.4.4.1.2.0': 'AEC',  # ups1equipmentManufacturer
    '.1.3.6.1.4.1.44782.1.4.1.5.0': '0000000000000000001A',  # systemSerialNumber
    '.1.3.6.1.2.1.33.1.1.3.0': 'VER 6.02  \r',  # upsIdentUPSSoftwareVersion
    '.1.3.6.1.2.1.33.1.1.4.0': 'V3.06.01.250813A.Release',  # upsIdentAgentSoftwareVersion
    '.1.3.6.1.4.1.44782.1.4.4.1.11.0': '0',  # ups1ratedPower
    '.1.3.6.1.4.1.44782.1.4.4.1.12.0': '9',  # ups1ratedCapacityOfBattery
    '.1.3.6.1.4.1.44782.1.4.4.1.6.0': '2025-12-04',  # ups1installationTime
    '.1.3.6.1.4.1.44782.1.4.4.1.8.0': '2032-01-01',  # ups1maintenanceExpirationTime
    '.1.3.6.1.4.1.44782.1.4.4.1.9.0': '2032-01-01',  # ups1batteryInstallationReplacementTime
    '.1.3.6.1.4.1.44782.1.4.4.1.10.0': '2032-01-01',  # ups1nextMaintenanceTimeOfBattery
    '.1.3.6.1.4.1.44782.1.4.4.1.14.0': '3',  # ups1numberOfBatteries
    '.1.3.6.1.4.1.44782.1.4.4.1.15.0': '3',  # ups1numberOfBatteriesInASingleGroup
    '.1.3.6.1.2.1.33.1.2.1.0': '2',  # upsBatteryStatus
    '.1.3.6.1.4.1.44782.1.4.4.1.16.0': '2',  # ups1batteryStatus
    '.1.3.6.1.2.1.33.1.2.2.0': '0',  # upsSecondsOnBattery
    '.1.3.6.1.4.1.44782.1.4.4.1.18.0': '99.0',  # ups1remainingCapacityOfBattery
    '.1.3.6.1.4.1.44782.1.4.4.1.17.0': '113.0',  # ups1batteryTimeRemaining
    '.1.3.6.1.4.1.44782.1.4.4.1.19.0': '41.2',  # ups1batteryVoltage
    '.1.3.6.1.4.1.44782.1.4.4.1.20.0': '4.50',  # ups1batteryChargingAndDischargingCurrent
    '.1.3.6.1.4.1.44782.1.4.4.1.21.0': '22.0',  # ups1batteryTemperature
    '.1.3.6.1.4.1.44782.1.4.4.1.72.0': '0',  # ups1batteryAbnormal
    '.1.3.6.1.4.1.44782.1.4.4.1.73.0': '0',  # ups1batteryPowered
    '.1.3.6.1.4.1.44782.1.4.4.1.74.0': '0',  # ups1batteryLowVoltage
    '.1.3.6.1.2.1.33.1.3.1.0': '6',  # upsInputLineBads
    '.1.3.6.1.4.1.44782.1.4.4.1.27.0': '233.5',  # ups1inputUPhaseVoltage
    '.1.3.6.1.4.1.44782.1.4.4.1.24.0': '50.0',  # ups1inputUPhaseFrequency
    '.1.3.6.1.4.1.44782.1.4.4.1.77.0': '0',  # ups1inputAbnormal
    '.1.3.6.1.4.1.44782.1.4.4.1.42.0': '230.0',  # ups1outputUPhaseVoltage
    '.1.3.6.1.4.1.44782.1.4.4.1.40.0': '50.0',  # ups1outputFrequency
    '.1.3.6.1.4.1.44782.1.4.4.1.45.0': '0.80',  # ups1outputUPhaseCurrent
    '.1.3.6.1.4.1.44782.1.4.4.1.48.0': '0.20',  # ups1outputUPhaseActivePower
    '.1.3.6.1.4.1.44782.1.4.4.1.51.0': '20.0',  # ups1outputUPhaseLoadRate
    '.1.3.6.1.2.1.33.1.4.1.0': '3',  # upsOutputSource
    '.1.3.6.1.4.1.44782.1.4.4.1.39.0': '3',  # ups1powerSupplyMode
    '.1.3.6.1.4.1.935.1.1.1.4.1.1.0': '2',  # upsBaseOutputStatus
    '.1.3.6.1.4.1.44782.1.4.4.1.78.0': '0',  # ups1outputAbnormal
    '.1.3.6.1.4.1.44782.1.4.4.1.59.0': '233.3',  # ups1bypassUPhaseVoltage
    '.1.3.6.1.4.1.44782.1.4.4.1.57.0': '50.0',  # ups1bypassFrequency
    '.1.3.6.1.4.1.44782.1.4.4.1.80.0': '0',  # ups1bypassStatus
    '.1.3.6.1.4.1.44782.1.4.4.1.71.0': '0',  # ups1abnormalCommunication
    '.1.3.6.1.4.1.44782.1.4.4.1.76.0': '0',  # ups1temperatureAbnormal
    '.1.3.6.1.4.1.44782.1.4.4.1.79.0': '0',  # ups1overLoad
    '.1.3.6.1.4.1.44782.1.4.4.1.81.0': '0',  # ups1fanFailure
    '.1.3.6.1.4.1.44782.1.4.4.1.85.0': '0',  # ups1shutdownRequest
    '.1.3.6.1.4.1.44782.1.4.4.1.86.0': '0',  # ups1testInProgress
    '.1.3.6.1.4.1.44782.1.4.4.1.89.0': '0',  # ups1shutdownImminent
    '.1.3.6.1.4.1.44782.1.4.4.1.93.0': '0',  # ups1lowBatteryShutdownImminent
    '.1.3.6.1.4.1.44782.1.4.4.1.94.0': '1',  # ups1systemStatus
    '.1.3.6.1.4.1.44782.1.1.3.1.0': '0',  # inputVoltUpConfig
    '.1.3.6.1.4.1.44782.1.1.3.2.0': '0',  # inputVoltLowConfig
    '.1.3.6.1.4.1.44782.1.1.3.3.0': '0',  # outputVoltUpConfig
    '.1.3.6.1.4.1.44782.1.1.3.4.0': '0',  # outputVoltLowConfig
    '.1.3.6.1.4.1.44782.1.1.3.5.0': '0',  # upsTempUpConfig
    '.1.3.6.1.4.1.44782.1.1.3.6.0': '0',  # upsOutputLoadUpConfig
    '.1.3.6.1.4.1.44782.1.1.3.7.0': '33',  # upsBatteryVoltLowConfig
    '.1.3.6.1.4.1.44782.1.2.1.1.1.0': '202',  # thsOneTempData
    '.1.3.6.1.4.1.44782.1.2.1.1.2.0': '456',  # thsOneHumiData
}


def _real_parse(check, **changes):
    values = {**REAL, **changes}
    return _section_def(check).parse_function([[[values[oid] for oid in _fetched_oids(check)]]])


def _real_run(check, service):
    plugin = _plugins(check)[service]
    section = _real_parse(check)
    discovered = list(plugin.discovery_function(section))
    if plugin.check_default_parameters is None:
        out = list(plugin.check_function(section))
    else:
        out = list(plugin.check_function(plugin.check_default_parameters, section))
    return discovered, out


def test_the_real_walk_has_every_fetched_oid(check):
    assert set(_fetched_oids(check)) <= set(REAL)


def test_detection_matches_the_real_device(check):
    assert REAL[SYS_DESCR].startswith("Wiseway network adapter")
    assert REAL[SYS_OBJECT_ID] == ".0.1.3.6.1.2.1.33"
    ((oid, pattern, expected),) = _section_def(check).detect[0]
    assert re.fullmatch(pattern, REAL[oid]) is not None and expected


@pytest.mark.parametrize("service", SERVICES)
def test_every_service_is_discovered_on_the_real_device(check, service):
    discovered, _ = _real_run(check, service)
    assert discovered == [Service()]


@pytest.mark.parametrize("service", SERVICES)
def test_the_real_device_on_mains_is_ok(check, service):
    _, out = _real_run(check, service)
    assert _worst(out) == State.OK, _text(out)


def test_real_output_power_is_read_in_kilowatts(check):
    """ups1outputUPhaseActivePower reads 0.20 while the RFC 1628
    upsOutputPower (.1.3.6.1.2.1.33.1.4.4.1.4.1) of the same walk reads
    200 W, the load is 20 % of 1000 VA and 0.80 A flow at 230 V."""
    _, out = _real_run(check, "UPS Output Power")
    assert _summaries(out) == ["Output power: 200W"]
    assert _metrics(out) == {"oposs_wiseways_ups_output_power": pytest.approx(200.0)}


def test_real_identity_strings_lose_the_padding(check):
    _, out = _real_run(check, "UPS System Info")
    summaries = _summaries(out)
    assert summaries[0] == "Model: 1000VA, Mfr: AEC, S/N: 0000000000000000001A"
    assert "Versions: FW: VER 6.02, Agent: V3.06.01.250813A.Release" in summaries


def test_real_measurements(check):
    section = _real_parse(check)
    assert section["input_voltage"] == 233.5
    assert section["output_voltage"] == 230.0
    assert section["battery_voltage"] == 41.2
    assert section["battery_runtime_seconds"] == 113 * 60
    assert section["env_temperature"] == pytest.approx(20.2)
    assert section["env_humidity"] == pytest.approx(45.6)
    assert section["base_output_status"] == "onLine"
    # Unset device thresholds read 0, not empty
    assert section["input_volt_up_config"] == 0.0
    assert section["battery_volt_low_config"] == 33.0


def test_real_battery_current_on_mains(check):
    """Still open: on mains with 99 % charge the card reads +4.50 A (and
    upsBatteryCurrent 45, in 0.1 A). Whether positive means charging needs a
    walk on battery; the check shows positive as charging."""
    _, out = _real_run(check, "UPS Battery Current")
    assert out == [Metric("oposs_wiseways_ups_battery_current", 4.5),
                   Result(state=State.OK, summary="Charging: 4.5A")]


def test_real_battery_voltage_is_ok(check):
    """3 blocks of 12 V float at 41.2 V; 0.6.0 went CRIT here with its
    180/170 V lower levels."""
    _, out = _real_run(check, "UPS Battery Voltage")
    assert out == [Result(state=State.OK, summary="Battery voltage: 41.2V"),
                   Metric("oposs_wiseways_ups_battery_voltage", 41.2)]


def test_real_power_status_is_ok_with_past_line_failures(check):
    """upsInputLineBads reads 6 on mains; 0.6.0 stayed WARN on it for good."""
    _, out = _real_run(check, "UPS Power Status")
    assert _worst(out) == State.OK, _text(out)
    assert "Input line failures: 6 in total" in _summaries(out)


# --- found with the real walk, owner decides (xfail strict) ------------------


@pytest.mark.xfail(strict=True, reason="BUG: ups1powerSupplyMode reads 3 on mains, which "
                   "the check names 'battery'; one value cannot give the right table")
def test_real_power_mode_is_not_battery(check):
    _, out = _real_run(check, "UPS Power Status")
    assert "Power mode: battery" not in _text(out)
