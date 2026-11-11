"""Every metric the checks emit is declared, and every graph can be drawn."""

import importlib.util
import pathlib
import sys

import pytest
from cmk.agent_based.v2 import CheckPlugin, Metric, SimpleSNMPSection
from cmk.graphing.v1 import graphs, metrics, perfometers, translations

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_wiseways_ups"

# A UPS on battery with load and a THS sensor: every service has a value.
FULL = {
    "battery_current": "-12.3", "output_current": "4.2", "output_power": "950",
    "output_load": "35.0", "seconds_on_battery": "120", "input_line_bads": "1",
    "env_temperature": "243", "env_humidity": "456", "input_voltage": "231.9",
    "output_voltage": "230.0", "bypass_voltage": "232.9", "battery_voltage": "217.9",
    "battery_temperature": "28.0", "input_frequency": "50.0", "output_frequency": "50.0",
    "bypass_frequency": "50.0", "battery_charge": "90", "battery_runtime": "15",
    "battery_status": "2", "output_source": "5", "model": "6000VA",
}


def _load(path):
    name = "test_graphing_" + path.parent.name + "_" + path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def check():
    return _load(PLUGIN / "agent_based/oposs_wiseways_ups.py")


@pytest.fixture(scope="module")
def graphing_objects():
    objects = []
    for path in sorted((PLUGIN / "graphing").glob("*.py")):
        objects.extend(vars(_load(path)).values())
    return objects


@pytest.fixture(scope="module")
def declared(graphing_objects):
    return {o.name for o in graphing_objects if isinstance(o, metrics.Metric)}


@pytest.fixture(scope="module")
def emitted(check):
    """Metric names per service, from a walk where every service has data."""
    row = [FULL.get(d.key, "") for d in check.OID_DEFINITIONS]
    (section_def,) = [v for v in vars(check).values() if isinstance(v, SimpleSNMPSection)]
    section = section_def.parse_function([[row]])
    per_service = {}
    for plugin in (v for v in vars(check).values() if isinstance(v, CheckPlugin)):
        assert list(plugin.discovery_function(section)), plugin.service_name
        if plugin.check_default_parameters is None:
            out = plugin.check_function(section)
        else:
            out = plugin.check_function(plugin.check_default_parameters, section)
        per_service[plugin.service_name] = {m.name for m in out if isinstance(m, Metric)}
    return per_service


def test_every_emitted_metric_is_declared(emitted, declared):
    names = set().union(*emitted.values())
    assert names, "the checks emitted no metric at all"
    assert names <= declared


def test_every_declared_metric_is_emitted(emitted, declared):
    assert declared <= set().union(*emitted.values())


def test_graphs_and_perfometers_use_declared_metrics(graphing_objects, declared):
    for obj in graphing_objects:
        if isinstance(obj, graphs.Graph):
            used = {*obj.compound_lines, *obj.simple_lines}
        elif isinstance(obj, perfometers.Perfometer):
            used = set(obj.segments)
        else:
            continue
        assert {u for u in used if isinstance(u, str)} <= declared, obj.name


def test_names_are_unique(graphing_objects):
    for kind in (metrics.Metric, graphs.Graph, perfometers.Perfometer):
        names = [o.name for o in graphing_objects if isinstance(o, kind)]
        assert len(names) == len(set(names)), kind


def _drawable(graph, emitted):
    required = {*graph.compound_lines, *graph.simple_lines} - set(graph.optional)
    return [service for service, names in emitted.items() if required <= names]


DRAWABLE = ["ups_battery_charge", "ups_battery_time", "ups_battery_voltage",
            "ups_output_load", "ups_output_power", "ups_currents", "ups_temperature",
            "ups_env_temperature", "ups_env_humidity", "ups_alarms"]


@pytest.mark.parametrize("name", DRAWABLE)
def test_graph_is_drawn_in_one_service(graphing_objects, emitted, name):
    (graph,) = [o for o in graphing_objects if isinstance(o, graphs.Graph) and o.name == name]
    assert _drawable(graph, emitted)


def test_every_graph_is_listed(graphing_objects):
    names = {o.name for o in graphing_objects if isinstance(o, graphs.Graph)}
    assert names == {*DRAWABLE, "ups_voltages_all", "ups_voltages_ac", "ups_frequencies"}


@pytest.mark.xfail(strict=True, reason="BUG: the graphs UPS All Voltages, UPS AC Voltages "
                   "and UPS Frequencies need metrics of several services and never appear")
@pytest.mark.parametrize("name", ["ups_voltages_all", "ups_voltages_ac", "ups_frequencies"])
def test_combined_graph_is_drawn_in_one_service(graphing_objects, emitted, name):
    """Checkmk draws a graph for one service, from that service's metrics.
    These graphs combine input, output and battery values, which come from
    separate services, so no service ever carries all their metrics."""
    (graph,) = [o for o in graphing_objects if isinstance(o, graphs.Graph) and o.name == name]
    assert _drawable(graph, emitted)


# Metric names up to 0.5.0, and the names the checks emit since.
RENAMED = {
    "battery_charge": "oposs_wiseways_ups_battery_charge",
    "battery_runtime": "oposs_wiseways_ups_battery_runtime",
    "battery_voltage": "oposs_wiseways_ups_battery_voltage",
    "battery_current": "oposs_wiseways_ups_battery_current",
    "temperature": "oposs_wiseways_ups_battery_temperature",
    "env_temperature": "oposs_wiseways_ups_env_temperature",
    "env_humidity": "oposs_wiseways_ups_env_humidity",
    "input_voltage": "oposs_wiseways_ups_input_voltage",
    "output_voltage": "oposs_wiseways_ups_output_voltage",
    "bypass_voltage": "oposs_wiseways_ups_bypass_voltage",
    "input_frequency": "oposs_wiseways_ups_input_frequency",
    "output_frequency": "oposs_wiseways_ups_output_frequency",
    "bypass_frequency": "oposs_wiseways_ups_bypass_frequency",
    "output_load": "oposs_wiseways_ups_output_load",
    "output_power": "oposs_wiseways_ups_output_power",
    "output_current": "oposs_wiseways_ups_output_current",
    "input_line_bads": "oposs_wiseways_ups_input_line_bads",
    "time_on_battery": "oposs_wiseways_ups_time_on_battery",
}


def test_every_emitted_metric_is_prefixed(emitted):
    """Checkmk 3.0 refuses plugin metrics that reuse a built-in name; the
    prefix keeps these apart from the built-in battery_charge, temperature,
    input_voltage and the like."""
    names = set().union(*emitted.values())
    assert names == set(RENAMED.values())
    for name in names:
        assert name.startswith("oposs_wiseways_ups_"), name


def test_no_perfometer_is_named_like_a_metric(graphing_objects, declared):
    for obj in graphing_objects:
        if isinstance(obj, perfometers.Perfometer):
            assert obj.name not in declared | set(RENAMED), obj.name


def test_translations_keep_the_history_of_the_old_names(check, graphing_objects, emitted):
    """The RRDs of 0.5.0 and earlier hold the old names; every check that
    emitted one translates it to the new name."""
    found = [o for o in graphing_objects if isinstance(o, translations.Translation)]
    assert len(found) == 1
    (translation,) = found
    assert translation.translations == {
        old: translations.RenameTo(new) for old, new in RENAMED.items()}
    plugins = {v.service_name: v for v in vars(check).values() if isinstance(v, CheckPlugin)}
    emitting = {plugins[service].name for service, names in emitted.items() if names}
    assert len(emitting) == 17
    assert set(translation.check_commands) == {
        translations.PassiveCheck(name) for name in emitting}
