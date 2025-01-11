from PyQt5 import QtCore, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CarHop")
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setStyleSheet("background-color: white;")

        # Welcome Label
        self.welcome_label = QtWidgets.QLabel(self.centralwidget)
        self.welcome_label.setText("Welcome to CarHop!")

        self.welcome_label.setGeometry(QtCore.QRect(200, 250, 400, 50))
        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #gray;")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
