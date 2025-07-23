from engine.simulator import PvSimulator

def main():
    simulator = PvSimulator()


    simulator.sundata.load_data()
    simulator.irradiance.load()

    profile = simulator.generate_profile(p_max_south=4.08, p_max_ew=4.08)
    simulator.generate_test_daily_kWh()

    print("Profile generated and saved to 'output/profile_records.csv'.")

if __name__ == "__main__":
    main()