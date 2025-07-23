import math
from datetime import timedelta

from model.PV import PV


class PV_east_west(PV):
    def __init__(self, P_max, irradiance, sundata,day,current_time):
        super().__init__(P_max, irradiance, sundata,day)
        self.t = current_time
        self.t_east_peak = self.sunrise + timedelta(hours=2)
        self.t_west_peak = self.sunset - timedelta(hours=2)

    def calculate_east(self):
        time_diff_sec = (self.t - self.t_east_peak).total_seconds()
        time_diff_hours = time_diff_sec / 3600.0
        sigma_hours = self.sigma / 3600.0

        return math.exp(- ((time_diff_hours) ** 2) / (2 * sigma_hours ** 2))

    def calculate_west(self):
        time_diff_sec = (self.t - self.t_west_peak).total_seconds()
        time_diff_hours = time_diff_sec / 3600.0
        sigma_hours = self.sigma / 3600.0

        return math.exp(- ((time_diff_hours) ** 2) / (2 * sigma_hours ** 2))

    def calculate(self):
        return self.P_max / 2 * self.max_irradiance * (self.calculate_east() + self.calculate_west())