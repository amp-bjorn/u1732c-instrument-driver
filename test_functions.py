# remember to install the module before running this example.
# alternatively, move this file inside src and change the import to -> from u1732c import U1732C
from U1732C import U1732C
import logging

logger = logging.getLogger(__name__)


# Example usage:
def cycle_settings(lcr: U1732C):
    logging.info("CYCLING INSTRUMENT THROUGH DIFFERENT SETTINGS")
    print(lcr.read_identity())

    # cycle through the different modes
    lcr.set_mode("SER")
    lcr.set_mode("PAL")

    # cycle through the different factors
    lcr.set_factor("D")
    lcr.set_factor("Q")
    lcr.set_factor("TH")

    # cycle through the different frequencies
    lcr.set_frequency("100")
    lcr.set_frequency("120")
    lcr.set_frequency("1k")
    lcr.set_frequency("10k")

    # cycle through the different functions, and for each function cycle through the different ranges
    for function in lcr.functions:
        lcr.set_function(function)
        for range in lcr.ranges[function]:
            lcr.set_range(range)


def sample_readings(lcr: U1732C):
    logging.info("TAKING SAMPLE READINGS")
    lcr.set_mode("SER")
    lcr.set_factor("D")
    lcr.set_frequency("1k")
    lcr.set_function("L")
    lcr.set_range("200m")
    print(lcr.get_measurement())
    print(lcr.get_all_measurements())
    print(lcr.check_errors())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # create and open the lcr object
    lcr = U1732C(port="COM7")

    # place debugger here to inspect the lcr object and its attributes step by step as the different commands do not return any value,
    # but instead just set the state of the instrument, so we can inspect the state of the lcr object to confirm that the commands are working as expected
    cycle_settings(lcr)
    sample_readings(lcr)
    lcr.check_errors()

    # close the connection to the instrument
    lcr.close()
