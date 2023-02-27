"""
Set the inputs of pcs_battery in this module
"""

BATTERY_CAPACITY = 1250  # capacity of the desired battery kWh
SOC_max = BATTERY_CAPACITY * 0.9  # kW   Maximum state of charge of battery, with this trick we consider SOC min
p_max = 500  # kW   Maximum discharging power of battery at time t

# Starting and ending time of charging in the morning and night
# this charging process is calculated based on the remained SOC at time 23 of yesterday
CHARGING_START_TIME1 = 22
CHARGING_END_TIME1 = 24
CHARGING_START_TIME2 = 2
CHARGING_END_TIME2 = 10
feeder_max = 600  # Maximum upper feeder limit
charging_margin = 160  # we consider a margin to prevent making problem for feeder
charge_max = 120  # maximum charging limit at each time
# SPS battery (for Lorama project) gives us the used life cycles of the battery, thus
# in order to calculate remained life cycle, we need total life cycle of that battery
TOTAL_LIFE_CYCLE = 7000
M = 5000  # auxiliary constant for linearization
charging_coef = 10  # charging coefficient
grid_coef = 0  # Grid coefficient

charging_coef_modified = -10  # modified charging coefficient for charging periods
grid_coef_modified = 0  # modified Grid coefficient for charging periods (22-24)

PROGRAMS_COEF_MAPPER = {1: 50000, 2: 5000, 3: 900, 4: 300, 5: 50}
