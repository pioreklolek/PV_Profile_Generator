import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import plotly.graph_objects as go

class GraphGenerator:
    def __init__(self,p_max_south,p_max_ew):
        self.p_max_south = p_max_south
        self.p_max_ew = p_max_ew
        self.input_path = "output/profile_records.csv"
        self.input_path_maxkW = "output/stats/daily_stats.csv"
        self.output_path = "output/wykresy/graph.png"
        self.output_path_daily_maxKw_png = ("output/wykresy/graph_daily_maxKw.png")
        self.output_path_svg = "output/wykresy/graph.svg"

    # wykres w png
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

    # wykres w png dla dziennego max kW , tylko dla typu south
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

    #daily max kW w svg, tylko dla typu south
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


    # wykres w plotly co 15 min roczny dla obu typow
    def generate_15_min_graph_plotly(self):
        df = pd.read_csv(self.input_path)

        df['datetime'] = pd.to_datetime(df['datetime']) #konwersja bo sie bugowalo

        required_cols = ['datetime']
        if self.p_max_south > 0:
            df['P_south'] = df['P_south'] / 1000 # kW
            required_cols.append('P_south')
        if self.p_max_ew > 0:
            df['P_ew'] = df['P_ew'] / 1000
            required_cols.append('P_ew')

        #debug
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Brakuje wymaganej kolumny: {col}")

        fig = go.Figure()

        if self.p_max_south > 0:
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df['P_south'],
                mode='lines',
                name='Południe',
                line=dict(color='red', width=1),
                opacity=0.8,
                hovertemplate = '%{x}<br><b>%{y:.3f} kW</b><extra></extra>' #hover kursora
            ))

        if self.p_max_ew > 0:
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df['P_ew'],
                mode='lines',
                name='Wschód-Zachód',
                line=dict(color='blue', width=1),
                opacity=0.8,
                hovertemplate='%{x}<br><b>%{y:.3f} kW</b><extra></extra>' #hover kursora
            ))

        fig.update_layout(
            title='Roczna chwilowa produkcja prądu [kW]',
            xaxis_title='Data i godzina',
            yaxis_title='Chwilowa produkcja [kW]',
            xaxis=dict(
                type="date",
                showgrid=True,
                gridcolor='grey',
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,label="1d",step="day",stepmode="backward"),  #klawisze zoom
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(step="all", label="Rok")
                    ]),
                    x=0.5,
                    y=-0.5,
                    xanchor="center",
                    yanchor="top"
                ),
                tickformatstops=[
                    dict(dtickrange=[None, 1000 * 60 * 60 * 24 * 3], value="%d %b %H:%M"),  #data przy przyblizaniu
                    dict(dtickrange=[1000 * 60 * 60 * 24 * 3, 1000 * 60 * 60 * 24 * 31], value="%d %b"),
                    dict(dtickrange=[1000 * 60 * 60 * 24 * 31, None], value="%b"),
                ],
            ),
            yaxis=dict(
                showgrid=True, gridcolor='grey'
            ),
            template='plotly_white',
            legend=dict(x=-0.1, y=0.99, bordercolor="black", borderwidth=1),
            height=600,
            margin=dict(l=60, r=20, t=60, b=60)
        )

        annotations = [] # opis inputow
        annotations.append(dict(
            xref="paper", yref="paper",
            x=0.5, y=1.15,
            text="Input:",
            showarrow=False,
            font=dict(size=14, color="black")
        ))
        if self.p_max_south > 0:
            annotations.append(dict(
                xref="paper", yref="paper",
                x=0.5, y=1.1,
                text=f"P_south: {self.p_max_south:.3f} kWp",
                showarrow=False,
                font=dict(size=14, color="red")
            ))

        if self.p_max_ew > 0:
            annotations.append(dict(
                xref="paper", yref="paper",
                x=0.5, y=1.05,
                text=f"P_ew: {self.p_max_ew:.3f} kWp",
                showarrow=False,
                font=dict(size=14, color="blue")
            ))
        fig.update_layout(annotations=annotations)


        #fig.show()
        output_html = "output/wykresy/wykres.html"
        fig.write_html(output_html)



