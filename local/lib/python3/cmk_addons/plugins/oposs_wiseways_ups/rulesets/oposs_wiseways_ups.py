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
    HostCondition,
)


# Combined UPS monitoring ruleset for all services
def _form_spec_oposs_wiseways_ups():
    return Dictionary(
        title=Title("OPOSS Wiseways UPS Monitoring"),
        help_text=Help("Configure thresholds for all UPS monitoring services"),
        elements={
            # Battery parameters
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
            
            # Power/Voltage parameters
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
            
            # Load parameters
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
            
            # Frequency parameters
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


rule_spec_oposs_wiseways_ups = CheckParameters(
    title=Title("OPOSS Wiseways UPS"),
    topic=Topic.POWER,
    name="oposs_wiseways_ups",
    parameter_form=_form_spec_oposs_wiseways_ups,
    condition=HostCondition(),
)