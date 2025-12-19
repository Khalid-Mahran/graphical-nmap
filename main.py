import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow

app = QApplication(sys.argv)

app.setApplicationName("graphical-nmap")
app.setDesktopFileName("graphical-nmap.desktop")
app.setWindowIcon(QIcon("/home/khalid_mahran/.local/share/icons/graphical-nmap.png"))

window = MainWindow()
window.setWindowIcon(QIcon("/home/khalid_mahran/.local/share/icons/graphical-nmap.png"))
window.show()

sys.exit(app.exec())

