import math
from datetime import timedelta

from model.PV import PV


class PV_east_west(PV):
    def __init__(self, P_max, irradiance, sundata, day, current_time, slope=0):
        super().__init__(P_max, irradiance, sundata, day)
        self.t = current_time
        self.slope = slope # kąt podawany w stopnieach zakres od 0 do 35

        self.t_east_peak = self.sunrise + timedelta(hours=2)
        self.t_west_peak = self.sunset - timedelta(hours=2)

        # poludnie srodek miedzy peak
        self.t_noon = self.t_east_peak + (self.t_west_peak - self.t_east_peak) / 2

    def calculate_east(self):
        time_diff_hours = (self.t - self.t_east_peak).total_seconds() / 3600.0
        sigma_hours = self.sigma / 3600.0
        return math.exp(- (time_diff_hours ** 2) / (2 * sigma_hours ** 2))

    def calculate_west(self):
        time_diff_hours = (self.t - self.t_west_peak).total_seconds() / 3600.0
        sigma_hours = self.sigma / 3600.0
        return math.exp(- (time_diff_hours ** 2) / (2 * sigma_hours ** 2))

        #odwrocony gaussa , najmniej w poludnie najwiecej pobookach , slope 0stopni = okolo 12% max  wartosci w poludnie , slope 35stopni= 85% max wartosci w poludnie
    def calculate_midday_factor(self):

        time_diff_hours = (self.t - self.t_noon).total_seconds() / 3600.0
        #odworocony gauss
        sigma_hours = (self.t_west_peak - self.t_east_peak).total_seconds() / 3600.0 / 2.0
        inverted_gauss = 1 - math.exp(- (time_diff_hours ** 2) / (2 * sigma_hours ** 2))

        #interpolacja miedzy 0 a 35, gladkie przejscie
        min_midday_ratio = 0.12
        max_midday_ratio = 0.85
        slope_clamped = max(0, min(self.slope, 35))
        midday_ratio = min_midday_ratio + (max_midday_ratio - min_midday_ratio) * (slope_clamped / 35.0)

        return midday_ratio * (1 - inverted_gauss)

    def calculate(self):
        peak_power = self.P_max / 2 * self.max_irradiance
        east = self.calculate_east()
        west = self.calculate_west()
        midday = self.calculate_midday_factor()

        return peak_power * (east + west + midday)