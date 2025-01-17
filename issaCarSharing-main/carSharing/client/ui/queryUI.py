from plistlib import loads

from PyQt5 import QtCore, QtWidgets

import socket
import json

from PyQt5.QtGui import QColor


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("CarHop")
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setStyleSheet("background-color: white;")

        # Rented Label
        self.rented_label = QtWidgets.QLabel(self.centralwidget)
        self.rented_label.setText("")
        self.rented_label.setGeometry(QtCore.QRect(100, 50, 600, 120))
        self.rented_label.setAlignment(QtCore.Qt.AlignCenter)
        self.rented_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")

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
        self.start_rental_button.setGeometry(QtCore.QRect(350, 500, 100, 30))
        self.start_rental_button.clicked.connect(self.start_rental)


        # End Rental Button
        self.end_rental_button = QtWidgets.QPushButton(self.centralwidget)
        self.end_rental_button.setText("End Rental")
        self.end_rental_button.setGeometry(QtCore.QRect(350, 500, 100, 30))
        self.end_rental_button.clicked.connect(self.end_rental)
        self.end_rental_button.hide()

        # Back to menu
        self.back_to_menu_button = QtWidgets.QPushButton(self.centralwidget)
        self.back_to_menu_button.setText("Back to Menu")  # Corrected text setting
        self.back_to_menu_button.setGeometry(QtCore.QRect(350, 550, 100, 30))  # Positioned below End Rental button
        self.back_to_menu_button.clicked.connect(self.back_to_menu)  # Corrected signal connection
        self.back_to_menu_button.hide()




    def load_cars(self):
        response = self.send_request({"action": "query_cars"})
        if response.get("status") == "success":
            self.cars_list.clear()
            for vin, car in response.get("cars", {}).items():
                item = QtWidgets.QListWidgetItem(f"VIN: {vin}, Location: {car['location']}")

                # Make the car non-selectable if not available
                print(car["available"])
                if not car["available"]:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
                    item.setText(item.text()+" -RENTED-")
                    item.setForeground(QColor(150, 150, 150))
                self.cars_list.addItem(item)

        else:
            QtWidgets.QMessageBox.warning(self, "Error", response.get("message"))

    def start_rental(self):
            selected_item = self.cars_list.currentItem()
            if selected_item:
                vin = selected_item.text().split(",")[0].split(": ")[1]
                location = selected_item.text().split(",")[1]
                response = self.send_request({"action": "start_rental", "vin": vin, "client_id": self.username})
                QtWidgets.QMessageBox.information(self, "Info", response.get("message"))
                if response.get("status") == "success":
                    self.rented_vin = vin
                    self.rented_label.setText(f"You have rented your car in {location}!")
                    self.rented_label.show()
                    self.end_rental_button.show()
                    self.start_rental_button.hide()
                    self.welcome_label.hide()
                    self.cars_list.hide()
                    self.back_to_menu_button.show()
                    self.load_cars()


    def end_rental(self):
            if self.rented_vin:
                response = self.send_request({"action": "end_rental", "vin":self.rented_vin})
                QtWidgets.QMessageBox.information(self, "Info", response.get("message"))
                if response.get("status") == "success":
                    self.rented_label.hide()
                    self.start_rental_button.show()
                    self.welcome_label.show()
                    self.cars_list.show()
                    self.end_rental_button.hide()
                    self.back_to_menu_button.hide()
                    self.load_cars()



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

    def back_to_menu(self):
        if self.end_rental_button.isVisible():
            self.rented_label.hide()
            self.start_rental_button.setDisabled(True)
            self.welcome_label.show()
            self.cars_list.show()
            self.end_rental_button.hide()
            self.back_to_menu_button.setText("Back to Rentel")
        else:
            self.rented_label.show()
            self.welcome_label.hide()
            self.start_rental_button.setDisabled(False)
            self.cars_list.hide()
            self.end_rental_button.show()
            self.back_to_menu_button.setText("Back to Menu")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow("TestUser")
    main_window.show()
    sys.exit(app.exec_())
