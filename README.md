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

---

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
