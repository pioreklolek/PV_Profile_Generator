import math
from datetime import timedelta

from model.PV import PV


class PV_east_west(PV):
    def __init__(self, P_max, irradiance, sundata, day, current_time, slope):
        super().__init__(P_max, irradiance, sundata, day)
        self.t = current_time
        self.slope = slope  # slope: 0 lub 35 stopni

        day_length = (self.sunset - self.sunrise).total_seconds() / 3600.0

        # Przesunięcie od południa do peak, max 40%, nie więcej niż 4h
        offset_hours = min(day_length * 0.35, 3.5)

        # Południe = środek dnia
        self.t_noon = self.sunrise + timedelta(hours=day_length / 2)
        # Ustawienie peaków
        self.t_east_peak = self.t_noon - timedelta(hours=offset_hours)
        self.t_west_peak = self.t_noon + timedelta(hours=offset_hours)

        # sigma = 1/3 odległości między east a noon
        distance_east = (self.t_noon - self.t_east_peak).total_seconds() / 3600.0
        self.sigma = distance_east / 3.0 * 3600.0

    def calculate_east(self):
        time_diff_hours = (self.t - self.t_east_peak).total_seconds() / 3600.0
        sigma_hours = self.sigma / 3600.0
        return math.exp(- (time_diff_hours ** 2) / (2 * sigma_hours ** 2))

    def calculate_west(self):
        time_diff_hours = (self.t - self.t_west_peak).total_seconds() / 3600.0
        sigma_hours = self.sigma / 3600.0
        return math.exp(- (time_diff_hours ** 2) / (2 * sigma_hours ** 2))


    def calculate_mid_curve(self):
        if self.slope == 0:
            time_diff_hours = (self.t - self.t_noon).total_seconds() / 3600.0
            sigma_hours = (self.t_west_peak - self.t_east_peak).total_seconds() / 3600.0 / 2.0
            base = math.exp(- (time_diff_hours ** 2) / (2 * sigma_hours ** 2))
            midday_factor = 0.12 + (0.85 - 0.12) * (self.slope / 35.0)
            return base * midday_factor

        elif self.slope == 35:
            t_total = (self.t_west_peak - self.t_east_peak).total_seconds()
            if t_total == 0:
                return 0
            t_cur = (self.t - self.t_east_peak).total_seconds()
            x = t_cur / t_total
            if x < 0 or x > 1:
                return 0
            a = -2.45  #parametry wplywywa na wyladzeine polaczenia peaku z srodkiem wykresu  , podstawowo: -2.8
            b = 1.6  # wspolczynnik pomnozenia peaku srodku wykresu do peaku east-west podstaowo  1.7 , czyli peak srodka ma 170% wartosci peak eastwest
            return a * (x - 0.5) ** 2 + b
        else:
            print(f"Niewłaściwa wartość slope: {self.slope}")


    def calculate(self):
        peak_power = self.P_max / 2 * self.max_irradiance
        east = self.calculate_east()
        west = self.calculate_west()
        if self.slope == 0:
            midday = self.calculate_mid_curve()
            return peak_power * (east + west + midday)
        elif self.slope == 35:
            mid_curve = self.calculate_mid_curve()
            if self.t < self.t_east_peak:
                return peak_power * east
            elif self.t > self.t_west_peak:
                return peak_power * west
            else:
                return peak_power * mid_curve