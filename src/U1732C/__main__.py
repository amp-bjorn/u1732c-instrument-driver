
from u1732c import U1732C
import logging


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # create and open the lcr object 
    lcr = U1732C(port="COM7")

    # perform a simple LCR identity check
    manufacturer, model, serial_number, firmware_version = lcr.read_identity()
    print(f"MANUFACTURER {manufacturer} MODEL {model} SERIAL NUMBER {serial_number} FIRMWARE VERSION {firmware_version}")

    # close the device and leave the handle open for next session 
    lcr.close()