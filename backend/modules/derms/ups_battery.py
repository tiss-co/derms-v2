import numpy as np
import functools
from datetime import datetime


class UPSBattery:
    def __init__(self,
                 Load,
                 SOC_max=1500,
                 SOC_available=1200,
                 p_max=500,
                 GA_START_TIME=0,
                 GA_END_TIME=0,
                 DR_START_TIME=0,
                 DR_END_TIME=0,
                 HOEP_START_TIME=0,
                 HOEP_END_TIME=0,
                 GA_STATUS=0,
                 DR_STATUS=0,
                 HOEP_STATUS=0,
                 CHARGING_START_TIME=22,
                 CHARGING_END_TIME=24):

        self.SOC_max = SOC_max
        self.SOC_available = SOC_available
        self.p_max = p_max
        self.GA_START_TIME = GA_START_TIME
        self.GA_END_TIME = GA_END_TIME
        self.DR_START_TIME = DR_START_TIME
        self.DR_END_TIME = DR_END_TIME
        self.HOEP_START_TIME = HOEP_START_TIME
        self.HOEP_END_TIME = HOEP_END_TIME
        self.GA_STATUS = GA_STATUS
        self.DR_STATUS = DR_STATUS
        self.HOEP_STATUS = HOEP_STATUS
        self.Load = np.array(Load)
        self.CHARGING_END_TIME = CHARGING_END_TIME
        self.CHARGING_START_TIME = CHARGING_START_TIME

        now = datetime.now().hour

        self.GA, self.DR, self.HOEP = np.zeros((3, 24), dtype="int64")
        self.GA[self.GA_START_TIME - 1:self.GA_END_TIME] = 1
        self.GA[:now] = 0

        self.DR[self.DR_START_TIME - 1:self.DR_END_TIME] = 1
        self.DR[:now] = 0

        self.HOEP[self.HOEP_START_TIME - 1:self.HOEP_END_TIME] = 1
        self.HOEP[:now] = 0

        self.soc, self.p_discharge, self.p_charge = np.zeros((3, 24))  # Initialize variables
        self.soc[0] = self.SOC_available

    def daily_activity_hours(self):
        activation_mode = np.zeros(24, dtype='int32')

        if self.HOEP_STATUS:
            activation_mode[self.HOEP == 1] = 3
        if self.DR_STATUS:
            activation_mode[self.DR == 1] = 2
        if self.GA_STATUS:
            activation_mode[self.GA == 1] = 1

        return activation_mode

    def check_program_activation(self):
        switcher = {
            (1, 0, 0): functools.partial(self.one_mode_activation, self.GA),
            (0, 1, 0): functools.partial(self.one_mode_activation, self.DR),
            (0, 0, 1): functools.partial(self.one_mode_activation, self.HOEP),
            (1, 1, 0): self.sub_condition_1,
            (1, 0, 1): self.sub_condition_2,
            (0, 1, 1): self.sub_condition_3,
            (1, 1, 1): self.sub_condition_4,
        }

        return switcher.get((self.GA_STATUS, self.DR_STATUS, self.HOEP_STATUS), lambda: "Error: Invalid arguments")()

    def sub_condition_1(self):
        if (self.GA_START_TIME < self.DR_START_TIME) and (self.GA_END_TIME + 1 < self.DR_START_TIME):
            self.indicator_4()
        elif (self.GA_START_TIME <= self.DR_START_TIME) and (self.GA_END_TIME + 1 >= self.DR_START_TIME):
            self.indicator_5()
        elif (self.DR_START_TIME < self.GA_START_TIME) and (self.DR_END_TIME + 1 < self.GA_START_TIME):
            self.indicator_6()
        elif (self.DR_START_TIME <= self.GA_START_TIME) and (self.DR_END_TIME + 1 >= self.GA_START_TIME):
            self.indicator_7()

    def sub_condition_2(self):
        if (self.GA_START_TIME < self.HOEP_START_TIME) and (self.GA_END_TIME + 1 < self.HOEP_START_TIME):
            self.indicator_8()
        elif (self.GA_START_TIME <= self.HOEP_START_TIME) and (self.GA_END_TIME + 1 >= self.HOEP_START_TIME):
            self.indicator_9()
        elif (self.HOEP_START_TIME < self.GA_START_TIME) and (self.HOEP_END_TIME + 1 < self.GA_START_TIME):
            self.indicator_10()
        elif (self.HOEP_START_TIME <= self.GA_START_TIME) and (self.HOEP_END_TIME + 1 >= self.GA_START_TIME):
            self.indicator_11()

    def sub_condition_3(self):
        if (self.DR_START_TIME < self.HOEP_START_TIME) and (self.DR_END_TIME + 1 < self.HOEP_START_TIME):
            self.indicator_12()
        elif (self.DR_START_TIME <= self.HOEP_START_TIME) and (self.DR_END_TIME + 1 >= self.HOEP_START_TIME):
            self.indicator_13()
        elif (self.HOEP_START_TIME < self.DR_START_TIME) and (self.HOEP_END_TIME + 1 < self.DR_START_TIME):
            self.indicator_14()
        elif (self.HOEP_START_TIME <= self.DR_START_TIME) and (self.HOEP_END_TIME + 1 >= self.DR_START_TIME):
            self.indicator_15()

    def sub_condition_4(self):
        if (self.GA_START_TIME < self.DR_START_TIME) and (self.GA_END_TIME + 1 < self.DR_START_TIME) and (self.GA_START_TIME < self.HOEP_START_TIME):
            if (self.DR_START_TIME < self.HOEP_START_TIME) and (self.DR_END_TIME + 1 < self.HOEP_START_TIME):
                self.indicator_16()
            elif (self.DR_START_TIME <= self.HOEP_START_TIME) and (self.DR_END_TIME + 1 >= self.HOEP_START_TIME):
                self.indicator_17()
            elif (self.HOEP_START_TIME < self.DR_START_TIME) and (self.HOEP_END_TIME + 1 < self.DR_START_TIME):
                self.indicator_18()
            elif (self.HOEP_START_TIME <= self.DR_START_TIME) and (self.HOEP_END_TIME + 1 >= self.DR_START_TIME):
                self.indicator_19()

        elif (self.GA_START_TIME <= self.DR_START_TIME) and (self.GA_END_TIME + 1 >= self.DR_START_TIME) and (self.GA_START_TIME < self.HOEP_START_TIME):
            if (self.DR_START_TIME < self.HOEP_START_TIME) and (self.DR_END_TIME + 1 < self.HOEP_START_TIME):
                self.indicator_20()
            elif (self.DR_START_TIME <= self.HOEP_START_TIME) and (self.DR_END_TIME + 1 >= self.HOEP_START_TIME):
                self.indicator_21()
            elif (self.HOEP_START_TIME < self.DR_START_TIME) and (self.HOEP_END_TIME + 1 < self.DR_START_TIME):
                self.indicator_22()
            elif (self.HOEP_START_TIME <= self.DR_START_TIME) and (self.HOEP_END_TIME + 1 >= self.DR_START_TIME):
                self.indicator_23()

        elif (self.DR_START_TIME < self.GA_START_TIME) and (self.DR_END_TIME + 1 < self.GA_START_TIME) and (self.DR_START_TIME < self.HOEP_START_TIME):
            if (self.GA_START_TIME < self.HOEP_START_TIME) and (self.GA_END_TIME + 1 < self.HOEP_START_TIME):
                self.indicator_24()
            if (self.GA_START_TIME <= self.HOEP_START_TIME) and (self.GA_END_TIME + 1 >= self.HOEP_START_TIME):
                self.indicator_25()

        elif (self.DR_START_TIME <= self.GA_START_TIME) and (self.DR_END_TIME + 1 >= self.GA_START_TIME) and (self.DR_START_TIME < self.HOEP_START_TIME):
            if (self.GA_START_TIME < self.HOEP_START_TIME) and (self.GA_END_TIME + 1 < self.HOEP_START_TIME):
                self.indicator_26()
            if (self.GA_START_TIME <= self.HOEP_START_TIME) and (self.GA_END_TIME + 1 >= self.HOEP_START_TIME):
                self.indicator_27()

        elif (self.HOEP_START_TIME < self.GA_START_TIME) and (self.HOEP_END_TIME + 1 < self.GA_START_TIME) and (self.HOEP_START_TIME < self.DR_START_TIME):
            if (self.GA_START_TIME < self.DR_START_TIME) and (self.GA_END_TIME + 1 < self.DR_START_TIME):
                self.indicator_28()
            if (self.GA_START_TIME <= self.DR_START_TIME) and (self.GA_END_TIME + 1 >= self.DR_START_TIME):
                self.indicator_29()

        elif (self.HOEP_START_TIME <= self.GA_START_TIME) and (self.HOEP_END_TIME + 1 >= self.GA_START_TIME) and (self.HOEP_START_TIME < self.DR_START_TIME):
            if (self.GA_START_TIME < self.DR_START_TIME) and (self.GA_END_TIME + 1 < self.DR_START_TIME):
                self.indicator_30()
            if (self.GA_START_TIME <= self.DR_START_TIME) and (self.GA_END_TIME + 1 >= self.DR_START_TIME):
                self.indicator_31()

        if (self.HOEP_START_TIME < self.DR_START_TIME) and (self.HOEP_END_TIME + 1 < self.DR_START_TIME) and (self.HOEP_START_TIME < self.GA_START_TIME):
            if (self.DR_START_TIME < self.GA_START_TIME) and (self.DR_END_TIME + 1 < self.GA_START_TIME):
                self.indicator_32()
            if (self.DR_START_TIME <= self.GA_START_TIME) and (self.DR_END_TIME + 1 >= self.GA_START_TIME):
                self.indicator_33()

        elif (self.HOEP_START_TIME <= self.DR_START_TIME) and (self.HOEP_END_TIME + 1 >= self.DR_START_TIME) and (self.HOEP_START_TIME < self.GA_START_TIME):
            if (self.DR_START_TIME < self.GA_START_TIME) and (self.DR_END_TIME + 1 < self.GA_START_TIME):
                self.indicator_34()
            if (self.DR_START_TIME <= self.GA_START_TIME) and (self.DR_END_TIME + 1 >= self.GA_START_TIME):
                self.indicator_35()

        elif (self.DR_START_TIME < self.HOEP_START_TIME) and (self.DR_END_TIME + 1 < self.HOEP_START_TIME) and (self.DR_START_TIME < self.GA_START_TIME):
            if (self.HOEP_START_TIME < self.GA_START_TIME) and (self.HOEP_END_TIME + 1 < self.GA_START_TIME):
                self.indicator_36()
            if (self.HOEP_START_TIME <= self.GA_START_TIME) and (self.HOEP_END_TIME + 1 >= self.GA_START_TIME):
                self.indicator_37()

        elif (self.DR_START_TIME <= self.HOEP_START_TIME) and (self.DR_END_TIME + 1 >= self.HOEP_START_TIME) and (self.DR_START_TIME < self.GA_START_TIME):
            if (self.HOEP_START_TIME < self.GA_START_TIME) and (self.HOEP_END_TIME + 1 < self.GA_START_TIME):
                self.indicator_38()
            if (self.HOEP_START_TIME <= self.GA_START_TIME) and (self.HOEP_END_TIME + 1 >= self.GA_START_TIME):
                self.indicator_39()

        if (self.GA_START_TIME == self.DR_START_TIME) and (self.GA_START_TIME == self.HOEP_START_TIME):
            self.indicator_40()

    def one_mode_activation(self, activity_times):
        self.p_discharge = self.calculate_p_discharge(activity_times, self.SOC_available, activity_times.sum())

        for i in range(1, 24):
            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_4(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())
        for i in range(1, 24):
            if (self.GA_END_TIME < i + 1 < self.DR_START_TIME) and (self.soc[i - 1] < self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.DR[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.DR_START_TIME - 2], self.DR.sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_5(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())  # GA is activated

        for i in range(1, 24):
            if self.DR[i] and not self.GA[i] and self.soc[i - 1] > 0:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.GA_END_TIME - 1], (self.DR - self.DR * self.GA).sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_6(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())
        SOC_need = max(0, self.p_discharge.sum() - max(0, (self.p_max * (self.GA_START_TIME - self.DR_END_TIME - 1))))
        SOC_extra = self.SOC_available - SOC_need

        for i in range(1, 24):
            if self.DR[i] and self.SOC_available > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, SOC_extra, self.DR.sum())[i]

            if (self.DR_END_TIME < i + 1 < self.GA_START_TIME) and (self.soc[i - 1] != self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_7(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())
        SOC_need = max(0, self.p_discharge.sum() - max(0, (self.p_max * (self.GA_START_TIME - self.DR_END_TIME - 1))))
        SOC_extra = self.SOC_available - SOC_need

        for i in range(1, 24):
            if self.DR[i] and self.SOC_available > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, SOC_extra, (self.DR - self.DR * self.GA).sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_8(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())

        for i in range(1, 24):
            if (self.GA_END_TIME < i + 1 < self.HOEP_START_TIME) and (self.soc[i - 1] < self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.HOEP[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.soc[self.HOEP_START_TIME - 2], self.HOEP.sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_9(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())  # GA is activated

        for i in range(1, 24):
            if self.HOEP[i] and not self.GA[i] and self.soc[i - 1] > 0:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.soc[self.GA_END_TIME - 1], (self.HOEP - self.HOEP * self.GA).sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_10(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())
        SOC_need = max(0, self.p_discharge.sum() - max(0, (self.p_max * (self.GA_START_TIME - self.HOEP_END_TIME - 1))))
        SOC_extra = self.SOC_available - SOC_need

        for i in range(1, 24):
            if self.HOEP[i] and self.SOC_available > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, SOC_extra, self.HOEP.sum())[i]

            if (self.HOEP_END_TIME < i + 1 < self.GA_START_TIME) and (self.soc[i - 1] < self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i]))

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_11(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())
        SOC_need = max(0, self.p_discharge.sum() - max(0, (self.p_max * (self.GA_START_TIME - self.HOEP_END_TIME - 1))))
        SOC_extra = self.SOC_available - SOC_need

        for i in range(1, 24):
            if self.HOEP[i] and self.SOC_available > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, SOC_extra, (self.HOEP - self.HOEP * self.GA).sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_12(self):
        self.p_discharge = self.calculate_p_discharge(self.DR, self.SOC_available, self.DR.sum())

        for i in range(1, 24):
            if (self.DR_END_TIME < i + 1 < self.HOEP_START_TIME) and (self.soc[i - 1] < self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.HOEP[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.soc[self.HOEP_START_TIME - 2], self.HOEP.sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_13(self):
        self.p_discharge = self.calculate_p_discharge(self.DR, self.SOC_available, self.DR.sum())  # DR is activated

        for i in range(1, 24):
            if self.HOEP[i] and not self.DR[i] and self.soc[i - 1] > 0:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.soc[self.DR_END_TIME - 1], (self.HOEP - self.HOEP * self.DR).sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_14(self):
        self.p_discharge = self.calculate_p_discharge(self.DR, self.SOC_available, self.DR.sum())
        SOC_need = max(0, self.p_discharge.sum() - max(0, (self.p_max * (self.DR_START_TIME - self.HOEP_END_TIME - 1))))
        SOC_extra = self.SOC_available - SOC_need

        for i in range(1, 24):
            if self.HOEP[i] and self.SOC_available > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, SOC_extra, self.HOEP.sum())[i]

            if (self.HOEP_END_TIME < i + 1 < self.DR_START_TIME) and (self.soc[i - 1] < self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i]))

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_15(self):
        self.p_discharge = self.calculate_p_discharge(self.DR, self.SOC_available, self.DR.sum())

        SOC_need = max(0, self.p_discharge.sum() - max(0, (self.p_max * (self.DR_START_TIME - self.HOEP_END_TIME - 1))))
        SOC_extra = self.SOC_available - SOC_need

        for i in range(1, 24):
            if self.HOEP[i] and self.SOC_available > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, SOC_extra, (self.HOEP - self.HOEP * self.DR).sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_16(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())

        for i in range(1, 24):
            if (self.GA_END_TIME < i + 1 < self.DR_START_TIME) and (self.soc[i - 1] != self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

        for i in range(1, 24):
            if self.DR[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.DR_START_TIME - 2], self.DR.sum())[i]

            if (self.DR_END_TIME < i + 1 < self.HOEP_START_TIME) and (self.soc[i - 1] < self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.HOEP[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.soc[self.HOEP_START_TIME - 2], self.HOEP.sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_17(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())

        for i in range(1, 24):
            if (self.GA_END_TIME < i + 1 < self.DR_START_TIME) and (self.soc[i - 1] != self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

        for i in range(1, 24):
            if self.DR[i] and self.soc[i - 1] > 0:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.DR_START_TIME - 2], self.DR.sum())[i]

            if self.HOEP[i] and not self.DR[i] and self.soc[i - 1] > 0:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.soc[self.DR_END_TIME - 1], (self.HOEP - self.DR * self.HOEP).sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_18(self):
        desired_SOC = max(self.GA_END_TIME, self.HOEP_START_TIME - 1)
        hoep_charge_load_number = 0
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())

        for i in range(1, 24):
            if (self.GA_END_TIME < i + 1 < self.HOEP_START_TIME) and (self.soc[i - 1] != self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

        soc_test = self.soc[desired_SOC - 1] - self.p_discharge[desired_SOC] + min(self.p_max, (self.SOC_max - self.soc[desired_SOC - 1]))

        for i in range(desired_SOC, self.DR_START_TIME):
            if soc_test < self.SOC_max:
                soc_test += min(self.p_max, (self.SOC_max - soc_test))

        p_discharge_DR = self.calculate_p_discharge(self.DR, soc_test, self.DR.sum())
        SOC_need = max(0, p_discharge_DR.sum() - max(0, (self.p_max * (self.DR_START_TIME - max(self.GA_END_TIME, self.HOEP_END_TIME) - 1))))

        for i in range(1, 24):
            if self.HOEP[i] and not self.GA[i]:
                if self.soc[(desired_SOC - 1) + hoep_charge_load_number] <= SOC_need:
                    if self.soc[(desired_SOC - 1) + hoep_charge_load_number] != self.SOC_max:
                        self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[(desired_SOC - 1) + hoep_charge_load_number]))
                        hoep_charge_load_number += 1
                        self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]
                else:
                    self.p_discharge[i] = \
                        self.calculate_p_discharge(self.HOEP, self.soc[(desired_SOC - 1) + hoep_charge_load_number] - SOC_need,
                                                   (self.HOEP - self.HOEP * self.GA).sum() - hoep_charge_load_number)[i]

            if (max(self.GA_END_TIME, self.HOEP_END_TIME) - 1 < i < self.DR_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.DR[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.DR_START_TIME - 2], self.DR.sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_19(self):
        desired_SOC = max(self.GA_END_TIME, self.HOEP_START_TIME - 1)
        hoep_charge_load_number = 0
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())

        for i in range(1, 24):
            if (self.GA_END_TIME < i + 1 < self.HOEP_START_TIME) and (self.soc[i - 1] != self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

        soc_test = self.soc[desired_SOC - 1] - self.p_discharge[desired_SOC] + min(self.p_max, (self.SOC_max - self.soc[desired_SOC - 1]))

        for i in range(desired_SOC, self.DR_START_TIME):
            if soc_test < self.SOC_max:
                soc_test += min(self.p_max, (self.SOC_max - soc_test))

        p_discharge_DR = self.calculate_p_discharge(self.DR, soc_test, self.DR.sum())
        SOC_need = max(0, p_discharge_DR.sum() - max(0, (self.p_max * (self.DR_START_TIME - self.HOEP_END_TIME - 1))))

        for i in range(1, 24):
            if self.HOEP[i] and not self.GA[i] and not self.DR[i]:
                if self.soc[(desired_SOC - 1) + hoep_charge_load_number] <= SOC_need:
                    if self.soc[(desired_SOC - 1) + hoep_charge_load_number] != self.SOC_max:
                        self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[(desired_SOC - 1) + hoep_charge_load_number]))
                        hoep_charge_load_number += 1
                        self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]
                else:
                    self.p_discharge[i] = \
                        self.calculate_p_discharge(self.HOEP, self.soc[(desired_SOC - 1) + hoep_charge_load_number] - SOC_need,
                                                   self.HOEP[~np.logical_or(self.GA, self.DR)].sum() - hoep_charge_load_number)[i]

            if self.DR[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.DR_START_TIME - 2], self.DR.sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_20(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())

        for i in range(1, 24):
            if self.DR[i] and not self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.GA_END_TIME - 1], self.DR[~np.logical_and(self.DR, self.GA)].sum())[i]

            if (max(self.GA_END_TIME, self.DR_END_TIME) < i + 1 < self.HOEP_START_TIME) and (self.soc[i - 1] < self.SOC_max):
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.HOEP[i] and not self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.soc[max(self.GA_END_TIME - 1, self.HOEP_START_TIME - 2)], self.HOEP[~(self.GA == 1)].sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_21(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())

        for i in range(1, 24):
            if self.DR[i] and not self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.GA_END_TIME - 1], self.DR[~(self.GA == 1)].sum())[i]

            if self.HOEP[i] and not self.GA[i] and not self.DR[i]:
                self.p_discharge[i] = \
                    self.calculate_p_discharge(self.HOEP, self.soc[max(self.GA_END_TIME - 1, self.DR_END_TIME - 1)], self.HOEP[~((self.GA == 1) | (self.DR == 1))].sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_22(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())

        for i in range(1, 24):
            # based on the condition, always we have HOEP program beside GA
            if self.DR[i] and not self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.GA_END_TIME - 1], self.DR[~(self.GA == 1)].sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_23(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())

        for i in range(1, 24):
            if self.DR[i] and not self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.GA_END_TIME - 1], self.DR[~(self.GA == 1)].sum())[i]

            if self.HOEP[i] and not self.GA[i] and not self.DR[i]:
                self.p_discharge[i] = \
                    self.calculate_p_discharge(self.HOEP, self.soc[max(self.GA_END_TIME, self.DR_END_TIME) - 1], self.HOEP[~((self.GA == 1) | (self.DR == 1))].sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_24(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())
        SOC_need = max(0, self.p_discharge.sum() - max(0, (self.p_max * (self.GA_START_TIME - self.DR_END_TIME - 1))))
        soc_extra = self.SOC_available - SOC_need

        for i in range(1, 24):
            if self.DR[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, soc_extra, self.DR.sum())[i]

            if (self.DR_END_TIME - 1 < i < self.GA_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if (self.GA_END_TIME - 1 < i < self.HOEP_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.HOEP[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.soc[self.HOEP_START_TIME - 2], self.HOEP.sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_25(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())
        SOC_need = max(0, self.p_discharge.sum() - max(0, (self.p_max * (self.GA_START_TIME - self.DR_END_TIME - 1))))
        soc_extra = self.SOC_available - SOC_need

        for i in range(1, 24):

            if self.DR[i] and self.SOC_available > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, soc_extra, self.DR.sum())[i]

            if (self.DR_END_TIME < i + 1 < self.GA_START_TIME) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.HOEP[i] and not self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(np.multiply(~np.logical_and(self.GA, self.HOEP), self.HOEP), self.soc[self.GA_END_TIME - 1],
                                                                 self.HOEP[~np.logical_and(self.GA, self.HOEP)].sum())[i]
            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_26(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())
        SOC_need = max(0, self.p_discharge.sum() - max(0, (self.p_max * (self.GA_START_TIME - self.DR_END_TIME - 1))))
        soc_extra = self.SOC_available - SOC_need

        for i in range(1, 24):
            if self.DR[i] and not self.GA[i] and self.SOC_available > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, soc_extra, self.DR[~np.logical_and(self.DR, self.GA)].sum())[i]

            if (max(self.GA_END_TIME, self.DR_END_TIME) < i + 1 < self.HOEP_START_TIME) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.HOEP[i] and not self.DR[i] and self.soc[i - 1] > 0.001:
                self.p_discharge[i] = \
                    self.calculate_p_discharge(self.HOEP, self.soc[max(self.DR_END_TIME - 1, self.HOEP_START_TIME - 2)], self.HOEP[~np.logical_and(self.DR, self.HOEP)].sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_27(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())
        SOC_need = max(0, self.p_discharge.sum() - max(0, (self.p_max * (self.GA_START_TIME - self.DR_END_TIME - 1))))
        soc_extra = self.SOC_available - SOC_need

        for i in range(1, 24):
            if self.DR[i] and not self.GA[i] and self.SOC_available > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, soc_extra, self.DR[~(self.GA == 1)].sum())[i]

            if self.HOEP[i] and not self.DR[i] and not self.GA[i] and self.soc[i - 1] > 0.001:
                self.p_discharge[i] = \
                    self.calculate_p_discharge(np.multiply(~((self.GA == 1) | (self.DR == 1)), self.HOEP), self.soc[max(self.DR_END_TIME, self.GA_END_TIME) - 1],
                                               self.HOEP[~((self.GA == 1) | (self.DR == 1))].sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_28(self):
        for i in range(1, 24):
            if self.HOEP[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.p_max * (self.GA_START_TIME - self.HOEP_END_TIME - 1), self.HOEP.sum())[i]

            if (self.HOEP_END_TIME - 1 < i < self.GA_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))
            if self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.GA, self.soc[self.GA_START_TIME - 2], self.GA.sum())[i]

            if (self.GA_END_TIME - 1 < i < self.DR_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.DR[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.DR_START_TIME - 2], self.DR.sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_29(self):
        for i in range(1, 24):
            if self.HOEP[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.p_max * (self.GA_START_TIME - self.HOEP_END_TIME - 1), self.HOEP.sum())[i]

            if (self.HOEP_END_TIME - 1 < i < self.GA_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.GA, self.soc[self.GA_START_TIME - 2], self.GA.sum())[i]

            if self.DR[i] and not self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.GA_END_TIME - 1], self.DR[~(self.GA == 1)].sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_30(self):
        self.indicator_4()

    def indicator_31(self):
        self.indicator_5()

    def indicator_32(self):
        for i in range(1, 24):
            if self.HOEP[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.p_max * (self.DR_START_TIME - self.HOEP_END_TIME - 1), self.HOEP.sum())[i]

            if (self.HOEP_END_TIME - 1 < i < self.DR_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.GA, self.soc[self.DR_START_TIME - 2], self.GA.sum())[i]
                SOC_need = max(0, self.p_discharge[self.GA == 1].sum() - max(0, (self.p_max * (self.GA_START_TIME - self.DR_END_TIME - 1))))
                soc_extra = self.soc[self.DR_START_TIME - 2] - SOC_need
            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]
        for i in range(1, 24):

            if self.DR[i] and self.soc[self.DR_START_TIME - 2] > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, soc_extra, self.DR.sum())[i]

            if (self.DR_END_TIME - 1 < i < self.GA_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_33(self):
        for i in range(1, 24):
            if self.HOEP[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.HOEP, self.p_max * (self.DR_START_TIME - self.HOEP_END_TIME - 1), self.HOEP.sum())[i]

            if (self.HOEP_END_TIME - 1 < i < self.DR_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.GA[i]:
                self.p_discharge[i] = self.calculate_p_discharge(self.GA, self.soc[self.DR_START_TIME - 2], self.GA.sum())[i]
                SOC_need = max(0, self.p_discharge[self.GA == 1].sum())
                soc_extra = self.soc[self.DR_START_TIME - 2] - SOC_need
            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]
        for i in range(1, 24):

            if self.DR[i] and not self.GA[i] and self.soc[self.DR_START_TIME - 2] > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(np.multiply(~np.logical_and(self.GA, self.DR), self.DR), soc_extra, self.DR[~(self.GA == 1)].sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_34(self):
        self.indicator_6()

    def indicator_35(self):
        self.indicator_7()

    def indicator_36(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_max, self.GA.sum())
        p_discharge_GA = self.p_discharge.sum()
        SOC_need = max(0, p_discharge_GA - max(0, (self.p_max * (self.GA_START_TIME - self.HOEP_END_TIME - 1 + self.HOEP_START_TIME - self.DR_END_TIME - 1))))
        soc_extra = self.SOC_max - SOC_need

        for i in range(1, 24):
            if self.DR[i] and self.SOC_max > SOC_need:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, soc_extra, self.DR.sum())[i]

            if (self.DR_END_TIME - 1 < i < self.HOEP_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if self.HOEP[i] and (self.soc[self.HOEP_START_TIME - 2] - p_discharge_GA + (self.p_max * (self.GA_START_TIME - self.HOEP_END_TIME - 1))) > 0:
                self.p_discharge[i] = \
                    self.calculate_p_discharge(self.HOEP, self.soc[self.HOEP_START_TIME - 2] - p_discharge_GA + (self.p_max * (self.GA_START_TIME - self.HOEP_END_TIME - 1)),
                                               self.HOEP.sum())[i]

            if (self.HOEP_END_TIME - 1 < i < self.GA_START_TIME - 1) and self.soc[i - 1] != self.SOC_max:
                self.p_charge[i] = min(self.p_max, (self.SOC_max - self.soc[i - 1]))

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def indicator_37(self):
        self.indicator_6()

    def indicator_38(self):
        if self.DR_END_TIME + 1 < self.GA_START_TIME:
            self.indicator_6()
        else:
            self.indicator_7()

    def indicator_39(self):
        if self.DR_END_TIME + 1 < self.GA_START_TIME:
            self.indicator_6()
        else:
            self.indicator_7()

    def indicator_40(self):
        self.p_discharge = self.calculate_p_discharge(self.GA, self.SOC_available, self.GA.sum())

        for i in range(1, 24):
            if self.DR[i] and not self.GA[i] and self.DR_END_TIME > self.GA_END_TIME and self.soc[i - 1] > 0.001:
                self.p_discharge[i] = self.calculate_p_discharge(self.DR, self.soc[self.GA_END_TIME - 1], self.DR[~(self.GA == 1)].sum())[i]

            if self.HOEP[i] and not self.GA[i] and not self.DR[i] and self.HOEP_END_TIME > max(self.GA_END_TIME, self.DR_END_TIME) and self.soc[i - 1] > 0.001:
                self.p_discharge[i] = \
                    self.calculate_p_discharge(self.HOEP, self.soc[max(self.GA_END_TIME, self.DR_END_TIME) - 1], self.HOEP[~((self.GA == 1) | (self.DR == 1))].sum())[i]

            if i in range(self.CHARGING_START_TIME - 1, self.CHARGING_END_TIME) and self.soc[i - 1] < self.SOC_max:
                self.p_charge[i] = min(self.p_max, self.SOC_max - self.soc[i - 1])

            self.soc[i] = self.soc[i - 1] - self.p_discharge[i] + self.p_charge[i]

    def calculate_extra_load(self, activation_times, p_max_soc):
        active_low_load = self.Load[(self.Load < min(self.p_max, p_max_soc)) & (activation_times == 1)]
        extra_load = (min(self.p_max, p_max_soc) - active_low_load).sum()
        low_load_number = active_low_load.size  # Times of low_load that we choose Load[i] as discharged amount
        return extra_load, low_load_number

    def calculate_p_discharge(self, activation_times, state_of_charge, activation_period):
        p_max_soc = state_of_charge / activation_period
        extra_load, low_load_number = self.calculate_extra_load(activation_times, p_max_soc)
        temp_1 = self.Load * activation_times
        temp_2 = self.Load * activation_times
        temp_3 = self.Load * activation_times

        temp_1[temp_1 >= min(self.p_max, p_max_soc)] = 0

        if activation_period == low_load_number:
            temp_2[self.p_max > temp_2] = 0
            temp_3[self.p_max <= temp_3] = 0
            temp_3[temp_3 < min(self.p_max, p_max_soc)] = 0
            temp_2 = np.minimum((self.p_max * activation_times), temp_2)

        else:
            temp_2[min(self.p_max, (p_max_soc + extra_load / (activation_period - low_load_number))) > temp_2] = 0
            temp_3[min(self.p_max, (p_max_soc + extra_load / (activation_period - low_load_number))) <= temp_3] = 0
            temp_3[temp_3 < min(self.p_max, p_max_soc)] = 0
            extra_loadn = (p_max_soc + extra_load / (activation_period - low_load_number) - temp_3[temp_3 > 0]).sum()
            low_load_numbern = temp_3[temp_3 > 0].size

            if activation_period == (low_load_number + low_load_numbern):
                temp_2 = np.minimum(self.p_max * activation_times, temp_2)
            else:
                temp_2 = np.minimum(min(self.p_max, p_max_soc + (extra_load / (activation_period - low_load_number)) + extra_loadn / (
                        activation_period - low_load_number - low_load_numbern)) * activation_times, temp_2)

        return np.maximum.reduce([temp_1, temp_2, temp_3])
