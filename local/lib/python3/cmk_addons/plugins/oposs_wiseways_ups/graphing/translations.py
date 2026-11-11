"""
Metric translations for the Wiseways UPS checks

Up to version 0.5.0 the metrics had no plugin prefix (battery_charge,
temperature, input_voltage, ...). Checkmk 3.0 refuses plugin metrics that
reuse a built-in name. These translations show the history recorded under
the old names in the graphs of the new, prefixed metrics.
"""

from cmk.graphing.v1 import translations

_RENAMED = {
    "battery_charge": "battery_charge",
    "battery_runtime": "battery_runtime",
    "battery_voltage": "battery_voltage",
    "battery_current": "battery_current",
    "temperature": "battery_temperature",
    "env_temperature": "env_temperature",
    "env_humidity": "env_humidity",
    "input_voltage": "input_voltage",
    "output_voltage": "output_voltage",
    "bypass_voltage": "bypass_voltage",
    "input_frequency": "input_frequency",
    "output_frequency": "output_frequency",
    "bypass_frequency": "bypass_frequency",
    "output_load": "output_load",
    "output_power": "output_power",
    "output_current": "output_current",
    "input_line_bads": "input_line_bads",
    "time_on_battery": "time_on_battery",
}

# The check plugins that emit metrics; each service runs its own check command.
_CHECKS = (
    "input_voltage",
    "output_voltage",
    "bypass_voltage",
    "battery_voltage",
    "battery_current",
    "output_current",
    "temperature",
    "input_frequency",
    "output_frequency",
    "bypass_frequency",
    "output_power",
    "output_load",
    "battery_charge",
    "battery_runtime",
    "battery_status",
    "power_status",
    "environment",
)

translation_oposs_wiseways_ups = translations.Translation(
    name="oposs_wiseways_ups_unprefixed_metrics",
    check_commands=[translations.PassiveCheck(f"oposs_wiseways_ups_{check}") for check in _CHECKS],
    translations={
        old: translations.RenameTo(f"oposs_wiseways_ups_{new}") for old, new in _RENAMED.items()
    },
)
