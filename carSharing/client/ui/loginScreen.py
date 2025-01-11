from PyQt5 import QtCore, QtWidgets
from queryUI import MainWindow

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setStyleSheet("background-color: white;")

        # Title Label
        self.title_label = QtWidgets.QLabel(self.centralwidget)
        self.title_label.setText("CarHop")
        self.title_label.setGeometry(QtCore.QRect(300, 100, 200, 50))
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #333;")

        # Username Label and Input
        self.username_label = QtWidgets.QLabel(self.centralwidget)
        self.username_label.setText("Username:")
        self.username_label.setGeometry(QtCore.QRect(250, 200, 100, 30))

        self.username_input = QtWidgets.QLineEdit(self.centralwidget)
        self.username_input.setGeometry(QtCore.QRect(350, 200, 200, 30))

        # Password Label and Input
        self.password_label = QtWidgets.QLabel(self.centralwidget)
        self.password_label.setText("Password:")
        self.password_label.setGeometry(QtCore.QRect(250, 250, 100, 30))

        self.password_input = QtWidgets.QLineEdit(self.centralwidget)
        self.password_input.setGeometry(QtCore.QRect(350, 250, 200, 30))
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # Login Button
        self.login_button = QtWidgets.QPushButton(self.centralwidget)
        self.login_button.setText("Login")
        self.login_button.setGeometry(QtCore.QRect(350, 300, 100, 30))
        self.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        # implementare cu mysql maybe later ?
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "" and password == "":
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid Username or Password")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
