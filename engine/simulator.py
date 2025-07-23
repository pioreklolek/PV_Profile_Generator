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

    def generate_profile(self, p_max_south, p_max_ew) -> pd.DataFrame:
        self.sundata.load_data()
        self.irradiance.load()

        os.makedirs('output', exist_ok=True)

        interval = timedelta(minutes=15)
        start = datetime(2025, 1, 1, 0, 0)
        end = datetime(2025, 12, 31, 23, 45)
        timestamps = pd.date_range(start=start, end=end, freq=interval)[:-1]

        records = []
        processed_count = 0

        print(f"Processing {len(timestamps)} timestamps...")

        for i, ts in enumerate(timestamps):
            day_timestamp = pd.Timestamp(ts.date())

            if i % 1000 == 0:
                print(f"Progress: {i}/{len(timestamps)} ({i / len(timestamps) * 100:.1f}%)")

            sunrise = self.sundata.getSunrise(ts)
            sunset = self.sundata.getSunset(ts)

            if sunrise is None or sunset is None:
                continue

            current_time = ts.time()
            sunrise_margin = (datetime.combine(ts.date(), sunrise) - timedelta(hours=1)).time()
            sunset_margin = (datetime.combine(ts.date(), sunset) + timedelta(hours=1)).time()

            if current_time < sunrise_margin or current_time > sunset_margin:
                records.append({
                    'datetime': ts,
                    'P_south': 0.0,
                    'P_ew': 0.0
                })
                continue

            try:
                power_south = PV_South(p_max_south, self.irradiance, self.sundata, day_timestamp, ts)
                power_ew = PV_east_west(p_max_ew, self.irradiance, self.sundata, day_timestamp, ts)

                p_south_value = power_south.calculate()
                p_ew_value = power_ew.calculate()

                records.append({
                    'datetime': ts,
                    'P_south': p_south_value,
                    'P_ew': p_ew_value
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
        df.to_csv('output/profile.csv', index=False)
        return df