from engine.simulator import PvSimulator

def main():
    simulator = PvSimulator()


    simulator.sundata.load_data()
    simulator.irradiance.load()

    profile = simulator.generate_profile(p_max_south=10, p_max_ew=10)

    print("Profile generated and saved to 'output/profile.csv'.")

if __name__ == "__main__":
    main()