"""The service table and the graph list in README.md match the plugin."""

import importlib.util
import pathlib
import re
import sys

import pytest
from cmk.agent_based.v2 import CheckPlugin, Metric, SimpleSNMPSection
from cmk.graphing.v1 import graphs

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
    name = "test_readme_" + path.parent.name + "_" + path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def check():
    return _load(PLUGIN / "agent_based/oposs_wiseways_ups.py")


@pytest.fixture(scope="module")
def plugins(check):
    return {v.service_name: v for v in vars(check).values() if isinstance(v, CheckPlugin)}


@pytest.fixture(scope="module")
def emitted(check, plugins):
    row = [FULL.get(d.key, "") for d in check.OID_DEFINITIONS]
    (section_def,) = [v for v in vars(check).values() if isinstance(v, SimpleSNMPSection)]
    section = section_def.parse_function([[row]])
    per_service = {}
    for name, plugin in plugins.items():
        if plugin.check_default_parameters is None:
            out = plugin.check_function(section)
        else:
            out = plugin.check_function(plugin.check_default_parameters, section)
        per_service[name] = {m.name for m in out if isinstance(m, Metric)}
    return per_service


@pytest.fixture(scope="module")
def table():
    """Service name -> cells of the service table in README.md"""
    rows = {}
    for line in (ROOT / "README.md").read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        match = re.fullmatch(r"\*\*(UPS [^*]+)\*\*", cells[0]) if line.startswith("|") else None
        if match:
            rows[match.group(1)] = cells[1:]
    return rows


@pytest.fixture(scope="module")
def header():
    for line in (ROOT / "README.md").read_text().splitlines():
        if line.startswith("| Service |"):
            return [c.strip() for c in line.strip().strip("|").split("|")][1:]
    raise AssertionError("README.md has no service table")


def _cell(table, header, service, column):
    return table[service][header.index(column)]


def test_the_table_lists_every_service(table, plugins):
    assert set(table) == set(plugins)


def test_the_table_lists_the_metrics_of_every_service(table, header, emitted):
    for service, names in emitted.items():
        cell = _cell(table, header, service, "Metrics")
        assert set(re.findall(r"`([a-z_]+)`", cell)) == names, service


def _pairs(cell):
    """Warn/crit pairs written as '250/260 V' or '10/5 min', in seconds for min"""
    found = set()
    for warn, crit, unit in re.findall(r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?) ?(min|[^\s,;]*)", cell):
        factor = 60.0 if unit == "min" else 1.0
        found.add((float(warn) * factor, float(crit) * factor))
    return found


def test_the_table_gives_the_default_levels(table, header, plugins):
    for service, plugin in plugins.items():
        cell = _cell(table, header, service, "Default levels (warn/crit)")
        defaults = {tuple(map(float, levels))
                    for _, levels in (plugin.check_default_parameters or {}).values()}
        assert _pairs(cell) == defaults, service


def test_the_table_says_which_services_take_levels_from_the_rule(table, header, plugins):
    for service, plugin in plugins.items():
        cell = _cell(table, header, service, "Rule")
        assert cell == ("yes" if plugin.check_ruleset_name else "no"), service


def _graph_list():
    text = (ROOT / "README.md").read_text()
    section = text.split("## Graphs", 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"^- \*\*([^*]+)\*\*", section, flags=re.MULTILINE))


def test_the_graph_list_names_the_graphs_checkmk_draws(emitted):
    """Checkmk draws a graph inside one service, when that service carries
    every metric the graph needs."""
    drawn = set()
    for path in sorted((PLUGIN / "graphing").glob("*.py")):
        for obj in vars(_load(path)).values():
            if not isinstance(obj, graphs.Graph):
                continue
            required = {*obj.compound_lines, *obj.simple_lines} - set(obj.optional)
            if any(required <= names for names in emitted.values()):
                drawn.add(obj.title.localize(lambda s: s))
    assert _graph_list() == drawn
