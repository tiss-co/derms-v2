# from backend.modules.derms import PCSBattery

# load = {
#     1: 320,
#     2: 310,
#     3: 430,
#     4: 370,
#     5: 420,
#     6: 430,
#     7: 310,
#     8: 310,
#     9: 270,
#     10: 350,
#     11: 240,
#     12: 510,
#     13: 510,
#     14: 220,
#     15: 500,
#     16: 420,
#     17: 470,
#     18: 195,
#     19: 610,
#     20: 605,
#     21: 580,
#     22: 570,
#     23: 355,
#     24: 330,
# }


# battery_features = {
#     "soc_max": 1000,
#     "soc_min_coef": 0.1,
#     "soc_available": 1000,
#     "p_max": 500,
#     "p_charge_max": 120,
#     "feeder_max": 600,
#     "charging_margin": 160,
#     "first_chargingـtimes_st": 1,
#     "first_chargingـtimes_et": 10,
#     "second_chargingـtimes_st": 23,
#     "second_chargingـtimes_et": 24,
# }

# programs = [
#     {
#         "name": "GA",
#         "start": 15,
#         "end": 16,
#         "activator": True,
#         "coef": 3,
#     },
#     {
#         "name": "DR",
#         "start": 13,
#         "end": 15,
#         "activator": False,
#         "coef": 4,
#     },
#     {
#         "name": "HOEP",
#         "start": 17,
#         "end": 19,
#         "activator": False,
#         "coef": 5,
#     },
#     {
#         "name": "first_rp_coef",
#         "start": 18,
#         "end": 18,
#         "activator": False,
#         "coef": 1,
#     },
#     {
#         "name": "second_rp_coef",
#         "start": 19,
#         "end": 20,
#         "activator": False,
#         "coef": 2,
#     },
# ]

# pcs_battery = PCSBattery(load=load, battery_features=battery_features, programs=programs)
# pcs_battery.calculate_pcs_battery_consumption()
# # print(pcs_battery.model.Pbch.get_values())
# print(pcs_battery.model.Pbdch.get_values())
# # print(pcs_battery.model.soc.get_values())

from backend.tasks.utils import calculate_pcs_battery_consumption

calculate_pcs_battery_consumption(comp_id=123, battery_id=1)
