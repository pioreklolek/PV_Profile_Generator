from datetime import datetime
import pandas as pd
from pandas import Timestamp

class Irradiance:
    def __init__(self):
        path = "data/avg10years_hour_Gi.csv"
        self.data = None
        self.path = path
        self.daily_max = {}

    def load(self):
        try:
            self.data = pd.read_csv(self.path, skiprows=8)
            print(f"Loaded columns in Irradiance: {self.data.columns}")
            print(f"First few rows in Irradiance:\n{self.data.head()}")
            self.data['time'] = pd.to_datetime(self.data['time'], format='%Y%m%d:%H%M')
            self.data.set_index('time', inplace=True)
        except FileNotFoundError:
            print("Irradiance CSV file not found.")
        except KeyError as e:
            print(f"Missing column in Irradiance CSV: {e}")
        except ValueError as e:
            print(f"Error parsing datetime: {e}")



    def get_irradance_at(self,timestamp: Timestamp):
        try:
            return self.data.loc[timestamp]['G(i)']
        except KeyError:
            return 0.0

    def get_max_day_irradance(self, day: datetime):
        try:
            if hasattr(day, 'date'):
                target_date = day.date()
            else:
                target_date = pd.to_datetime(day).date()

            cache_key = target_date.strftime('%m-%d')
            if cache_key in self.daily_max:
                return self.daily_max[cache_key]

            try:
                equivalent_2023_date = target_date.replace(year=2023)
            except ValueError:
                if target_date.month == 2 and target_date.day == 29:
                    equivalent_2023_date = target_date.replace(year=2023, day=28)
                else:
                    raise

            date_str = equivalent_2023_date.strftime('%Y-%m-%d')
            day_data = self.data[self.data.index.strftime('%Y-%m-%d') == date_str]

            if not day_data.empty:
                max_irradiance = day_data['G(i)'].max()
                self.daily_max[cache_key] = max_irradiance
                return max_irradiance
            else:
                print(f"Nie znaleziono max irradiance dla dnia {date_str}")
                self.   daily_max[cache_key] = 0.0
                return 0.0

        except Exception as e:
            print(f"Błąd przy szukaniu max irradiance dla dnia {day}: {e}")
            return 0.0
