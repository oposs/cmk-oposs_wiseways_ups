"""Every metric the checks emit is declared, and every graph can be drawn."""

import importlib.util
import pathlib
import sys

import pytest
from cmk.agent_based.v2 import CheckPlugin, Metric, SimpleSNMPSection
from cmk.graphing.v1 import graphs, metrics, perfometers

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

