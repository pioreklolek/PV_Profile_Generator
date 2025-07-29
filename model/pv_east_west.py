import math
from datetime import timedelta

from model.PV import PV


class PV_east_west(PV):
    def __init__(self, P_max, irradiance, sundata, day, current_time, slope):
        super().__init__(P_max, irradiance, sundata, day)
        self.t = current_time
        self.slope = slope #kat naychelnia zakres od 0 do 35 stopni

        day_length = (self.sunset - self.sunrise).total_seconds() / 3600.0

        #przesuniecie od poludnia do peak , maxx 30%, nie wiecej niz 3h
        offset_hours = min(day_length * 0.3, 3)

        #poludnie = srodek dnia
        self.t_noon = self.sunrise + timedelta(hours=day_length / 2)
        #ustawienie pekow
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

    #odwrocony gaussa , najmniej w poludnie najwiecej po bookach, slope 0stopni = okolo 12% max  wartosci w poludnie , slope 35stopni= 85% max wartosci w poludnie
    def calculate_midday_factor(self):
        time_diff_hours = (self.t - self.t_noon).total_seconds() / 3600.0

        # 1/2 odleglosci miedze peakami
        sigma_hours = (self.t_west_peak - self.t_east_peak).total_seconds() / 3600.0 / 2.0

        # inverted gauss - 1 w południe, 0 po bokach
        base = math.exp(- (time_diff_hours ** 2) / (2 * sigma_hours ** 2))

        # moc poludnia od slope
        midday_factor = 0.12 + (0.85 - 0.12) * (self.slope / 35.0)

        return base * midday_factor

    def calculate(self):
        peak_power = self.P_max / 2 * self.max_irradiance
        east = self.calculate_east()
        west = self.calculate_west()
        midday = self.calculate_midday_factor()

        return peak_power * (east + west + midday)