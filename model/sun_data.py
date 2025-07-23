import pandas as pd
class SunData:
    def __init__(self):
        self.path = "data/sunset_sunrise_2025.csv"
        self.data = None

    def load_data(self):
        try:
            self.data = pd.read_csv(self.path)
            print(f"Loaded columns in SunData: {self.data.columns}")
            print(f"First few rows in SunData:\n{self.data.head()}")
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data['sunrise'] = pd.to_datetime(self.data['sunrise'], format='%H:%M:%S').dt.time
            self.data['sunset'] = pd.to_datetime(self.data['sunset'], format='%H:%M:%S').dt.time
            print(f"Załadowano {len(self.data)} dni danych ")
        except FileNotFoundError:
            print(f"Nie znaleziono pliku csv sunset_sunrise")
        except KeyError as e:
            print(f"Missing column in SunData CSV: {e}")
        except ValueError as e:
            print(f"Error parsing datetime: {e}")

    def getSunrise(self,day):
        if hasattr(day,'date'):
            day_date = day.date()
        else:
            day_date = pd.to_datetime(day).date()

        matching_rows = self.data[self.data['date'].dt.date == day_date]

        if matching_rows.empty:
            print(f"Nie znaleziono danych o wschodzie słońca dla {day_date}")
            return None

        return matching_rows['sunrise'].iloc[0]

    def getSunset(self,day):
        if hasattr(day, 'date'):
            day_date = day.date()
        else:
            day_date = pd.to_datetime(day).date()

        matching_rows = self.data[self.data['date'].dt.date == day_date]

        if matching_rows.empty:
            print(f"No sunset data found for date: {day_date}")
            return None

        return matching_rows['sunset'].iloc[0]