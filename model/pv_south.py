import math
from model.PV import PV

class PV_South(PV):
    def __init__(self, P_max, irradiance, sundata, day, current_time):
        super().__init__(P_max, irradiance, sundata, day)
        self.t = current_time

    def calculate(self):
        time_diff_seconds = (self.t - self.t_mid).total_seconds()
        time_diff_hours = time_diff_seconds / 3600.0

        # Parametry funkcji
        sigma_hours = self.sigma / 3600.0  # szerokość rozkładu
        super_gauss_power = 2.8 #parametr odpowiadajacy za "grubosc" krzywej na srodku

        if not (self.sunrise <= self.t <= self.sunset):
            return 0.0

        result = self.P_max * self.max_irradiance * math.exp(
            - (abs(time_diff_hours) ** super_gauss_power) / (2 * sigma_hours ** super_gauss_power)
        )
        return result