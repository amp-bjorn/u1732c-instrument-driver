# Agilent/Keysight U1732C LCR Meter Driver & GUI

A professional-grade Python interface for the U1732C Handheld LCR Meter. This project includes a core Python driver (compliant with `pyproject.toml`) and a modern dark-themed GUI for benchtop data acquisition.

## 🛠 Features

- **Complete SCPI Support**: Full control over Modes, Functions, Ranges, and Frequencies.
- **Dual Data Acquisition**: Read primary screen measurements or poll all secondary parameters simultaneously.
- **Dark Mode GUI**: A high-contrast, compact interface with engineering notation and real-time logging.
- **CSV Logging**: Automatic timestamped data capture for long-term component stability testing.

---

## 📖 SCPI Command Reference

The driver wraps these low-level serial commands into high-level Python methods.

| **Command** | **Parameter Options**           | **Description**          | **Example Usage** | **Example Return (Blank means no return value)**                                                                                                       |
| ----------- | ------------------------------- | ------------------------ | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `*IDN?`     | -                               | Identity check           | `*IDN?`           | `Agilent Technologies,U1732C,...`                                                                                                                      |
| `SYST:ERR?` | -                               | Error queue check        | `SYST:ERR?`       | `+0, "No error"`                                                                                                                                       |
| `MODE`      | `SER`, `PAL`                    | Series vs Parallel       | `MODE SER`        | -                                                                                                                                                      |
| `DISP2`     | `D`, `Q`, `TH`                  | Set secondary parameter  | `DISP2 Q`         | -                                                                                                                                                      |
| `FREQ`      | `100`, `120`, `1k`, `10k`       | Test frequency (Hz)      | `FREQ 1k`         | -                                                                                                                                                      |
| `FUNC`      | `R`, `C`, `L`, `Z`, `ESR`, `AI` | Primary measurement type | `FUNC C`          | -                                                                                                                                                      |
| `RANG`      | _See Range Table below_         | Set manual range         | `RANG 20u`        | -                                                                                                                                                      |
| `FETC?`     | -                               | Read primary value       | `FETC?`           | `+6.856E-07`                                                                                                                                           |
| `FETC? ALL` | -                               | Read all parameters      | `FETC? ALL`       | `Rs,+3.809052E-13,Ls,+4.316664E+09,Rp,+6.172276E-14,Lp,+4.316802E+09,Z,+4.316733E+09,TH,+5.774222E-01,F,+1.000000E+03,D,+1.774207E+02,Q,+5.636322E-03` |

### 📉 Range Options by Function

|Function|Available Range Arguments|
|---|---|
|**R / Z**|`2`, `20`, `200`, `2k`, `20k`, `200k`, `2M`, `20M`, `200M`|
|**L**|`2000u`, `20m`, `200m`, `2`, `20`, `200`, `2k`|
|**C**|`2000p`, `20n`, `200n`, `2000n`, `20u`, `200u`, `20m`|

---

## 🚀 Installation

### 1. Install the Driver

Navigate to the root directory and install the package in editable mode:

Bash

```
pip install -e .
```

### 2. Run the GUI

Ensure your meter is connected via the IR-to-USB cable, then launch the dashboard:

Bash

```
python main_gui.py
```

---

## 💻 Programmatic Usage

If you want to use the driver in your own scripts:

Python

```
from U1732C import U1732C

# Initialize connection
lcr = U1732C(port="COM7")

# Configure meter
lcr.set_function("C")
lcr.set_range("20u")
lcr.set_frequency("1k")

# Take reading
reading = lcr.get_measurement()
print(f"Capacitance: {reading} F")

lcr.close()
```

---

## 📦 Building an Executable

To bundle the GUI and driver into a single standalone `.exe` for Windows:

Bash

```
pyinstaller --noconsole --onefile --paths=src --name "LCR_Dashboard" main_gui.py
```

---

### UI Overview

The GUI uses a non-blocking polling architecture to ensure the interface remains responsive even during "high-speed" data acquisition.