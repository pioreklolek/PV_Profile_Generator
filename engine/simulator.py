import os
from datetime import timedelta, datetime
import pandas as pd
from model.irradiance import Irradiance
from model.pv_east_west import PV_east_west
from model.pv_south import PV_South
from model.sun_data import SunData


class PvSimulator:
    def __init__(self):
        self.sundata = SunData()
        self.irradiance = Irradiance()

    #generuje profil PV w csv
    def generate_profile(self, p_max_south, p_max_ew,slope_ew, progress_barr_callback=None) -> pd.DataFrame:
        self.sundata.load_data()
        self.irradiance.load_max_daily_irradance()
        sunset_cache = {}
        sunrise_cache = {}

        self.slope_ew = slope_ew

        os.makedirs('output', exist_ok=True)

        interval = timedelta(minutes=15)
        start = datetime(2025, 1, 1, 0, 0)
        end = datetime(2025, 12, 31, 23, 45)
        timestamps = pd.date_range(start=start, end=end, freq=interval)[:-1]

        records = []
        processed_count = 0

        print(f"Processing {len(timestamps)} timestamps...")

        for i, ts in enumerate(timestamps):
            if progress_barr_callback and i % 1000 == 0:
                percent = int(i / len(timestamps) * 100)
                progress_barr_callback(percent)

            day_timestamp = pd.Timestamp(ts.date())

            if i % 1000 == 0:
                print(f"Progress: {i}/{len(timestamps)} ({i / len(timestamps) * 100:.1f}%)")

            if day_timestamp not in sunrise_cache:
                sunrise = self.sundata.getSunrise(ts)
                sunset = self.sundata.getSunset(ts)
                sunrise_cache[day_timestamp] = sunrise
                sunset_cache[day_timestamp] = sunset

                if sunrise is None or sunset is None:
                    continue

            current_time = ts.time()

            if current_time < sunrise or current_time > sunset:
                records.append({
                    'datetime': ts,
                    'P_south': 0.0,
                    'P_ew': 0.0
                })
                continue

            try:
                power_south = PV_South(p_max_south, self.irradiance, self.sundata, day_timestamp,ts)
                power_ew = PV_east_west(p_max_ew, self.irradiance, self.sundata, day_timestamp, ts,self.slope_ew)

                p_south_value = power_south.calculate()
                p_ew_value = power_ew.calculate()

                records.append({
                    'datetime': ts,
                    'P_south': round(p_south_value, 4),
                    'P_ew': round(p_ew_value, 4)
                })

                processed_count += 1

                if processed_count <= 10 and (p_south_value > 0 or p_ew_value > 0):
                    print(f"Daylight {ts}: P_south={p_south_value:.3f}, P_ew={p_ew_value:.3f}")

            except Exception as e:
                print(f"Error processing timestamp {ts}: {e}")
                records.append({
                    'datetime': ts,
                    'P_south': 0.0,
                    'P_ew': 0.0
                })
                continue

        df = pd.DataFrame(records)
        print(f"Generated profile with {len(df)} records")
        df.to_csv('output/profile_records.csv', index=False, float_format='%.4f')
        return df

    #generuje csv z łącznym dziennym kWh
    def generate_daily_kWh(self):
        input_file = "output/profile_records.csv"
        output_file = "output/stats/daily_kWh.csv"

        df = pd.read_csv(input_file, parse_dates=['datetime'])

        df['date'] = df['datetime'].dt.date

        df['E_south'] = df['P_south'] * 0.25
        df['E_ew'] = df['P_ew'] * 0.25

        daily_energy = df.groupby('date').agg({
            'E_south' : 'sum',
            "E_ew" : 'sum'
        }).reset_index()


        daily_energy['E_south'] = daily_energy['E_south'] / 1000  # konwersja na kilo
        daily_energy['E_ew'] = daily_energy['E_ew'] / 1000


        daily_energy['E_south'] = daily_energy['E_south'].round(4)
        daily_energy['E_ew'] = daily_energy['E_ew'].round(4)

        total_row = pd.DataFrame([{
            'date' : 'TOTAL',
            'E_south' : daily_energy['E_south'].sum().round(4),
            'E_ew' : daily_energy['E_ew'].sum().round(4)
        }])
        result = pd.concat([daily_energy,total_row],ignore_index=True)

        result.to_csv(output_file,index=False,float_format='%.4f')

        print(f"Wygenerowano dzienne kWh, {len(df)} ilość")

        #generuje csv z różnymi statystykami
    def generate_stats(self):
        input_daily_kWh = "output/stats/daily_kWh.csv"
        input_profile = "output/profile_records.csv"

        output_daily_stats = "output/stats/daily_stats.csv"
        output_monthly_stats = "output/stats/monthly_stats.csv"

        #miesieczne kwH
        df_kWh = pd.read_csv(input_daily_kWh, parse_dates=['date'])
        df_kWh['month'] = df_kWh['date'].dt.to_period('M')

        monthly_kWh_stats = df_kWh.groupby('month').agg({
            'E_south': ['mean', 'max']
        }).reset_index()

        monthly_kWh_stats.columns = ['month', 'avg_kWh_south', 'max_kWh_south']

        # miesieczne srednie kw
        df_kW = pd.read_csv(input_profile, parse_dates=['datetime'])
        df_kW['month'] = df_kW['datetime'].dt.to_period('M')
        df_kW['date'] = df_kW['datetime'].dt.floor('D')

        monthly_kW_stats = df_kW.groupby('month').agg({
            'P_south': ['mean', 'max']
        }).reset_index()

        monthly_kW_stats.columns = ['month', 'avg_kW_south', 'max_kW_south']

        #miesieczne statystyki
        monthly_stats = pd.merge(monthly_kWh_stats, monthly_kW_stats, on='month')
        monthly_stats['month'] = monthly_stats['month'].astype(str)
        monthly_stats.to_csv(output_monthly_stats, index=False)
        print(f"Zapisano statystyki miesięczne!")

        #dzienne max kw
        daily_kW_stats = df_kW.groupby(['date']).agg(
            avg_kW_south=('P_south', 'mean'),
            max_kW_south=('P_south', 'max')
        ).reset_index()

        #max godzina
        max_times = df_kW.loc[df_kW.groupby('date')['P_south'].idxmax(), ['date', 'datetime']]
        max_times = max_times.rename(columns={'datetime': 'max_kW_time_south'})

        daily_kW_stats = pd.merge(daily_kW_stats, max_times, on='date')

        cols_to_round = ['avg_kWh_south', 'max_kWh_south', 'avg_kW_south', 'max_kW_south']
        monthly_stats[cols_to_round] = monthly_stats[cols_to_round].round(4)
        daily_kW_stats[['avg_kW_south', 'max_kW_south']] = daily_kW_stats[['avg_kW_south', 'max_kW_south']].round(4)

        daily_kW_stats.to_csv(output_daily_stats, index=False,float_format='%.4f')
        print("Zapisano statystyki dzienne kW do pliku!")

    def generate_yearly_kWh(self):
        input_file = "output/profile_records.csv"
        output_file = "output/stats/year_kWh.csv"

        df = pd.read_csv(input_file,parse_dates=['datetime'])

        total_kWh_south = (df['P_south'].sum()) * 0.25
        total_kWh_ew = (df['P_ew'].sum()) * 0.25

        total_kWh_south = total_kWh_south / 1000 # na Kilo
        total_kWh_ew = total_kWh_ew / 1000

        total_kWh_south = round(total_kWh_south, 4)
        total_kWh_ew =round(total_kWh_ew, 4)

        summ = pd.DataFrame([{
            'type' : 'TOTAL',
            'E_south' : total_kWh_south,
            'E_ew' : total_kWh_ew
        }])
        summ.to_csv(output_file,index=False,float_format='%.4f')
        print(f"Wygenerowano plik z roczna sumą kWh")