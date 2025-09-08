#!/usr/bin/env python3

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    SimpleLevels,
    LevelDirection,
    DefaultValue,
    Float,
    TimeSpan,
    TimeMagnitude,
    validators,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    Topic,
    HostAndServiceCondition,
)


# Battery monitoring ruleset
def _form_spec_oposs_wiseways_ups_battery():
    return Dictionary(
        title=Title("OPOSS Wiseways UPS Battery Monitoring"),
        help_text=Help("Configure thresholds for UPS battery monitoring"),
        elements={
            "battery_charge_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Battery charge levels"),
                    help_text=Help("Alert when battery charge drops below these levels"),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(
                        unit_symbol="%",
                        custom_validate=[validators.NumberInRange(0, 100)]
                    ),
                    prefill_fixed_levels=DefaultValue((20.0, 10.0)),
                ),
                required=True,
            ),
            "battery_runtime_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Battery runtime levels"),
                    help_text=Help("Alert when runtime drops below these levels"),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.MINUTE,
                            TimeMagnitude.SECOND,
                        ]
                    ),
                    prefill_fixed_levels=DefaultValue((600.0, 300.0)),  # 10min, 5min
                ),
                required=True,
            ),
            "battery_temp_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Battery temperature upper levels"),
                    help_text=Help("Alert when temperature exceeds these levels"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="°C"),
                    prefill_fixed_levels=DefaultValue((40.0, 45.0)),
                ),
            ),
            "battery_temp_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Battery temperature lower levels"),
                    help_text=Help("Alert when temperature drops below these levels"),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(unit_symbol="°C"),
                    prefill_fixed_levels=DefaultValue((10.0, 5.0)),
                ),
            ),
        },
    )


rule_spec_oposs_wiseways_ups_battery = CheckParameters(
    title=Title("OPOSS Wiseways UPS Battery"),
    topic=Topic.POWER,
    name="oposs_wiseways_ups_battery",
    parameter_form=_form_spec_oposs_wiseways_ups_battery,
    condition=HostAndServiceCondition(),
)


# Power (voltages) monitoring ruleset
def _form_spec_oposs_wiseways_ups_power():
    return Dictionary(
        title=Title("OPOSS Wiseways UPS Power Monitoring"),
        help_text=Help("Configure voltage thresholds for UPS power monitoring"),
        elements={
            "input_voltage_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Input voltage upper levels"),
                    help_text=Help("Alert when input voltage exceeds these levels"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="V",
                        custom_validate=[validators.NumberInRange(0, 500)]
                    ),
                    prefill_fixed_levels=DefaultValue((250.0, 260.0)),
                ),
            ),
            "input_voltage_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Input voltage lower levels"),
                    help_text=Help("Alert when input voltage drops below these levels"),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(
                        unit_symbol="V",
                        custom_validate=[validators.NumberInRange(0, 500)]
                    ),
                    prefill_fixed_levels=DefaultValue((210.0, 200.0)),
                ),
            ),
            "output_voltage_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Output voltage upper levels"),
                    help_text=Help("Alert when output voltage exceeds these levels"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="V",
                        custom_validate=[validators.NumberInRange(0, 500)]
                    ),
                    prefill_fixed_levels=DefaultValue((250.0, 260.0)),
                ),
            ),
            "output_voltage_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Output voltage lower levels"),
                    help_text=Help("Alert when output voltage drops below these levels"),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(
                        unit_symbol="V",
                        custom_validate=[validators.NumberInRange(0, 500)]
                    ),
                    prefill_fixed_levels=DefaultValue((210.0, 200.0)),
                ),
            ),
        },
    )


rule_spec_oposs_wiseways_ups_power = CheckParameters(
    title=Title("OPOSS Wiseways UPS Power"),
    topic=Topic.POWER,
    name="oposs_wiseways_ups_power",
    parameter_form=_form_spec_oposs_wiseways_ups_power,
    condition=HostAndServiceCondition(),
)


# Load monitoring ruleset
def _form_spec_oposs_wiseways_ups_load():
    return Dictionary(
        title=Title("OPOSS Wiseways UPS Load Monitoring"),
        help_text=Help("Configure thresholds for UPS load monitoring"),
        elements={
            "load_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Output load levels"),
                    help_text=Help("Alert when output load exceeds these percentages"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="%",
                        custom_validate=[validators.NumberInRange(0, 100)]
                    ),
                    prefill_fixed_levels=DefaultValue((80.0, 90.0)),
                ),
                required=True,
            ),
        },
    )


rule_spec_oposs_wiseways_ups_load = CheckParameters(
    title=Title("OPOSS Wiseways UPS Load"),
    topic=Topic.POWER,
    name="oposs_wiseways_ups_load",
    parameter_form=_form_spec_oposs_wiseways_ups_load,
    condition=HostAndServiceCondition(),
)


# Frequency monitoring ruleset
def _form_spec_oposs_wiseways_ups_frequency():
    return Dictionary(
        title=Title("OPOSS Wiseways UPS Frequency Monitoring"),
        help_text=Help("Configure frequency thresholds for UPS monitoring"),
        elements={
            "frequency_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Frequency upper levels"),
                    help_text=Help("Alert when frequency exceeds these levels"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="Hz",
                        custom_validate=[validators.NumberInRange(40, 60)]
                    ),
                    prefill_fixed_levels=DefaultValue((51.0, 52.0)),
                ),
                required=True,
            ),
            "frequency_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Frequency lower levels"),
                    help_text=Help("Alert when frequency drops below these levels"),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(
                        unit_symbol="Hz",
                        custom_validate=[validators.NumberInRange(40, 60)]
                    ),
                    prefill_fixed_levels=DefaultValue((49.0, 48.0)),
                ),
                required=True,
            ),
        },
    )


rule_spec_oposs_wiseways_ups_frequency = CheckParameters(
    title=Title("OPOSS Wiseways UPS Frequency"),
    topic=Topic.POWER,
    name="oposs_wiseways_ups_frequency",
    parameter_form=_form_spec_oposs_wiseways_ups_frequency,
    condition=HostAndServiceCondition(),
)