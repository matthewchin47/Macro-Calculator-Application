import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QRadioButton, QPushButton, QLabel,
    QStackedWidget,
)

import engine


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Calculator")
        self.resize(420, 380)

        layout = QVBoxLayout(self)

        # ---- Unit toggle (FR-2) ----
        unit_row = QHBoxLayout()
        self.metric_radio = QRadioButton("Metric (kg, cm)")
        self.imperial_radio = QRadioButton("Imperial (lb, ft/in)")
        self.metric_radio.setChecked(True)
        self.imperial_radio.toggled.connect(self.on_units_changed)
        unit_row.addWidget(self.metric_radio)
        unit_row.addWidget(self.imperial_radio)
        layout.addLayout(unit_row)

        # ---- Input form (FR-1) ----
        form = QFormLayout()
        layout.addLayout(form)

        self.sex_combo = QComboBox()
        self.sex_combo.addItem("Male", "male")
        self.sex_combo.addItem("Female", "female")
        form.addRow("Sex:", self.sex_combo)

        self.age_input = QLineEdit()
        form.addRow("Age:", self.age_input)

        # Height: page 0 = cm box, page 1 = ft + in boxes
        self.cm_input = QLineEdit()
        self.ft_input = QLineEdit()
        self.ft_input.setPlaceholderText("ft")
        self.in_input = QLineEdit()
        self.in_input.setPlaceholderText("in")
        imperial_box = QWidget()
        imperial_row = QHBoxLayout(imperial_box)
        imperial_row.setContentsMargins(0, 0, 0, 0)
        imperial_row.addWidget(self.ft_input)
        imperial_row.addWidget(self.in_input)

        self.height_stack = QStackedWidget()
        self.height_stack.addWidget(self.cm_input)
        self.height_stack.addWidget(imperial_box)
        self.height_label = QLabel("Height (cm):")
        form.addRow(self.height_label, self.height_stack)

        self.weight_input = QLineEdit()
        self.weight_label = QLabel("Weight (kg):")
        form.addRow(self.weight_label, self.weight_input)

        # Label the user sees, key the engine expects (FR-4)
        self.activity_combo = QComboBox()
        self.activity_combo.addItem("Sedentary", "sedentary")
        self.activity_combo.addItem("Lightly active", "light")
        self.activity_combo.addItem("Moderately active", "moderate")
        self.activity_combo.addItem("Very active", "active")
        self.activity_combo.addItem("Extra active", "very_active")
        self.activity_combo.setToolTip(
            "How active you are in a typical week. Used to turn your resting "
            "calorie burn (BMR) into your total daily burn (TDEE)."
        )
        form.addRow("Activity level:", self.activity_combo)

        self.goal_combo = QComboBox()
        self.goal_combo.addItem("Lose weight", "lose")
        self.goal_combo.addItem("Maintain weight", "maintain")
        self.goal_combo.addItem("Gain weight", "gain")
        form.addRow("Goal:", self.goal_combo)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Balanced", "balanced")
        self.preset_combo.addItem("Low carb", "low_carb")
        self.preset_combo.addItem("High carb", "high_carb")
        form.addRow("Macro split:", self.preset_combo)

        # ---- Buttons (FR-12) ----
        button_row = QHBoxLayout()
        self.calc_button = QPushButton("Calculate")
        self.calc_button.clicked.connect(self.on_calculate)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.on_reset)
        button_row.addWidget(self.calc_button)
        button_row.addWidget(self.reset_button)
        layout.addLayout(button_row)

        # ---- Error and result output ----
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #b00020;")
        layout.addWidget(self.error_label)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)
        layout.addStretch()

    # ---------- helpers ----------

    def read_number(self, field, name):
        text = field.text().strip()
        if not text:
            raise ValueError(f"Please enter your {name}.")
        return float(text)  # raises ValueError on things like "abc"

    def read_height_cm(self):
        if self.metric_radio.isChecked():
            return self.read_number(self.cm_input, "height")
        feet = self.read_number(self.ft_input, "height (feet)")
        inches = float(self.in_input.text() or 0)
        return engine.inches_to_cm(feet * 12 + inches)

    def read_weight_kg(self):
        weight = self.read_number(self.weight_input, "weight")
        if self.imperial_radio.isChecked():
            return engine.lb_to_kg(weight)
        return weight

    # ---------- event handlers ----------

    def on_units_changed(self, imperial):
        self.height_stack.setCurrentIndex(1 if imperial else 0)
        self.height_label.setText("Height (ft, in):" if imperial else "Height (cm):")
        self.weight_label.setText("Weight (lb):" if imperial else "Weight (kg):")

    def on_calculate(self):
        try:
            result = engine.calculate(
                sex=self.sex_combo.currentData(),
                age=int(self.read_number(self.age_input, "age")),
                height_cm=self.read_height_cm(),
                weight_kg=self.read_weight_kg(),
                activity=self.activity_combo.currentData(),
                goal=self.goal_combo.currentData(),
                ratio=engine.MACRO_PRESETS[self.preset_combo.currentData()],
            )
        except ValueError as err:
            self.error_label.setText(str(err))
            self.result_label.setText("")
            return

        self.error_label.setText("")
        # Placeholder output. Replace with your results display later.
        self.result_label.setText(
            f"Calories: {result.calories:.0f} kcal\n"
            f"Protein: {result.protein_g:.0f} g   "
            f"Carbs: {result.carbs_g:.0f} g   "
            f"Fat: {result.fat_g:.0f} g"
        )

    def on_reset(self):
        for field in (self.age_input, self.cm_input, self.ft_input,
                      self.in_input, self.weight_input):
            field.clear()
        self.sex_combo.setCurrentIndex(0)
        self.activity_combo.setCurrentIndex(0)
        self.goal_combo.setCurrentIndex(0)
        self.preset_combo.setCurrentIndex(0)
        self.error_label.setText("")
        self.result_label.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())