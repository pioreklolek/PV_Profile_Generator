import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


class GraphGenerator:
    def __init__(self,p_max_south,p_max_ew):
        self.p_max_south = p_max_south
        self.p_max_ew = p_max_ew
        self.input_path = "output/profile_records.csv"
        self.input_path_maxkW = "output/stats/daily_stats.csv"
        self.output_path = "output/graph.png"
        self.output_path_daily_maxKw_png = ("output/graph_daily_maxKw.png")
        self.output_path_svg = "output/graphy/graph.svg"
    def generate_graph(self):
        df = pd.read_csv(self.input_path,parse_dates=['datetime'])

        plt.figure(figsize=(18,6))
        plt.title("Profil PV")
        plt.xlabel("Data i godzina", fontsize=12)
        plt.ylabel("Moc chwilowa kW",fontsize=12)

        if self.p_max_south > 0 and 'P_south' in df:
            plt.plot(df['datetime'],df['P_south'],label="S",linewidth=0.7,alpha=0.7)

        if self.p_max_ew > 0 and 'P_ew' in df:
            plt.plot(df['datetime'], df['P_ew'], label="E-W", linewidth=0.7, alpha=0.7)

        plt.legend()
        plt.grid(True,linestyle="--",alpha=0.5)

        locator = mdates.MonthLocator()
        formatter = mdates.DateFormatter('%b')
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.tight_layout

        plt.savefig(self.output_path,dpi=150)
        plt.close()

    def generate_graph_daily_maxkW_png(self):
        df = pd.read_csv(self.input_path_maxkW,parse_dates=['date'])

        requred_cols = ['date','max_kW_south']

        for col in requred_cols:
            if col not in df.columns:
                raise ValueError(f"Brakuje wymaganej kolumny: {col}")

        fig = plt.figure(figsize=(100,6.66),dpi=300)
        plt.title("Maksymalna moca chwilowa dzienna ",fontsize=16)
        plt.xlabel("Data",fontsize=4)
        plt.ylabel("Maksymalna moc chwilowa [kW]",fontsize=12)

        plt.plot(df['date'],df['max_kW_south'],label="Max kW (South)",color="orange",linewidth=1.2)

        locator = mdates.DayLocator(interval=7)
        formatter = mdates.DateFormatter('%d-%b')
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)

        plt.gca().xaxis.set_minor_locator(mdates.DayLocator())
        plt.grid(True,which='minor',linestyle='--',linewidth=0.3,alpha=0.5)
        plt.grid(True,which='major' ,linestyle='--',alpha=0.4)
        plt.legend(fontsize=10)
        plt.tight_layout()

        plt.savefig(self.output_path_daily_maxKw_png,dpi=300)
        plt.close()

    def generate_graph_daily_maxKw_svg(self):
        df = pd.read_csv(self.input_path_maxkW, parse_dates=['date'])

        requred_cols = ['date', 'max_kW_south']

        for col in requred_cols:
            if col not in df.columns:
                raise ValueError(f"Brakuje wymaganej kolumny: {col}")


        plt.figure(figsize=(230,6))
        plt.title("Maksymalna moc chwilowa dzienna",fontsize=16)
        plt.xlabel("Data",fontsize=4)
        plt.ylabel("Maksymalna moc chwilowa [kW]",fontsize=12)

        plt.plot(df['date'],df['max_kW_south'],label="Max kW",color="orange",linewidth=1.2)

        locator = mdates.DayLocator()
        formatter = mdates.DateFormatter('%d-%b')
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)

        plt.gca().xaxis.set_minor_locator(mdates.DayLocator())
        plt.grid(True, which='minor', linestyle='--', linewidth=0.3, alpha=0.5)
        plt.grid(True, which='major', linestyle='--', alpha=0.4)

        plt.legend(fontsize=10)
        plt.tight_layout()

        plt.savefig(self.output_path_svg, dpi=300)
        plt.close()

