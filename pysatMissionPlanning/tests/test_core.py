import pysatMissionPlanning
import pysat


class TestBasic():
    """Test basic functionality
    """

    def setup(self):
        self.module = pysatMissionPlanning.instruments.pysat_sgp4

    def teardown(self):
        del self.module

    def test_module_loading(self):
        """Check if instrument module can be loaded as a pysat instrument"""

        testInst = pysat.Instrument(inst_module=self.module)

        assert isinstance(testInst, pysat._instrument.Instrument)

    def test_data_loading(self):
        """Check if instrument module can be loaded as a pysat instrument"""

        testInst = pysat.Instrument(inst_module=self.module)
        testInst.load(pysat.datetime(2018, 1, 1))

        assert True
