from xml.parsers.expat import errors
from serial import Serial
import logging

logger = logging.getLogger(__name__)


class U1732C:
    def __init__(self, port: str, baudrate: int = 9600):
        self.serial = Serial(port, baudrate, timeout=5)
        self.modes: dict[str, str] = {
            "SER": "Series",
            "PAL": "Parallel",
        }
        self.factors: dict[str, str] = {
            "D": "Dissipation Factor",
            "Q": "Quality Factor",
            "TH": "Phase Angle",
        }
        self.frequencies: dict[str, str] = {
            "100": "100Hz",
            "120": "120Hz",
            "1k": "1kHz",
            "10k": "10kHz",
        }
        self.functions: dict[str, str] = {
            "R": "Resistance",
            "C": "Capacitance",
            "L": "Inductance",
            "Z": "Impedance",
            "ESR": "Equivalent Series Resistance",
            "AI": "Auto Identification",
        }
        self.ranges: dict[str, list[str]] = {
            "R": ["2", "20", "200", "2k", "20k", "200k", "2M", "20M", "200M"],
            "C": ["2000p", "20n", "200n", "2000n", "20u", "200u", "20m"],
            "L": ["2000u", "20m", "200m", "2", "20", "200", "2k"],
            "Z": ["2", "20", "200", "2k", "20k", "200k", "2M", "20M", "200M"],
            "ESR": [],
            "AI": [],
        }
        self._current_mode: str = ""
        self._current_factor: str = ""
        self._current_frequency: str = ""
        self._current_function: str = ""
        self._current_range: str = ""

    def _command(self, command: str):
        logger.debug(f"SEND COMMAND {command}")
        self.serial.write((f"{command}\n").encode())

    def _response(self) -> str:
        serial_return = self.serial.readline().decode().strip()
        logger.debug(f"RECEIVED RESPONSE {serial_return}")
        return serial_return

    def _command_response(self, command: str) -> str:
        self._command(command)
        instrument_response = self._response()
        if not instrument_response:
            raise Exception("INSTRUMENT DID NOT RESPOND")
        if "*E" in instrument_response:
            raise Exception(f"INSTRUMENT ERROR {instrument_response}")
        return instrument_response

    def read_identity(self) -> tuple[str, str, str, str]:
        instrument_response = self._command_response("*IDN?")
        manufacturer, model, serial_number, firmware_version = (
            instrument_response.split(",")
        )
        logging.debug(
            f"MANUFACTURER {manufacturer} MODEL {model} SERIAL NUMBER {serial_number} FIRMWARE VERSION {firmware_version}"
        )
        return manufacturer, model, serial_number, firmware_version

    def set_mode(self, mode: str):
        if mode not in self.modes:
            raise ValueError(f"INVALID MODE {mode}")
        self._command(f"MODE {mode}")
        self._current_mode = mode

    def set_factor(self, factor: str):
        if factor not in self.factors:
            raise ValueError(f"INVALID FACTOR {factor}")
        self._command(f"DISP2 {factor}")
        self._current_factor = factor

    def set_frequency(self, frequency: str):
        if frequency not in self.frequencies:
            raise ValueError(f"INVALID FREQUENCY {frequency}")
        self._command(f"FREQ {frequency}")
        self._current_frequency = frequency

    def set_function(self, function: str):
        if function not in self.functions:
            raise ValueError(f"INVALID FUNCTION {function}")
        self._command(f"FUNC {function}")
        self._current_function = function

    def set_range(self, range: str):
        if self._current_function == "":
            raise Exception("FUNCTION MUST BE SET BEFORE SETTING RANGE")
        if range not in self.ranges[self._current_function]:
            raise ValueError(
                f"INVALID RANGE {range} FOR FUNCTION {self._current_function}"
            )
        self._command(f"RANG {range}")
        self._current_range = range

    def get_measurement(self) -> float:
        if self._current_function == "":
            raise Exception("FUNCTION MUST BE SET BEFORE READING MEASUREMENT")
        try:
            instrument_string = self._command_response("FETC?")
            instrument_measurement = float(instrument_string)
            return instrument_measurement
        except:
            raise ValueError(
                f"INSTRUMENT DID NOT RETURN A VALID MEASUREMENT {instrument_string}"
            )

    def get_all_measurements(self) -> dict[str, float]:
        if self._current_function == "":
            raise Exception("FUNCTION MUST BE SET BEFORE READING MEASUREMENT")
        # expected response: Rs,+3.834978E+02,Cs,+6.856665E-07,...
        instrument_string = self._command_response("FETC? ALL")
        try:
            instrument_measurements = instrument_string.split(",")
            measurement_dict: dict[str, float] = {}
            for i in range(0, len(instrument_measurements), 2):
                measurement_dict[instrument_measurements[i]] = float(
                    instrument_measurements[i + 1]
                )
            return measurement_dict
        except:
            raise ValueError(
                f"INSTRUMENT DID NOT RETURN VALID MEASUREMENTS {instrument_string}"
            )

    def check_errors(self) -> list[str]:
        # expected return format no error +0,\s"No\serror"\r\n
        # expected return format for error -100,\s"Command\serror"\r\n
        instrument_string = self._command_response("SYST:ERR?")
        try:
            error_code, error_message = instrument_string.split(",")
            error_code = int(error_code)
            error_message = error_message.strip().strip('"')
            if error_code == 0:
                return []
            else:
                return [f"ERROR CODE {error_code} ERROR MESSAGE {error_message}"]
        except:
            raise ValueError(
                f"INSTRUMENT DID NOT RETURN VALID ERROR RESPONSE {instrument_string}"
            )

    def refresh(self):
        self._command("SYST:ERR?\n")
        self._command("SYST:ERR?\n")
        self.set_mode(self._current_mode)
        self.set_factor(self._current_factor)
        self.set_frequency(self._current_frequency)
        self.set_function(self._current_function)
        self.set_range(self._current_range)
        self._command("SYST:ERR?\n")

    def close(self):
        self.serial.close()


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

    # perform a simple LCR identity check
    manufacturer, model, serial_number, firmware_version = lcr.read_identity()
    print(
        f"MANUFACTURER {manufacturer} MODEL {model} SERIAL NUMBER {serial_number} FIRMWARE VERSION {firmware_version}"
    )

    # close the device and leave the handle open for next session
    lcr.close()
