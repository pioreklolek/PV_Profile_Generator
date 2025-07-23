import unittest
from engine.simulator import PvSimulator


class TestPVSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = PvSimulator()

        self.simulator.sundata.load_data()
        self.simulator.irradiance.load()

    def test_generate_profile(self):
        df = self.simulator.generate_profile(p_max_south=0, p_max_ew=0)

        self.assertFalse(df.empty)

        self.assertListEqual(list(df.columns), ['datetime', 'P_south', 'P_ew'])

        print(df.head())


if __name__ == '__main__':
    unittest.main()