import math
from model.PV import PV


class PV_South(PV):
    def __init__(self, P_max, irradiance, sundata, day, current_time):
        super().__init__(P_max, irradiance, sundata, day)
        self.t = current_time

    def calculate(self):
        time_diff_seconds = (self.t - self.t_mid).total_seconds()
        time_diff_hours = time_diff_seconds / 3600.0
        sigma_hours = self.sigma / 3600.0

        # Skala rozciągania: im większe, tym bardziej „ściśnięty” środek, łagodny początek i koniec
        shaping_factor = 0.05

        scaled_time = time_diff_hours * (1 + shaping_factor * abs(time_diff_hours))

        return self.P_max * self.max_irradiance * math.exp(
            -((scaled_time) ** 2) / (2 * sigma_hours ** 2)
        )
