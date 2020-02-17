import pysat
from pysatMissions import plot as mplt


class TestPlot():

    def setup(self):
        """Runs before every method to create a clean testing setup."""

        from pysatMissions.instruments import pysat_ephem
        self.testInst = pysat.Instrument(inst_module=pysat_ephem, tag='all',
                                         sat_id='100')
        self.testInst.load(date=pysat.datetime(2018, 1, 1))

    def teardown(self):
        """Clean up test environment after tests"""

        del self.testInst

    def test_plot_simulated_data(self):
        """Try running the plot to see if warning or errors are generated"""

        mplt.plot_simulated_data(self.testInst)

        assert True
