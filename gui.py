import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel,
)

import engine


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Calculator")
        self.resize(400, 300)

        layout = QVBoxLayout(self)   # stacks widgets top to bottom
        form = QFormLayout()         # "Label: [input]" rows
        layout.addLayout(form)

        # One example field. Add your other inputs the same way.
        self.age_input = QLineEdit()
        form.addRow("Age:", self.age_input)

        self.calc_button = QPushButton("Calculate")
        self.calc_button.clicked.connect(self.on_calculate)
        layout.addWidget(self.calc_button)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

    def on_calculate(self):
        # Read your inputs here, then call engine.calculate(...)
        self.result_label.setText(f"You entered age: {self.age_input.text()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())