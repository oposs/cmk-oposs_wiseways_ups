#!/usr/bin/env python3

from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import (
    Color,
    DecimalNotation,
    Metric,
    TimeNotation,
    Unit,
)
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.perfometers import Perfometer, FocusRange, Closed

# Define units
unit_percentage = Unit(DecimalNotation("%"))
unit_volts = Unit(DecimalNotation("V"))
unit_hertz = Unit(DecimalNotation("Hz"))
unit_amperes = Unit(DecimalNotation("A"))
unit_watts = Unit(DecimalNotation("W"))
unit_celsius = Unit(DecimalNotation("°C"))
unit_seconds = Unit(TimeNotation())
unit_count = Unit(DecimalNotation(""))

# Battery metrics
metric_battery_charge = Metric(
    name="battery_charge",
    title=Title("Battery Charge"),
    unit=unit_percentage,
    color=Color.GREEN,
)

metric_battery_runtime = Metric(
    name="battery_runtime",
    title=Title("Battery Runtime"),
    unit=unit_seconds,
    color=Color.BLUE,
)

metric_battery_voltage = Metric(
    name="battery_voltage",
    title=Title("Battery Voltage"),
    unit=unit_volts,
    color=Color.PURPLE,
)

metric_battery_current = Metric(
    name="battery_current",
    title=Title("Battery Current"),
    unit=unit_amperes,
    color=Color.CYAN,
)

metric_temperature = Metric(
    name="temperature",
    title=Title("Temperature"),
    unit=unit_celsius,
    color=Color.ORANGE,
)

# Voltage metrics
metric_input_voltage = Metric(
    name="input_voltage",
    title=Title("Input Voltage"),
    unit=unit_volts,
    color=Color.BLUE,
)

metric_output_voltage = Metric(
    name="output_voltage",
    title=Title("Output Voltage"),
    unit=unit_volts,
    color=Color.GREEN,
)

metric_bypass_voltage = Metric(
    name="bypass_voltage",
    title=Title("Bypass Voltage"),
    unit=unit_volts,
    color=Color.ORANGE,
)

# Frequency metrics
metric_input_frequency = Metric(
    name="input_frequency",
    title=Title("Input Frequency"),
    unit=unit_hertz,
    color=Color.BLUE,
)

metric_output_frequency = Metric(
    name="output_frequency",
    title=Title("Output Frequency"),
    unit=unit_hertz,
    color=Color.GREEN,
)

metric_bypass_frequency = Metric(
    name="bypass_frequency",
    title=Title("Bypass Frequency"),
    unit=unit_hertz,
    color=Color.ORANGE,
)

# Load and power metrics
metric_output_load = Metric(
    name="output_load",
    title=Title("Output Load"),
    unit=unit_percentage,
    color=Color.YELLOW,
)

metric_output_power = Metric(
    name="output_power",
    title=Title("Output Power"),
    unit=unit_watts,
    color=Color.RED,
)

metric_output_current = Metric(
    name="output_current",
    title=Title("Output Current"),
    unit=unit_amperes,
    color=Color.CYAN,
)

# Other metrics
metric_input_line_bads = Metric(
    name="input_line_bads",
    title=Title("Input Line Failures"),
    unit=unit_count,
    color=Color.RED,
)

metric_time_on_battery = Metric(
    name="time_on_battery",
    title=Title("Time on Battery"),
    unit=unit_seconds,
    color=Color.ORANGE,
)

# Graph definitions

# Battery percentage graph
graph_ups_battery_charge = Graph(
    name="ups_battery_charge",
    title=Title("UPS Battery Charge"),
    simple_lines=[
        "battery_charge",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=100,
    ),
)

# Battery time metrics graph (seconds)
graph_ups_battery_time = Graph(
    name="ups_battery_time",
    title=Title("UPS Battery Time Metrics"),
    simple_lines=[
        "battery_runtime",
        "time_on_battery",
    ],
    optional=["time_on_battery"],  # Only present when on battery
)

# All voltages graph - all voltages on same graph for comparison
graph_ups_voltages_all = Graph(
    name="ups_voltages_all",
    title=Title("UPS All Voltages"),
    simple_lines=[
        "input_voltage",
        "output_voltage",
        "bypass_voltage",
        "battery_voltage",
    ],
    optional=["bypass_voltage"],  # May not always be present
    minimal_range=MinimalRange(
        lower=0,
        upper=300,
    ),
)

# AC voltages graph (input/output/bypass)
graph_ups_voltages_ac = Graph(
    name="ups_voltages_ac",
    title=Title("UPS AC Voltages"),
    simple_lines=[
        "input_voltage",
        "output_voltage",
        "bypass_voltage",
    ],
    optional=["bypass_voltage"],  # May not always be present
    minimal_range=MinimalRange(
        lower=180,
        upper=260,
    ),
)

# Battery voltage graph
graph_ups_battery_voltage = Graph(
    name="ups_battery_voltage",
    title=Title("UPS Battery Voltage"),
    simple_lines=[
        "battery_voltage",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=300,
    ),
)

# Frequencies graph - all three frequencies for comparison
graph_ups_frequencies = Graph(
    name="ups_frequencies",
    title=Title("UPS Frequencies"),
    simple_lines=[
        "input_frequency",
        "output_frequency",
        "bypass_frequency",
    ],
    optional=["bypass_frequency"],  # May not always be present
    minimal_range=MinimalRange(
        lower=45,
        upper=55,
    ),
)

# Output load percentage graph
graph_ups_output_load = Graph(
    name="ups_output_load",
    title=Title("UPS Output Load"),
    simple_lines=[
        "output_load",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=100,
    ),
)

# Output power graph (watts)
graph_ups_output_power = Graph(
    name="ups_output_power",
    title=Title("UPS Output Power"),
    simple_lines=[
        "output_power",
    ],
)

# Current metrics graph (all currents in amperes)
graph_ups_currents = Graph(
    name="ups_currents",
    title=Title("UPS Currents"),
    simple_lines=[
        "output_current",
        "battery_current",
    ],
    optional=["battery_current"],  # May be zero or not present
)

# Temperature graph
graph_ups_temperature = Graph(
    name="ups_temperature",
    title=Title("UPS Battery Temperature"),
    simple_lines=[
        "temperature",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=50,
    ),
)

# Alarm counters graph
graph_ups_alarms = Graph(
    name="ups_alarms",
    title=Title("UPS Alarm Counters"),
    simple_lines=[
        "input_line_bads",
    ],
)

# Perfometers

# Battery charge perfometer
perfometer_battery_charge = Perfometer(
    name="battery_charge",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(100),
    ),
    segments=["battery_charge"],
)

# Output load perfometer
perfometer_output_load = Perfometer(
    name="output_load",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(100),
    ),
    segments=["output_load"],
)