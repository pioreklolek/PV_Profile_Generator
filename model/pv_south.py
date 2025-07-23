import math
from model.PV import PV


class PV_South(PV):
    def __init__(self, P_max, irradiance, sundata,day,current_time):
        super().__init__(P_max, irradiance, sundata, day)
        self.t = current_time

    def calculate(self):
        time_diff_secods = (self.t - self.t_mid).total_seconds()
        time_diff_hours = time_diff_secods / 3600.0
        sigma_hours = self.sigma / 3600.0

        return self.P_max * self.max_irradiance * math.exp(-((time_diff_hours) ** 2) / (2 * sigma_hours ** 2))