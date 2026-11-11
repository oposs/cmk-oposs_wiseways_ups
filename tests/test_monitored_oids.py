"""monitored_oids.md describes the services, OIDs and levels of the plugin."""

import re

import pytest
from cmk.agent_based.v2 import State
from test_check import (
    CHECK,
    ROOT,
    SERVICES,
    WALK,
    _fetched_oids,
    _plugins,
    _run,
    _worst,
    load_module,
)

DOC = (ROOT / "monitored_oids.md").read_text()


@pytest.fixture(scope="module")
def check():
    return load_module(CHECK, "test_monitored_oids_check")


def _service_sections():
    """'UPS <name>' -> table rows (lists of cells) under '### <name> Service'"""
    sections = {}
    current = None
    for line in DOC.splitlines():
        heading = re.fullmatch(r"#{3,4} (.+) Service\s*", line)
        if heading:
            current = sections.setdefault("UPS " + heading.group(1), [])
        elif line.startswith("#"):
            current = None
        elif current is not None and line.startswith("|"):
            current.append([c.strip() for c in line.strip().strip("|").split("|")])
    return sections


def _examples():
    """OID -> example value as the UPS sends it: '"6000VA"' is 6000VA, '2 (batteryNormal)' is 2"""
    examples = {}
    for line in DOC.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0].startswith(".1.3.6.1."):
            examples[cells[0]] = cells[2].split(" (")[0].strip('"')
    return examples


def test_there_is_a_section_per_service():
    assert set(_service_sections()) == set(SERVICES)


def test_every_fetched_oid_is_documented(check):
    assert set(_fetched_oids(check)) <= set(_examples())


@pytest.mark.parametrize("service", SERVICES)
def test_the_documented_levels_are_the_defaults(check, service):
    rows = _service_sections()[service]
    header, rows = rows[0], rows[2:]
    documented = set()
    if "Thresholds" in header:
        column = header.index("Thresholds")
        for row in rows:
            documented |= {float(n) for n in re.findall(r"\d+(?:\.\d+)?", row[column])}
    defaults = _plugins(check)[service].check_default_parameters or {}
    assert documented == {float(n) for _, levels in defaults.values() for n in levels}


def test_the_service_summary_lists_every_service():
    summary = DOC.split("## Service Summary", 1)[1].split("\n## ", 1)[0]
    assert f"creates {len(SERVICES)} CheckMK services" in summary
    assert re.findall(r"^\d+\. \*\*(UPS [^*]+)\*\*", summary, flags=re.MULTILINE) == SERVICES


@pytest.mark.parametrize("service", SERVICES)
def test_the_documented_examples_are_a_healthy_ups(check, service):
    """Fed to the checks, the example values give OK everywhere."""
    examples = _examples()
    changes = {name: examples[oid] for oid, (name, _) in WALK.items() if oid in examples}
    discovered, out = _run(check, service, **changes)
    assert discovered, service
    assert _worst(out) == State.OK, out
