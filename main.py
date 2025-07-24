from engine.graph_generator import GraphGenerator
from engine.simulator import PvSimulator

def main():
    simulator = PvSimulator()
    simulator.sundata.load_data()
    simulator.irradiance.load()

    p_max_south = 4
    p_max_ew = 1

    graph = GraphGenerator(p_max_south,p_max_ew)


    simulator.generate_profile(p_max_south, p_max_ew)
    simulator.generate_daily_kWh()
    simulator.generate_stats()
    print("Wygenerowano rekordy profilu i zapisano do 'output/profile_records.csv'.")

    graph.generate_graph()
    print(f"Wygenerowano wykres profilu i zapisano do 'output/graph.png'. ")

    graph.generate_graph_daily_maxkW_png()
    print("Wygenerowano wykres do png!!")

    graph.generate_graph_daily_maxKw_svg()
    print("Wygenerowano wykres do svg!!")

if __name__ == "__main__":
    main()