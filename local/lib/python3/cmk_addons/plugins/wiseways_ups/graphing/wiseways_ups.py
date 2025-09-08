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

metric_battery_temperature = Metric(
    name="battery_temperature",
    title=Title("Battery Temperature"),
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

# Graph definitions

# Battery status graph - combining charge and runtime
graph_ups_battery_status = Graph(
    name="ups_battery_status",
    title=Title("UPS Battery Status"),
    simple_lines=[
        "battery_charge",
        "battery_runtime",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=100,
    ),
)

# Battery electrical graph - voltage and temperature
graph_ups_battery_electrical = Graph(
    name="ups_battery_electrical",
    title=Title("UPS Battery Electrical"),
    simple_lines=[
        "battery_voltage",
        "battery_temperature",
    ],
)

# Voltages graph - all three voltages on same graph for comparison
graph_ups_voltages = Graph(
    name="ups_voltages",
    title=Title("UPS Voltages"),
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

# Load and power graph
graph_ups_load_power = Graph(
    name="ups_load_power",
    title=Title("UPS Load and Power"),
    simple_lines=[
        "output_load",
        "output_power",
        "output_current",
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