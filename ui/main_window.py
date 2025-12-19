from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QCheckBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QStatusBar,
    QMessageBox, QProgressBar
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from core.nmap_runner import scan_multiple
import pyperclip


class ScanWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, targets, options):
        super().__init__()
        self.targets = targets
        self.options = options

    def run(self):
        results = scan_multiple(self.targets, self.options, workers=3)
        self.finished.emit(results)


class ScanTab(QWidget):
    def __init__(self):
        super().__init__()

        main = QVBoxLayout()
        main.setSpacing(12)

        top = QHBoxLayout()
        self.targets = QTextEdit()
        self.targets.setPlaceholderText("One target per line")
        self.targets.setFixedHeight(120)

        paste_btn = QPushButton("📋 Paste")
        paste_btn.clicked.connect(self.paste_clipboard)

        top.addWidget(self.targets)
        top.addWidget(paste_btn)

        opts = QHBoxLayout()
        self.fast = QCheckBox("Fast (-F)")
        self.service = QCheckBox("Service (-sV)")
        self.os = QCheckBox("OS (-O)")
        opts.addWidget(self.fast)
        opts.addWidget(self.service)
        opts.addWidget(self.os)
        opts.addStretch()

        self.run = QPushButton("Run Scan")
        self.run.clicked.connect(self.run_scan)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Port", "Proto", "State", "Service"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        main.addLayout(top)
        main.addLayout(opts)
        main.addWidget(self.run)
        main.addWidget(self.progress)
        main.addWidget(self.table)
        self.setLayout(main)

    def paste_clipboard(self):
        self.targets.setText(pyperclip.paste())

    def run_scan(self):
        self.table.setRowCount(0)
        self.run.setEnabled(False)
        self.progress.show()

        targets = [
            t.strip() for t in self.targets.toPlainText().splitlines()
            if t.strip()
        ]

        options = []
        if self.fast.isChecked():
            options.append("-F")
        if self.service.isChecked():
            options.append("-sV")
        if self.os.isChecked():
            options.append("-O")

        self.worker = ScanWorker(targets, options)
        self.worker.finished.connect(self.show_results)
        self.worker.start()

    def show_results(self, results):
        found_open = False

        for output in results.values():
            for line in output.splitlines():
                if "/tcp" in line or "/udp" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        row = self.table.rowCount()
                        self.table.insertRow(row)

                        port, proto = parts[0].split("/")
                        state = parts[1]
                        service = parts[2]

                        self.table.setItem(row, 0, QTableWidgetItem(port))
                        self.table.setItem(row, 1, QTableWidgetItem(proto))
                        self.table.setItem(row, 2, QTableWidgetItem(state))
                        self.table.setItem(row, 3, QTableWidgetItem(service))

                        color = QColor("#2ecc71") if state == "open" else QColor("#e74c3c")
                        if state == "open":
                            found_open = True

                        for c in range(4):
                            self.table.item(row, c).setBackground(color)

        if not found_open:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem("No open ports found"))

        self.progress.hide()
        self.run.setEnabled(True)

        QMessageBox.information(self, "Done", "Scan completed successfully")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphical Nmap")
        self.resize(960, 680)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.add_tab()

        plus = QPushButton("➕")
        plus.clicked.connect(self.add_tab)
        self.tabs.setCornerWidget(plus, Qt.Corner.TopRightCorner)

        status = QStatusBar()
        status.addPermanentWidget(QLabel("Powered by Khalid Mahran"))
        self.setStatusBar(status)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #eaeaea;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #2c2f4a;
                padding: 6px;
                border-radius: 8px;
            }
            QTextEdit, QTableWidget {
                background-color: #25273c;
                border-radius: 8px;
            }
        """)

    def add_tab(self):
        self.tabs.addTab(ScanTab(), f"Scan {self.tabs.count() + 1}")

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            for i in range(self.tabs.count()):
                self.tabs.setTabText(i, f"Scan {i + 1}")

