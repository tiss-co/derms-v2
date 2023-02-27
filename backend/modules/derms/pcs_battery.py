"""
psc_battery module
"""
import numpy as np
import pytz
from pyomo.environ import (
    Binary,
    ConcreteModel,
    Constraint,
    NonNegativeReals,
    Objective,
    Param,
    RangeSet,
    Set,
    SolverFactory,
    Var,
    value,
)

from backend import configs
from backend.modules.derms import settings

from .logger import logger

tz = pytz.timezone(configs.TIMEZONE)  # consider time zone


class PCSBattery:
    def __init__(self, load: dict, battery_features: dict, programs: list, **kwargs):
        logger.info("Loading input data...")
        # Define battery attributes
        self.soc_max = battery_features.get("soc_max")
        self.soc_min = battery_features.get("soc_min_coef") * self.soc_max
        self.soc_available = battery_features.get("soc_available")
        self.p_max = battery_features.get("p_max")
        self.p_charge_max = battery_features.get("p_charge_max")
        self.feeder_max = battery_features.get("feeder_max")
        self.charging_margin = battery_features.get("charging_margin")
        self.init_soc = self.soc_available

        self.costdch_init = {}
        self.costch_init = {}
        self.costgr_init = {}

        # Create the concrete model
        self.model = ConcreteModel(name="PCS")
        self.model.times = RangeSet(1, 24)

        self.model.non_charging_times = Set()
        self.model.Load = Param(self.model.times, initialize=load)

        self.model.first_chargingـtimes = RangeSet(
            battery_features.get("first_chargingـtimes_st"),
            battery_features.get("first_chargingـtimes_et"),
        )

        self.model.second_chargingـtimes = RangeSet(
            battery_features.get("second_chargingـtimes_st"),
            battery_features.get("second_chargingـtimes_et"),
        )

        inactive_times = RangeSet(1, 24)
        self.cost_coef = []

        for item in programs:

            pgrm = dict()
            pgrm["name"] = item.get("name")
            pgrm["coef"] = settings.PROGRAMS_COEF_MAPPER[item.get("coef")]
            pgrm["active_time"] = RangeSet(item.get("start"), item.get("end")) if item["activator"] else []
            inactive_times -= pgrm["active_time"] if item["activator"] else []
            self.cost_coef.append(pgrm)

        self.model.inactive_times = inactive_times

        # # Sort programs based on coef
        self.cost_coef.sort(key=self.get_costcoef)

        load_max_init = {k: min(self.p_max, v) for k, v in load.items()}
        self.model.load_max = Param(self.model.times, initialize=load_max_init)

        costdch = np.zeros(24, dtype="int64")

        for item in self.cost_coef:
            for i in item.get("active_time", []):
                costdch[i - 1] = item["coef"]

        costdch_init = dict(enumerate(costdch.flatten(), 1))

        self.model.costdch = Param(self.model.times, initialize=costdch_init)

        for i in self.model.times:
            if i in self.model.first_chargingـtimes:
                self.costch_init[i] = settings.charging_coef_modified
                self.costgr_init[i] = settings.grid_coef
            elif i in self.model.second_chargingـtimes:
                self.costch_init[i] = settings.charging_coef_modified
                self.costgr_init[i] = settings.grid_coef_modified
            else:
                self.costch_init[i] = settings.charging_coef
                self.costgr_init[i] = settings.grid_coef
                self.model.non_charging_times.add(i)

        self.model.costch = Param(self.model.times, initialize=self.costch_init)
        self.model.costgr = Param(self.model.times, initialize=self.costgr_init)

        self.model.z = Var()
        self.model.Pbch = Var(self.model.times, within=NonNegativeReals, bounds=(0.0, self.p_charge_max))
        self.model.Pbdch = Var(self.model.times, within=NonNegativeReals, bounds=(0.0, self.p_max))
        self.model.Pbchn = Var(self.model.times, within=NonNegativeReals)
        self.model.Pbdchn = Var(self.model.times, within=NonNegativeReals)
        self.model.soc = Var(
            self.model.times,
            within=NonNegativeReals,
            bounds=(self.soc_min, self.soc_max),
        )
        self.model.Pg = Var(self.model.times, within=NonNegativeReals)
        self.model.Ubch = Var(self.model.times, within=Binary)
        self.model.Ubdch = Var(self.model.times, within=Binary)
        self.model.bch = Var(self.model.times, within=Binary)
        self.model.bdch = Var(self.model.times, within=Binary)

        self.model.obj = Objective(rule=self.obj_rule)
        self.model.electrical_balance = Constraint(self.model.times, rule=self.electrical_balance_rule)
        self.model.constraint_dch = Constraint(self.model.times, rule=self.constraint_dch_rule)
        self.model.constraint_ch = Constraint(self.model.times, rule=self.constraint_ch_rule)
        self.model.constraint_lindch1 = Constraint(self.model.times, rule=self.constraint_lindch1_rule)
        self.model.constraint_lindch2 = Constraint(self.model.times, rule=self.constraint_lindch2_rule)
        self.model.constraint_lindch3 = Constraint(self.model.times, rule=self.constraint_lindch3_rule)
        self.model.constraint_lindch4 = Constraint(self.model.times, rule=self.constraint_lindch4_rule)
        self.model.constraint_lindch5 = Constraint(self.model.times, rule=self.constraint_lindch5_rule)
        self.model.constraint_lindch6 = Constraint(self.model.times, rule=self.constraint_lindch6_rule)
        self.model.constraint_discharge1 = Constraint(self.model.times, rule=self.constraint_discharge1_rule)
        self.model.constraint_discharge2 = Constraint(self.model.times, rule=self.constraint_discharge2_rule)
        self.model.constraint_discharge3 = Constraint(self.model.times, rule=self.constraint_discharge3_rule)
        self.model.constraint_linch1 = Constraint(self.model.times, rule=self.constraint_linch1_rule)
        self.model.constraint_linch2 = Constraint(self.model.times, rule=self.constraint_linch2_rule)
        self.model.constraint_linch3 = Constraint(self.model.times, rule=self.constraint_linch3_rule)
        self.model.constraint_linch4 = Constraint(self.model.times, rule=self.constraint_linch4_rule)
        self.model.constraint_linch5 = Constraint(self.model.times, rule=self.constraint_linch5_rule)
        self.model.constraint_linch6 = Constraint(self.model.times, rule=self.constraint_linch6_rule)
        self.model.constraint_charge1 = Constraint(self.model.times, rule=self.constraint_charge1_rule)
        self.model.constraint_charge2 = Constraint(self.model.times, rule=self.constraint_charge2_rule)
        self.model.constraint_charge3 = Constraint(self.model.times, rule=self.constraint_charge3_rule)

        self.model.constraint_tunecharge1 = Constraint(
            next(item["active_time"] for item in self.cost_coef if item["active_time"]),
            rule=self.constraint_tunecharge1_rule,
        )

        self.model.constraint_tunecharge2 = Constraint(
            self.model.non_charging_times, rule=self.constraint_tunecharge2_rule
        )

        self.model.constraint_tunedischarge1 = Constraint(
            self.model.inactive_times, rule=self.constraint_tunedischarge1_rule
        )

        self.model.constraint_UCbattery = Constraint(self.model.times, rule=self.constraint_UCbattery_rule)
        self.model.constraint_SOCbattery = Constraint(self.model.times, rule=self.constraint_SOCbattery_rule)

    @staticmethod
    def get_costcoef(coeffient):
        return coeffient.get("coef")

    @staticmethod
    def obj_rule(model):
        return sum(
            (-1 * model.costdch[tt] * model.Pbdch[tt])
            + (model.costch[tt] * model.Pbch[tt])
            + (model.costgr[tt] * model.Pg[tt])
            for tt in model.times
        )

    @staticmethod
    def electrical_balance_rule(model, tt):
        return model.Pbdch[tt] + model.Pg[tt] == model.Load[tt] + model.Pbch[tt]

    def constraint_dch_rule(self, model, t):
        return model.Pbdch[t] <= model.Ubdch[t] * self.p_max

    def constraint_ch_rule(self, model, t):
        return model.Pbch[t] <= model.Ubch[t] * self.p_charge_max

    def constraint_lindch1_rule(self, model, t):
        if t > 1:
            return model.soc[t - 1] - model.load_max[t] <= settings.M * model.bdch[t]
        else:
            return self.init_soc - model.load_max[t] <= settings.M * model.bdch[t]

    def constraint_lindch2_rule(self, model, t):
        if t > 1:
            return model.load_max[t] - model.soc[t - 1] <= settings.M * (1 - model.bdch[t])
        else:
            return model.load_max[t] - self.init_soc <= settings.M * (1 - model.bdch[t])

    @staticmethod
    def constraint_lindch3_rule(model, t):
        return model.Pbdchn[t] <= model.load_max[t]

    def constraint_lindch4_rule(self, model, t):
        if t > 1:
            return model.Pbdchn[t] <= model.soc[t - 1]
        else:
            return model.Pbdchn[t] <= self.init_soc

    @staticmethod
    def constraint_lindch5_rule(model, t):
        return model.Pbdchn[t] >= model.load_max[t] - settings.M * (1 - model.bdch[t])

    def constraint_lindch6_rule(self, model, t):
        if t > 1:
            return model.Pbdchn[t] >= model.soc[t - 1] - settings.M * model.bdch[t]
        else:
            return model.Pbdchn[t] >= self.init_soc - settings.M * model.bdch[t]

    def constraint_discharge1_rule(self, model, t):
        return model.Pbdch[t] <= model.Ubdch[t] * settings.M

    @staticmethod
    def constraint_discharge2_rule(model, t):
        return model.Pbdch[t] <= model.Pbdchn[t]

    def constraint_discharge3_rule(self, model, t):
        return model.Pbdch[t] >= model.Pbdchn[t] - settings.M * (1 - model.Ubdch[t])

    def constraint_linch1_rule(self, model, t):
        if t > 1:
            return (self.soc_max - model.soc[t - 1]) - self.p_charge_max <= settings.M * model.bch[t]
        else:
            return (self.soc_max - self.init_soc) - self.p_charge_max <= settings.M * model.bch[t]

    def constraint_linch2_rule(self, model, t):
        if t > 1:
            return self.p_charge_max - (self.soc_max - model.soc[t - 1]) <= settings.M * (1 - model.bch[t])
        else:
            return self.p_charge_max - (self.soc_max - self.init_soc) <= settings.M * (1 - model.bch[t])

    def constraint_linch3_rule(self, model, t):
        return model.Pbchn[t] <= self.p_charge_max

    def constraint_linch4_rule(self, model, t):
        if t > 1:
            return model.Pbchn[t] <= (self.soc_max - model.soc[t - 1])
        else:
            return model.Pbchn[t] <= (self.soc_max - self.init_soc)

    def constraint_linch5_rule(self, model, t):
        return model.Pbchn[t] >= self.p_charge_max - settings.M * (1 - model.bch[t])

    def constraint_linch6_rule(self, model, t):
        if t > 1:
            return model.Pbchn[t] >= (self.soc_max - model.soc[t - 1]) - settings.M * model.bch[t]
        else:
            return model.Pbchn[t] >= (self.soc_max - self.init_soc) - settings.M * model.bch[t]

    def constraint_charge1_rule(self, model, t):
        return model.Pbch[t] <= model.Ubch[t] * settings.M

    @staticmethod
    def constraint_charge2_rule(model, t):
        return model.Pbch[t] <= model.Pbchn[t]

    def constraint_charge3_rule(self, model, t):
        return model.Pbch[t] >= model.Pbchn[t] - settings.M * (1 - model.Ubch[t])

    @staticmethod
    def constraint_tunecharge1_rule(model, t):
        return model.Ubch[t] == 0

    @staticmethod
    def constraint_tunecharge2_rule(model, t):
        return model.Ubch[t] == 0

    @staticmethod
    def constraint_tunedischarge1_rule(model, t):
        return model.Ubdch[t] == 0

    @staticmethod
    def constraint_UCbattery_rule(model, t):
        return model.Ubch[t] + model.Ubdch[t] <= 1

    def constraint_SOCbattery_rule(self, model, t):
        if t > 1:
            return model.soc[t] == model.soc[t - 1] - model.Pbdch[t] + model.Pbch[t]
        else:
            return model.soc[t] == self.init_soc - model.Pbdch[t] + model.Pbch[t]

    def calculate_pcs_battery_consumption(self):
        logger.info("Try to found the solution...")
        solver = SolverFactory("glpk")  # GNU linear programming Kit
        solver.solve(self.model)
