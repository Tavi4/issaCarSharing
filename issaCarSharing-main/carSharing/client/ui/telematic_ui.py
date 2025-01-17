import socket
import json
from PyQt5 import QtWidgets

class TelematicUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.vin = None
        self.client_id = None
        self.is_valid_id = False

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # ------------- VIN Input -------------
        self.vin_input = QtWidgets.QLineEdit()
        self.vin_input.setPlaceholderText("Enter VIN")
        layout.addWidget(QtWidgets.QLabel("VIN:"))
        layout.addWidget(self.vin_input)

        # ------------- Client ID Input -------------
        self.client_id_input = QtWidgets.QLineEdit()
        self.client_id_input.setPlaceholderText("Enter Client ID")
        layout.addWidget(QtWidgets.QLabel("Client ID:"))
        layout.addWidget(self.client_id_input)

        # ------------- Submit ID Button -------------
        self.submit_id_button = QtWidgets.QPushButton("Submit ID")
        self.submit_id_button.clicked.connect(self.validate_client_id)
        layout.addWidget(self.submit_id_button)

        # ------------- Reset Button -------------
        self.reset_button = QtWidgets.QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_fields)
        layout.addWidget(self.reset_button)

        # ------------- Status Display -------------
        self.status_label = QtWidgets.QLabel("Status: Please validate Client ID")
        layout.addWidget(self.status_label)

        # ------------- lock/unlock buttons -------------
        self.unlock_doors_button = QtWidgets.QPushButton("Unlock Doors")
        self.unlock_doors_button.clicked.connect(lambda: self.send_telematics_request("unlock_doors"))

        self.lock_doors_button = QtWidgets.QPushButton("Lock Doors")
        self.lock_doors_button.clicked.connect(lambda: self.send_telematics_request("lock_doors"))

        # ------------- turn on/off lights -------------
        self.turn_on_lights_button = QtWidgets.QPushButton("Turn On Lights")
        self.turn_on_lights_button.clicked.connect(lambda: self.send_telematics_request("turn_on_lights"))

        self.turn_off_lights_button = QtWidgets.QPushButton("Turn Off Lights")
        self.turn_off_lights_button.clicked.connect(lambda: self.send_telematics_request("turn_off_lights"))

        # ------------- disable buttons initially -------------
        self.unlock_doors_button.setEnabled(False)
        self.lock_doors_button.setEnabled(False)
        self.turn_on_lights_button.setEnabled(False)
        self.turn_off_lights_button.setEnabled(False)

        # ------------- add buttons to layout -------------
        layout.addWidget(self.unlock_doors_button)
        layout.addWidget(self.lock_doors_button)
        layout.addWidget(self.turn_on_lights_button)
        layout.addWidget(self.turn_off_lights_button)

        # ------------- doors and lights status -------------
        self.door_status_label = QtWidgets.QLabel("Doors: Unknown")
        self.light_status_label = QtWidgets.QLabel("Lights: Unknown")
        layout.addWidget(self.door_status_label)
        layout.addWidget(self.light_status_label)

        self.setLayout(layout)
        self.setWindowTitle("Telematic UI")

    def validate_client_id(self):
        vin = self.vin_input.text()
        client_id = self.client_id_input.text()

        if not vin or not client_id:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter both VIN and Client ID.")
            return

        # sending validation request to server
        request = {
            "action": "validate_client_id",
            "vin": vin,
            "client_id": client_id
        }
        print(f"Debug: Attempting to validate VIN: {vin}, Client ID: {client_id}")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(("127.0.0.1", 12345))
                client_socket.sendall(json.dumps(request).encode())
                response_data = client_socket.recv(1024).decode()
                response = json.loads(response_data)

                if response.get("status") == "success":
                    self.is_valid_id = True
                    self.vin = vin
                    self.client_id = client_id
                    self.status_label.setText("Status: Valid Client ID")

                    # enable telematics buttons
                    self.enable_telematics_buttons(True)

                    # update door and light status
                    self.update_status(response)

                else:
                    self.is_valid_id = False
                    self.status_label.setText("Status: Invalid Client ID")
                    QtWidgets.QMessageBox.warning(self, "Error", response.get("message", "Invalid ID."))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to connect to server: {str(e)}")

    def send_telematics_request(self, control):
        if not self.is_valid_id:
            QtWidgets.QMessageBox.warning(self, "Error", "Please validate Client ID first.")
            return

        request = {
            "action": "telematics_control",
            "vin": self.vin,
            "client_id": self.client_id,
            "control": control
        }

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(("127.0.0.1", 12345))
                client_socket.sendall(json.dumps(request).encode())
                response_data = client_socket.recv(1024).decode()
                response = json.loads(response_data)

                QtWidgets.QMessageBox.information(self, "Info", response.get("message", "No response message."))

                # update doors/lights status
                self.update_status(response)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to connect to server: {str(e)}")

    def update_status(self, response):
        doors_locked = response.get("doors_locked", False)
        lights_on = response.get("lights", False)

        self.door_status_label.setText(f"Doors: {'Locked' if doors_locked else 'Unlocked'}")
        self.light_status_label.setText(f"Lights: {'On' if lights_on else 'Off'}")

    def reset_fields(self):
        self.vin_input.clear()
        self.client_id_input.clear()
        self.status_label.setText("Status: Please validate Client ID")
        self.door_status_label.setText("Doors: Unknown")
        self.light_status_label.setText("Lights: Unknown")
        self.enable_telematics_buttons(False)
        self.is_valid_id = False

    def enable_telematics_buttons(self, enable):
        self.unlock_doors_button.setEnabled(enable)
        self.lock_doors_button.setEnabled(enable)
        self.turn_on_lights_button.setEnabled(enable)
        self.turn_off_lights_button.setEnabled(enable)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = TelematicUI()
    window.show()
    sys.exit(app.exec_())
