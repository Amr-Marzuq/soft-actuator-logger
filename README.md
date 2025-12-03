# Pressure & Displacement Logger for Soft Actuators

This project is a **Python GUI application** for logging **pressure** and **displacement** during soft actuator experiments.

It was developed to interface with:

- A **KEYENCE GP-M001T pressure sensor** (connected via Arduino)
- A **KEYENCE LK-G3000 laser displacement sensor** (for measuring soft actuator deformation)

The GUI is built with **PySide6** and **pyqtgraph**, and it provides real-time plots, calibration tools, and CSV data export.

---

## Features

- 🔌 **Serial connection** management (select COM port, connect/disconnect)
- 🧪 **Two-step calibration** for:
  - Pressure (kPa) based on voltage from the Arduino
  - Displacement (mm) based on voltage from the Arduino
- 📈 **Real-time plots**:
  - Pressure vs time
  - Displacement vs time
- 📋 **Live data table** showing:
  - Time (s)
  - Pressure (kPa)
  - Displacement (mm)
- 💾 **Data export**:
  - Save to CSV
  - Copy data to clipboard as CSV text
- 🌙 **Dark theme** for comfortable lab usage

---

## Hardware Setup 

- **Microcontroller**: Arduino (Pro Micro)
- **Sensors**:
  - KEYENCE GP-M001T pressure sensor (analog voltage output)
  - KEYENCE LK-G3000 laser displacement sensor (analog voltage output)
- The Arduino firmware is expected to:
  - Send **pressure voltage** when receiving the command `'a'`
  - Send **displacement voltage** when receiving the command `'b'`

> Note: You can adapt the Arduino code to match this protocol.

--------------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------------

Run the application:

```bash
python src/pressure_displacement_logger.py
```

1) Connection Tab
- Go to the Connection tab
- Select the correct COM port for the Arduino
- Click Connect
- The status indicator will turn green when successful

2) Calibration Tab
Perform two‑point calibration for both sensors.

Pressure Calibration:
- Set the known low pressure value
- Click "Record low"
- Set the known high pressure value
- Click "Record high"

Displacement Calibration:
- Set the low displacement value (mm)
- Click "Record low"
- Set the high displacement value (mm)
- Click "Record high"

The application automatically computes a linear mapping from voltage → physical units.

3) Plotter Tab
- Set the sampling rate (samples per second)
- Click Start to begin live data logging
- Real‑time pressure and displacement plots will update continuously
- Click Stop to finish the experiment
- Export data using:
  • Save CSV
  • Copy data (CSV)

--------------------------------------------------------------------------------
PROJECT BACKGROUND
--------------------------------------------------------------------------------

This tool was developed as part of my doctoral research in robotics, specifically 
for characterizing soft pneumatic/electrohydrodynamic actuators.

It enables:
- Measuring internal pressure inside soft robotic actuators
- Measuring external deformation/displacement using a laser sensor
- Logging synchronized data for actuator performance analysis

It demonstrates skills in:
- Python GUI development (PySide6)
- Real-time visualization (pyqtgraph)
- Sensor integration & Arduino communication
- Experimental automation and data acquisition


## Installation

```bash
# Clone this repository
git clone https://github.com/<your-username>/soft-actuator-logger.git
cd soft-actuator-logger

# (Optional) create a virtual environment
# python -m venv .venv
# source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
## GUI Preview

### Main Connection Interface
<img width="1492" height="902" alt="gui_Connection" src="https://github.com/user-attachments/assets/a3f848d5-951b-4c5b-8f89-5fa4c020d79d" />
### Calibration Tab
<img width="1486" height="900" alt="calibration_tab" src="https://github.com/user-attachments/assets/e4a0a5a4-bf5c-48d2-84f8-ee0256e16d19" />
### Real-time Plotting
<img width="1487" height="900" alt="Data_Plotter" src="https://github.com/user-attachments/assets/adb346ea-6aba-4053-962e-5b6ae3bb515a" />

---


