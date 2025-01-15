from PyQt5 import QtCore, QtWidgets
import socket
import json

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("CarHop")
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setStyleSheet("background-color: white;")

        # Welcome Label
        self.welcome_label = QtWidgets.QLabel(self.centralwidget)
        self.welcome_label.setText(f"Welcome, {username}!")
        self.welcome_label.setGeometry(QtCore.QRect(200, 50, 400, 50))
        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")

        # Cars List
        self.cars_list = QtWidgets.QListWidget(self.centralwidget)
        self.cars_list.setGeometry(QtCore.QRect(50, 150, 700, 300))
        self.load_cars()

        # Start Rental Button
        self.start_rental_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_rental_button.setText("Start Rental")
        self.start_rental_button.setGeometry(QtCore.QRect(250, 500, 100, 30))
        self.start_rental_button.clicked.connect(self.start_rental)

        # End Rental Button
        self.end_rental_button = QtWidgets.QPushButton(self.centralwidget)
        self.end_rental_button.setText("End Rental")
        self.end_rental_button.setGeometry(QtCore.QRect(450, 500, 100, 30))
        self.end_rental_button.clicked.connect(self.end_rental)

    def load_cars(self):
        response = self.send_request({"action": "query_cars"})
        if response.get("status") == "success":
            self.cars_list.clear()
            for vin, car in response.get("cars", {}).items():
                self.cars_list.addItem(f"VIN: {vin}, Location: {car['location']}")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", response.get("message"))

    def start_rental(self):
        selected_item = self.cars_list.currentItem()
        if selected_item:
            vin = selected_item.text().split(",")[0].split(": ")[1]
            response = self.send_request({"action": "start_rental", "vin": vin, "client_id": self.username})
            QtWidgets.QMessageBox.information(self, "Info", response.get("message"))

    def end_rental(self):
        selected_item = self.cars_list.currentItem()
        if selected_item:
            vin = selected_item.text().split(",")[0].split(": ")[1]
            response = self.send_request({"action": "end_rental", "vin": vin})
            QtWidgets.QMessageBox.information(self, "Info", response.get("message"))

    def send_request(self, request):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", 12345))  # Portul serverului
            client.send(json.dumps(request).encode())
            response = json.loads(client.recv(1024).decode())
            client.close()
            return response
        except Exception as e:
            print(f"Error: {e}")
            return {"status": "error", "message": "Server unavailable"}

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow("TestUser")
    main_window.show()
    sys.exit(app.exec_())
