import os.path
from datetime import datetime
import pandas as pd
from pandas import Timestamp
import csv

class Irradiance:
    def __init__(self):
        self.data = None
        self.path = "data/avg10years_hour_Gi.csv"
        self.daily_max = {}
        self.outputpath = "data/max_daily_10avg_irradiance.csv"


    #wczytuje dane z pliku z rekordami co godzine
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

    #oblicza max irradance dla danego dnia z 24 dziennych rekorodow, zwraca ja , i zapisuje do pliku
    def count_max_day_irradance(self, day: datetime):
        try:
            if hasattr(day, 'date'):
                target_date = day.date()
            else:
                target_date = pd.to_datetime(day).date()

            cache_key = target_date.strftime('%m-%d')
            if cache_key in self.daily_max:
                return self.daily_max[cache_key]

            #zastepujemy na rok 2023
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

                self.append_irradance_to_file(target_date,max_irradiance)
                return max_irradiance
            else:
                print(f"Nie znaleziono max irradiance dla dnia {date_str}")
                self.   daily_max[cache_key] = 0.0
                return 0.0

        except Exception as e:
            print(f"Błąd przy szukaniu max irradiance dla dnia {day}: {e}")
            return 0.0


    #zaladowuje dane z pliku z juz oblczonymi max irradance
    def load_max_daily_irradance(self):
        if not os.path.exists(self.outputpath):
            print(f"Plik {self.outputpath} nie istnieje brak danych do załadowania!")
            return

        try:
            df = pd.read_csv(self.outputpath,parse_dates=['time'])
            if 'G(i)' not in df.columns:
                print("Brak col G(i)")
                return

            for _, row in df.iterrows():
                timestamp = row['time']
                irradiance = row['G(i)']

                if isinstance(timestamp,str):
                    timestamp = pd.to_datetime(timestamp)

                key = timestamp.strftime('%m-%d')
                if key not in self.daily_max:
                    self.daily_max[key] = irradiance
                else:
                    self.daily_max[key] = max(self.daily_max[key],irradiance)

            print(f"Wczytano {len(self.daily_max)} max irradance z {self.outputpath}")
        except Exception as e:
            print(f"Błąd podczas wczytaywania plik z max irradance {e}")

    #zwraca max irradance dla danego dnia  z pliku z obliczonym maxem
    def get_max_daily_irradance(self, day: datetime):

        try:
            if hasattr(day, 'date'):
                target_date = day.date()
            else:
                target_date = pd.to_datetime(day).date()

            try:
                equivalent_2023_date = target_date.replace(year=2023)
            except ValueError:
                if target_date.month == 2 and target_date.day == 29:
                    equivalent_2023_date = target_date.replace(year=2023, day=28)
                else:
                    raise

            key = equivalent_2023_date.strftime('%m-%d')

            if key in self.daily_max:
                return self.daily_max[key]
            else:
                print(f"Brak zapisanej max irradancji dla dnia {key}")
                return 0.0
        except Exception as e:
            print(f"Błąd przy pobieraniu max irradancji: {e}")
            return 0.0

    #zapsisuje irradance do pliku
    def append_irradance_to_file(self, date: datetime.date, irradiance: float):
        file_exists = os.path.exists(self.outputpath)

        existing_dates = set()
        if file_exists:
            try:
                with open(self.outputpath, 'r', newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        existing_dates.add(row['time'])
            except Exception as e:
                print(f"Błąd przy odczycie istniejących dat z pliku: {e}")

        date_str = date.strftime('%Y-%m-%d')
        if date_str in existing_dates:
            return

        try:
            with open(self.outputpath, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['time', 'G(i)'])
                writer.writerow([date_str, irradiance])
        except Exception as e:
            print(f"Błąd przy zapisie do pliku {self.outputpath}: {e}")