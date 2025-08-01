from datetime import datetime, timedelta
from pandas import Timestamp


class PV:
    def __init__(self, P_max, irradiance, sundata, day: Timestamp):
        self.P_max = P_max
        self.sundata = sundata
        self.irradiance = irradiance
        self.data = None

        self.sunrise = datetime.combine(day, self.sundata.getSunrise(day))
        self.sunset = datetime.combine(day, self.sundata.getSunset(day))

        self.t_mid = self.sunrise + (self.sunset - self.sunrise) / 2 #środek dnia

        self.day_length = (self.sunset - self.sunrise).total_seconds()

        self.max_irradiance = self.irradiance.get_max_daily_irradance(day)
        self.sigma = self.day_length / 6 # parametr wykresu gaussa