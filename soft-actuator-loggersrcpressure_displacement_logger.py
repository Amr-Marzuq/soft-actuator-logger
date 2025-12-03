import sys
import time
import csv

import serial
import serial.tools.list_ports

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton,
    QComboBox, QDoubleSpinBox, QSpinBox, QFileDialog, QMessageBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QAbstractItemView
)

import pyqtgraph as pg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pressure & Displacement Logger")

        # Serial port object
        self.ser = None

        # Calibration data
        self.pressure_low_p = None
        self.pressure_low_v = None
        self.pressure_high_p = None
        self.pressure_high_v = None
        self.pressure_slope = None
        self.pressure_offset = None

        self.disp_low_d = None
        self.disp_low_v = None
        self.disp_high_d = None
        self.disp_high_v = None
        self.disp_slope = None
        self.disp_offset = None

        # Data storage
        self.time_data = []
        self.pressure_data = []
        self.disp_data = []

        self.max_points = 2000  # for plot history

        # Timer for acquisition
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_and_update)

        self.start_time = None

        # Tabs
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.connection_tab = QWidget()
        self.calibration_tab = QWidget()
        self.plot_tab = QWidget()

        self.tab_widget.addTab(self.connection_tab, "Connection")
        self.tab_widget.addTab(self.calibration_tab, "Calibration")
        self.tab_widget.addTab(self.plot_tab, "Plotter")

        self.init_connection_tab()
        self.init_calibration_tab()
        self.init_plot_tab()

        self.apply_dark_theme()

    # ---------- Dark Theme ----------
    def apply_dark_theme(self):
        app = QApplication.instance()
        if app is None:
            return  # safety; will still work with default theme

        palette = QPalette()

        palette.setColor(QPalette.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(0, 122, 204))
        palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.HighlightedText, Qt.black)

        app.setPalette(palette)

        pg.setConfigOption('background', (30, 30, 30))
        pg.setConfigOption('foreground', 'w')

    # ---------- Connection Tab ----------
    def init_connection_tab(self):
        layout = QVBoxLayout()

        form = QFormLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()

        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.clicked.connect(self.refresh_ports)

        form.addRow("Serial Port:", self.port_combo)
        form.addRow("", refresh_btn)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_serial)

        self.connection_status = QLabel("Status: Not connected")
        self.connection_status.setStyleSheet("color: orange;")

        layout.addLayout(form)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.connection_status)
        layout.addStretch()

        self.connection_tab.setLayout(layout)

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.port_combo.addItem(p.device)

    def connect_serial(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None

        port = self.port_combo.currentText().strip()
        if not port:
            QMessageBox.warning(self, "Error", "No COM port selected.")
            return

        try:
            self.ser = serial.Serial(port, 9600, timeout=0.3)
            self.connection_status.setText(f"Status: Connected to {port}")
            self.connection_status.setStyleSheet("color: lightgreen;")
            QMessageBox.information(self, "Connection", f"Connected to {port}")
        except Exception as e:
            self.ser = None
            self.connection_status.setText("Status: Connection failed")
            self.connection_status.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Error", f"Failed to connect:\n{e}")

    # ---------- Calibration Tab ----------
    def init_calibration_tab(self):
        main_layout = QVBoxLayout()

        # Pressure Calibration
        pressure_group = QGroupBox("Pressure Calibration")
        p_layout = QVBoxLayout()
        p_form_low = QFormLayout()
        p_form_high = QFormLayout()

        self.pressure_low_spin = QDoubleSpinBox()
        self.pressure_low_spin.setSuffix(" kPa")
        self.pressure_low_spin.setRange(-1000, 1000)
        self.pressure_low_spin.setValue(0.0)

        self.pressure_low_voltage_label = QLabel("Not recorded")

        self.pressure_high_spin = QDoubleSpinBox()
        self.pressure_high_spin.setSuffix(" kPa")
        self.pressure_high_spin.setRange(-1000, 1000)
        self.pressure_high_spin.setValue(20.0)

        self.pressure_high_voltage_label = QLabel("Not recorded")

        self.pressure_status_label = QLabel("Status: Not calibrated")
        self.pressure_status_label.setStyleSheet("color: orange;")

        btn_p_low = QPushButton("Record low pressure point")
        btn_p_low.clicked.connect(self.record_pressure_low)

        btn_p_high = QPushButton("Record high pressure point")
        btn_p_high.clicked.connect(self.record_pressure_high)

        p_form_low.addRow("Low pressure value:", self.pressure_low_spin)
        p_form_low.addRow("Low voltage:", self.pressure_low_voltage_label)
        p_form_low.addRow("", btn_p_low)

        p_form_high.addRow("High pressure value:", self.pressure_high_spin)
        p_form_high.addRow("High voltage:", self.pressure_high_voltage_label)
        p_form_high.addRow("", btn_p_high)

        p_layout.addLayout(p_form_low)
        p_layout.addLayout(p_form_high)
        p_layout.addWidget(self.pressure_status_label)
        pressure_group.setLayout(p_layout)

        # Displacement Calibration
        disp_group = QGroupBox("Displacement Calibration")
        d_layout = QVBoxLayout()
        d_form_low = QFormLayout()
        d_form_high = QFormLayout()

        self.disp_low_spin = QDoubleSpinBox()
        self.disp_low_spin.setSuffix(" mm")
        self.disp_low_spin.setRange(-1000, 1000)
        self.disp_low_spin.setValue(-5.0)

        self.disp_low_voltage_label = QLabel("Not recorded")

        self.disp_high_spin = QDoubleSpinBox()
        self.disp_high_spin.setSuffix(" mm")
        self.disp_high_spin.setRange(-1000, 1000)
        self.disp_high_spin.setValue(5.0)

        self.disp_high_voltage_label = QLabel("Not recorded")

        self.disp_status_label = QLabel("Status: Not calibrated")
        self.disp_status_label.setStyleSheet("color: orange;")

        btn_d_low = QPushButton("Record low displacement point")
        btn_d_low.clicked.connect(self.record_disp_low)

        btn_d_high = QPushButton("Record high displacement point")
        btn_d_high.clicked.connect(self.record_disp_high)

        d_form_low.addRow("Low displacement value:", self.disp_low_spin)
        d_form_low.addRow("Low voltage:", self.disp_low_voltage_label)
        d_form_low.addRow("", btn_d_low)

        d_form_high.addRow("High displacement value:", self.disp_high_spin)
        d_form_high.addRow("High voltage:", self.disp_high_voltage_label)
        d_form_high.addRow("", btn_d_high)

        d_layout.addLayout(d_form_low)
        d_layout.addLayout(d_form_high)
        d_layout.addWidget(self.disp_status_label)
        disp_group.setLayout(d_layout)

        main_layout.addWidget(pressure_group)
        main_layout.addWidget(disp_group)
        main_layout.addStretch()

        self.calibration_tab.setLayout(main_layout)

    def ensure_serial(self):
        if not self.ser or not self.ser.is_open:
            QMessageBox.warning(self, "Error", "Serial port not connected.")
            return False
        return True

    def read_voltage_from_arduino(self, command_char):
        if not self.ensure_serial():
            return None
        try:
            self.ser.reset_input_buffer()
            self.ser.write(command_char.encode('ascii'))
            self.ser.flush()
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                raise ValueError("Empty response")
            value = float(line)
            return value
        except Exception as e:
            QMessageBox.warning(self, "Read Error",
                                f"Failed to read voltage for '{command_char}':\n{e}")
            return None

    # Pressure calibration
    def record_pressure_low(self):
        v = self.read_voltage_from_arduino('a')  # pressure command
        if v is None:
            return
        self.pressure_low_p = self.pressure_low_spin.value()
        self.pressure_low_v = v
        self.pressure_low_voltage_label.setText(f"{v:.3f} V")
        self.update_pressure_calibration()

    def record_pressure_high(self):
        v = self.read_voltage_from_arduino('a')  # pressure command
        if v is None:
            return
        self.pressure_high_p = self.pressure_high_spin.value()
        self.pressure_high_v = v
        self.pressure_high_voltage_label.setText(f"{v:.3f} V")
        self.update_pressure_calibration()

    def update_pressure_calibration(self):
        if None not in (self.pressure_low_p, self.pressure_low_v,
                        self.pressure_high_p, self.pressure_high_v):
            if self.pressure_high_v == self.pressure_low_v:
                QMessageBox.warning(self, "Calibration Error",
                                    "Pressure calibration voltages are identical.")
                return
            self.pressure_slope = (self.pressure_high_p - self.pressure_low_p) / \
                                  (self.pressure_high_v - self.pressure_low_v)
            self.pressure_offset = self.pressure_low_p - self.pressure_slope * self.pressure_low_v
            self.pressure_status_label.setText(
                f"Status: Calibrated (P = {self.pressure_slope:.3f}*V + {self.pressure_offset:.3f})"
            )
            self.pressure_status_label.setStyleSheet("color: lightgreen;")

    # Displacement calibration
    def record_disp_low(self):
        v = self.read_voltage_from_arduino('b')  # displacement command
        if v is None:
            return
        self.disp_low_d = self.disp_low_spin.value()
        self.disp_low_v = v
        self.disp_low_voltage_label.setText(f"{v:.3f} V")
        self.update_disp_calibration()

    def record_disp_high(self):
        v = self.read_voltage_from_arduino('b')  # displacement command
        if v is None:
            return
        self.disp_high_d = self.disp_high_spin.value()
        self.disp_high_v = v
        self.disp_high_voltage_label.setText(f"{v:.3f} V")
        self.update_disp_calibration()

    def update_disp_calibration(self):
        if None not in (self.disp_low_d, self.disp_low_v,
                        self.disp_high_d, self.disp_high_v):
            if self.disp_high_v == self.disp_low_v:
                QMessageBox.warning(self, "Calibration Error",
                                    "Displacement calibration voltages are identical.")
                return
            self.disp_slope = (self.disp_high_d - self.disp_low_d) / \
                              (self.disp_high_v - self.disp_low_v)
            self.disp_offset = self.disp_low_d - self.disp_slope * self.disp_low_v
            self.disp_status_label.setText(
                f"Status: Calibrated (D = {self.disp_slope:.3f}*V + {self.disp_offset:.3f})"
            )
            self.disp_status_label.setStyleSheet("color: lightgreen;")

    # ---------- Plot Tab ----------
    def init_plot_tab(self):
        main_layout = QHBoxLayout()

        # Left: plots
        plot_layout = QVBoxLayout()

        self.pressure_plot = pg.PlotWidget(title="Pressure vs Time")
        self.pressure_plot.setLabel('bottom', 'Time', units='s')
        self.pressure_plot.setLabel('left', 'Pressure', units='kPa')

        self.disp_plot = pg.PlotWidget(title="Displacement vs Time")
        self.disp_plot.setLabel('bottom', 'Time', units='s')
        self.disp_plot.setLabel('left', 'Displacement', units='mm')

        self.pressure_curve = self.pressure_plot.plot(pen=pg.mkPen(width=2))
        self.disp_curve = self.disp_plot.plot(pen=pg.mkPen(width=2))

        plot_layout.addWidget(self.pressure_plot)
        plot_layout.addWidget(self.disp_plot)

        # Right: controls + table
        control_layout = QVBoxLayout()

        # Sampling rate
        sr_layout = QFormLayout()
        self.sampling_spin = QSpinBox()
        self.sampling_spin.setRange(1, 1000)
        self.sampling_spin.setValue(10)
        sr_layout.addRow("Sampling rate (samples/s):", self.sampling_spin)
        control_layout.addLayout(sr_layout)

        # Buttons
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_logging)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_logging)
        self.stop_button.setEnabled(False)

        self.save_button = QPushButton("Save CSV")
        self.save_button.clicked.connect(self.save_csv)

        self.copy_button = QPushButton("Copy data (CSV)")
        self.copy_button.clicked.connect(self.copy_data)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.save_button)
        control_layout.addWidget(self.copy_button)

        control_layout.addSpacing(10)

        # Real-time readings
        rt_group = QGroupBox("Real-time readings")
        rt_layout = QFormLayout()
        self.current_time_label = QLabel("-- s")
        self.current_pressure_label = QLabel("-- kPa")
        self.current_disp_label = QLabel("-- mm")
        rt_layout.addRow("Time:", self.current_time_label)
        rt_layout.addRow("Pressure:", self.current_pressure_label)
        rt_layout.addRow("Displacement:", self.current_disp_label)
        rt_group.setLayout(rt_layout)
        control_layout.addWidget(rt_group)

        control_layout.addSpacing(10)

        # Data table (logger view)
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(
            ["time_s", "pressure_kPa", "displacement_mm"]
        )
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSortingEnabled(False)

        control_layout.addWidget(QLabel("Data log:"))
        control_layout.addWidget(self.data_table)

        control_layout.addStretch()

        main_layout.addLayout(plot_layout, stretch=3)
        main_layout.addLayout(control_layout, stretch=2)

        self.plot_tab.setLayout(main_layout)

    # ---------- Logging ----------
    def start_logging(self):
        if not self.ensure_serial():
            return

        # Reset data
        self.time_data = []
        self.pressure_data = []
        self.disp_data = []
        self.data_table.setRowCount(0)

        self.start_time = time.monotonic()

        rate = self.sampling_spin.value()
        interval_ms = int(1000 / rate)
        self.timer.start(interval_ms)

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_logging(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def map_pressure(self, voltage):
        if self.pressure_slope is None or self.pressure_offset is None:
            return voltage  # fallback: show raw volts
        return self.pressure_slope * voltage + self.pressure_offset

    def map_displacement(self, voltage):
        if self.disp_slope is None or self.disp_offset is None:
            return voltage
        return self.disp_slope * voltage + self.disp_offset

    def safe_read_voltage(self, command_char):
        try:
            self.ser.reset_input_buffer()
            self.ser.write(command_char.encode('ascii'))
            self.ser.flush()
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                return None
            return float(line)
        except Exception:
            return None

    def read_and_update(self):
        if not self.ser or not self.ser.is_open:
            self.stop_logging()
            return

        v_pressure = self.safe_read_voltage('a')  # pressure
        v_disp = self.safe_read_voltage('b')      # displacement

        if v_pressure is None or v_disp is None:
            return

        t = time.monotonic() - self.start_time
        p_kpa = self.map_pressure(v_pressure)
        d_mm = self.map_displacement(v_disp)

        self.time_data.append(t)
        self.pressure_data.append(p_kpa)
        self.disp_data.append(d_mm)

        # Limit for plotting
        if len(self.time_data) > self.max_points:
            self.time_data = self.time_data[-self.max_points:]
            self.pressure_data = self.pressure_data[-self.max_points:]
            self.disp_data = self.disp_data[-self.max_points:]

        # Update plots
        self.pressure_curve.setData(self.time_data, self.pressure_data)
        self.disp_curve.setData(self.time_data, self.disp_data)

        # Update live labels
        self.current_time_label.setText(f"{t:.2f} s")
        self.current_pressure_label.setText(f"{p_kpa:.3f} kPa")
        self.current_disp_label.setText(f"{d_mm:.3f} mm")

        # Update table (full history)
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        self.data_table.setItem(row, 0, QTableWidgetItem(f"{t:.6f}"))
        self.data_table.setItem(row, 1, QTableWidgetItem(f"{p_kpa:.6f}"))
        self.data_table.setItem(row, 2, QTableWidgetItem(f"{d_mm:.6f}"))
        self.data_table.scrollToBottom()

    # ---------- Save / Copy ----------
    def save_csv(self):
        if not self.time_data:
            QMessageBox.information(self, "No data", "No data to save.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return

        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["time_s", "pressure_kPa", "displacement_mm"])
                for t, p, d in zip(self.time_data, self.pressure_data, self.disp_data):
                    writer.writerow([f"{t:.6f}", f"{p:.6f}", f"{d:.6f}"])
            QMessageBox.information(self, "Saved", f"Data saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save CSV:\n{e}")

    def copy_data(self):
        if not self.time_data:
            QMessageBox.information(self, "No data", "No data to copy.")
            return

        lines = ["time_s,pressure_kPa,displacement_mm"]
        for t, p, d in zip(self.time_data, self.pressure_data, self.disp_data):
            lines.append(f"{t:.6f},{p:.6f},{d:.6f}")

        text = "\n".join(lines)
        QGuiApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Data copied to clipboard as CSV text.")


# ---------- Jupyter-safe launcher ----------

# Reuse existing QApplication if present (important for Jupyter)
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

# Optional: configure pyqtgraph colors globally (already done in apply_dark_theme,
# but this keeps it similar to your snippet)
pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')

window = MainWindow()
window.resize(1200, 700)
window.show()