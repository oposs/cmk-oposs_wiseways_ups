"""The rule form builds, and it fits the check parameters of every service."""

import importlib.util
import pathlib
import sys

import pytest
from cmk.agent_based.v2 import CheckPlugin
from cmk.rulesets.v1.form_specs import SimpleLevels
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_wiseways_ups"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def rulesets():
    return _load(PLUGIN / "rulesets/oposs_wiseways_ups.py", "test_oposs_wiseways_ups_rulesets")


@pytest.fixture(scope="module")
def check():
    return _load(PLUGIN / "agent_based/oposs_wiseways_ups.py", "test_oposs_wiseways_ups_check_rs")


@pytest.fixture(scope="module")
def form(rulesets):
    return rulesets.rule_spec_oposs_wiseways_ups.parameter_form()


def _parametrised(check):
    return [v for v in vars(check).values()
            if isinstance(v, CheckPlugin) and v.check_ruleset_name is not None]


def test_one_check_parameter_rule_for_the_host(rulesets):
    rule = rulesets.rule_spec_oposs_wiseways_ups
    assert isinstance(rule, CheckParameters)
    assert rule.name == "oposs_wiseways_ups"
    # The services have no item, so the rule must not ask for one
    assert isinstance(rule.condition, HostCondition)


def test_every_parametrised_check_uses_the_rule(check, rulesets):
    plugins = _parametrised(check)
    assert len(plugins) == 14
    for plugin in plugins:
        assert plugin.check_ruleset_name == rulesets.rule_spec_oposs_wiseways_ups.name


def test_every_form_field_is_optional_simple_levels(form):
    for key, element in form.elements.items():
        assert isinstance(element.parameter_form, SimpleLevels), key
        assert element.required is False, key


def test_every_default_parameter_has_a_form_field(check, form):
    for plugin in _parametrised(check):
        assert set(plugin.check_default_parameters) <= set(form.elements), plugin.name


def test_default_parameters_have_the_simple_levels_shape(check):
    for plugin in _parametrised(check):
        for key, value in plugin.check_default_parameters.items():
            kind, levels = value
            assert kind == "fixed" and len(levels) == 2, (plugin.name, key)


def test_form_prefills_match_the_defaults(check, form):
    for plugin in _parametrised(check):
        for key, (_, levels) in plugin.check_default_parameters.items():
            prefill = form.elements[key].parameter_form.prefill_fixed_levels.value
            assert prefill == levels, (plugin.name, key)


def test_the_check_reads_every_form_field(form):
    """A form field that no check reads is a setting that does nothing."""
    source = (PLUGIN / "agent_based/oposs_wiseways_ups.py").read_text()
    for key in form.elements:
        assert f'params.get("{key}"' in source, key


def test_battery_voltage_prefills_are_those_of_0_5_0(form):
    """0.6.0 moved them to a 218 V string; the Wiseway units in use carry
    3 blocks of 12 V and float at 40.7 to 41.2 V."""
    upper = form.elements["battery_voltage_upper"].parameter_form.prefill_fixed_levels.value
    lower = form.elements["battery_voltage_lower"].parameter_form.prefill_fixed_levels.value
    assert upper == (220.0, 230.0)
    assert lower == (32.0, 30.0)
