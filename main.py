import sys

from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QFrame, QStackedWidget,
    QButtonGroup,
)

import engine
import theme
from goals import GoalsPage
from widgets import make_card, field_label, StatTile, MacroBar

DISCLAIMER = (
    "Estimates only, based on the Mifflin-St Jeor formula. This is not medical "
    "advice. Talk to a doctor or registered dietitian before making major diet "
    "changes, especially if you have a health condition."
)


class CalculatorPage(QWidget):
    def __init__(self, on_calculated, on_units_changed):
        super().__init__()
        self.setObjectName("page")
        self.on_calculated = on_calculated    # callback(profile dict)
        self.units_changed_cb = on_units_changed  # callback(imperial bool)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 12)
        outer.setSpacing(18)

        title = QLabel("Calculator")
        title.setObjectName("title")
        subtitle = QLabel("Your daily calories and macros, calculated privately on your device.")
        subtitle.setObjectName("subtitle")
        outer.addWidget(title)
        outer.addWidget(subtitle)

        body = QHBoxLayout()
        body.setSpacing(20)
        outer.addLayout(body, 1)
        body.addWidget(self.build_form_card(), 5)
        body.addWidget(self.build_results_card(), 6)

        # Pressing Enter in any text field calculates
        for field in (self.age_input, self.cm_input, self.ft_input,
                      self.in_input, self.weight_input):
            field.returnPressed.connect(self.on_calculate)

    # ---------- layout builders ----------

    def build_form_card(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        heading = QLabel("About you")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)

        # Segmented unit toggle (FR-2)
        bar = QFrame()
        bar.setObjectName("segmentBar")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(3, 3, 3, 3)
        bar_layout.setSpacing(3)
        self.metric_btn = QPushButton("Metric (kg, cm)")
        self.imperial_btn = QPushButton("Imperial (lb, ft/in)")
        group = QButtonGroup(self)
        for btn in (self.metric_btn, self.imperial_btn):
            btn.setObjectName("segment")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            group.addButton(btn)
            bar_layout.addWidget(btn)
        self.metric_btn.setChecked(True)
        self.imperial_btn.toggled.connect(self.on_units_changed)
        layout.addWidget(bar)

        # Input grid (FR-1)
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        layout.addLayout(grid)

        self.sex_combo = QComboBox()
        self.sex_combo.addItem("Male", "male")
        self.sex_combo.addItem("Female", "female")
        grid.addWidget(field_label("SEX"), 0, 0)
        grid.addWidget(self.sex_combo, 1, 0)

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("e.g. 25")
        grid.addWidget(field_label("AGE"), 0, 1)
        grid.addWidget(self.age_input, 1, 1)

        # Height: page 0 = cm box, page 1 = ft + in boxes
        self.cm_input = QLineEdit()
        self.cm_input.setPlaceholderText("e.g. 178")
        self.ft_input = QLineEdit()
        self.ft_input.setPlaceholderText("ft")
        self.in_input = QLineEdit()
        self.in_input.setPlaceholderText("in")
        imperial_box = QWidget()
        imperial_row = QHBoxLayout(imperial_box)
        imperial_row.setContentsMargins(0, 0, 0, 0)
        imperial_row.setSpacing(8)
        imperial_row.addWidget(self.ft_input)
        imperial_row.addWidget(self.in_input)
        self.height_stack = QStackedWidget()
        self.height_stack.addWidget(self.cm_input)
        self.height_stack.addWidget(imperial_box)
        self.height_label = field_label("HEIGHT (CM)")
        grid.addWidget(self.height_label, 2, 0)
        grid.addWidget(self.height_stack, 3, 0)

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("e.g. 75")
        self.weight_label = field_label("WEIGHT (KG)")
        grid.addWidget(self.weight_label, 2, 1)
        grid.addWidget(self.weight_input, 3, 1)

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
        grid.addWidget(field_label("ACTIVITY LEVEL"), 4, 0, 1, 2)
        grid.addWidget(self.activity_combo, 5, 0, 1, 2)

        self.goal_combo = QComboBox()
        self.goal_combo.addItem("Lose weight", "lose")
        self.goal_combo.addItem("Maintain weight", "maintain")
        self.goal_combo.addItem("Gain weight", "gain")
        grid.addWidget(field_label("GOAL"), 6, 0)
        grid.addWidget(self.goal_combo, 7, 0)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Balanced", "balanced")
        self.preset_combo.addItem("Low carb", "low_carb")
        self.preset_combo.addItem("High carb", "high_carb")
        grid.addWidget(field_label("MACRO SPLIT"), 6, 1)
        grid.addWidget(self.preset_combo, 7, 1)

        layout.addStretch()

        self.error_label = QLabel("")
        self.error_label.setObjectName("error")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        # Buttons (FR-12)
        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        self.calc_button = QPushButton("Calculate")
        self.calc_button.setObjectName("primary")
        self.calc_button.setCursor(Qt.PointingHandCursor)
        self.calc_button.clicked.connect(self.on_calculate)
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("secondary")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.clicked.connect(self.on_reset)
        button_row.addWidget(self.calc_button, 2)
        button_row.addWidget(self.reset_button, 1)
        layout.addLayout(button_row)
        return card

    def build_results_card(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        heading = QLabel("Your daily targets")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)

        self.results_stack = QStackedWidget()
        layout.addWidget(self.results_stack, 1)

        # Page 0: empty state
        empty = QLabel("Fill in your details and press Calculate\nto see your personalized targets.")
        empty.setObjectName("placeholder")
        empty.setAlignment(Qt.AlignCenter)
        self.results_stack.addWidget(empty)

        # Page 1: dashboard
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(16)

        self.cal_tile = StatTile("Calories", "kcal per day", "accent")
        page_layout.addWidget(self.cal_tile)

        row = QHBoxLayout()
        row.setSpacing(12)
        self.protein_tile = StatTile("Protein", "grams", "protein")
        self.carbs_tile = StatTile("Carbs", "grams", "carbs")
        self.fat_tile = StatTile("Fat", "grams", "fat")
        for tile in (self.protein_tile, self.carbs_tile, self.fat_tile):
            row.addWidget(tile)
        page_layout.addLayout(row)

        self.macro_bar = MacroBar()
        page_layout.addWidget(self.macro_bar)
        self.split_label = QLabel("")
        self.split_label.setObjectName("subtitle")
        page_layout.addWidget(self.split_label)

        self.detail_label = QLabel("")
        self.detail_label.setObjectName("subtitle")
        self.detail_label.setWordWrap(True)
        page_layout.addWidget(self.detail_label)
        page_layout.addStretch()

        self.results_stack.addWidget(page)
        return card

    # ---------- helpers ----------

    def is_imperial(self):
        return self.imperial_btn.isChecked()

    def read_number(self, field, name):
        text = field.text().strip()
        if not text:
            raise ValueError(f"Please enter your {name}.")
        try:
            return float(text)
        except ValueError:
            raise ValueError(f"Your {name} must be a number.") from None

    def read_height_cm(self):
        if not self.is_imperial():
            return self.read_number(self.cm_input, "height")
        feet = self.read_number(self.ft_input, "height (feet)")
        inches = float(self.in_input.text() or 0)
        return engine.inches_to_cm(feet * 12 + inches)

    def read_weight_kg(self):
        weight = self.read_number(self.weight_input, "weight")
        return engine.lb_to_kg(weight) if self.is_imperial() else weight

    # ---------- event handlers ----------

    def on_units_changed(self, imperial):
        self.height_stack.setCurrentIndex(1 if imperial else 0)
        self.height_label.setText("HEIGHT (FT, IN)" if imperial else "HEIGHT (CM)")
        self.weight_label.setText("WEIGHT (LB)" if imperial else "WEIGHT (KG)")
        self.weight_input.setPlaceholderText("e.g. 165" if imperial else "e.g. 75")
        self.units_changed_cb(imperial)

    def on_calculate(self):
        ratio = engine.MACRO_PRESETS[self.preset_combo.currentData()]
        try:
            age = int(self.read_number(self.age_input, "age"))
            height_cm = self.read_height_cm()
            weight_kg = self.read_weight_kg()
            sex = self.sex_combo.currentData()
            activity = self.activity_combo.currentData()
            result = engine.calculate(
                sex=sex, age=age, height_cm=height_cm, weight_kg=weight_kg,
                activity=activity, goal=self.goal_combo.currentData(), ratio=ratio,
            )
        except ValueError as err:
            self.error_label.setText(str(err))
            self.results_stack.setCurrentIndex(0)
            return

        self.error_label.setText("")
        self.cal_tile.set_value(f"{result.calories:,.0f}")
        self.protein_tile.set_value(f"{result.protein_g:.0f} g")
        self.carbs_tile.set_value(f"{result.carbs_g:.0f} g")
        self.fat_tile.set_value(f"{result.fat_g:.0f} g")
        self.macro_bar.set_ratio(ratio)
        self.split_label.setText(
            f"Split: {ratio[0]:.0%} protein  ·  {ratio[1]:.0%} carbs  ·  {ratio[2]:.0%} fat"
        )
        self.detail_label.setText(
            f"Resting burn (BMR): {result.bmr:,.0f} kcal    "
            f"Daily burn (TDEE): {result.tdee:,.0f} kcal"
        )
        self.results_stack.setCurrentIndex(1)

        self.on_calculated({
            "sex": sex, "age": age, "height_cm": height_cm,
            "weight_kg": weight_kg, "activity": activity,
        })

    def on_reset(self):
        for field in (self.age_input, self.cm_input, self.ft_input,
                      self.in_input, self.weight_input):
            field.clear()
        self.sex_combo.setCurrentIndex(0)
        self.activity_combo.setCurrentIndex(0)
        self.goal_combo.setCurrentIndex(0)
        self.preset_combo.setCurrentIndex(0)
        self.error_label.setText("")
        self.results_stack.setCurrentIndex(0)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle("Macro Calculator")
        self.resize(1080, 700)
        self.setMinimumSize(980, 640)
        self.settings = QSettings("MacroCalculator", "MacroCalculator")

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self.build_sidebar())

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        root.addLayout(content, 1)

        self.goals_page = GoalsPage()
        self.calc_page = CalculatorPage(
            on_calculated=self.goals_page.set_profile,
            on_units_changed=self.goals_page.set_imperial,
        )
        self.pages = QStackedWidget()
        self.pages.addWidget(self.calc_page)
        self.pages.addWidget(self.goals_page)
        content.addWidget(self.pages, 1)

        disclaimer = QLabel(DISCLAIMER)
        disclaimer.setObjectName("disclaimer")
        disclaimer.setWordWrap(True)
        disclaimer.setContentsMargins(28, 0, 28, 14)
        content.addWidget(disclaimer)

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 22, 14, 18)
        layout.setSpacing(6)

        brand = QLabel("Macro Calculator")
        brand.setObjectName("brand")
        brand.setContentsMargins(6, 0, 0, 14)
        layout.addWidget(brand)

        group = QButtonGroup(self)
        for index, label in enumerate(("Calculator", "Goals")):
            btn = QPushButton(label)
            btn.setObjectName("nav")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setChecked(index == 0)
            btn.clicked.connect(lambda _checked, i=index: self.pages.setCurrentIndex(i))
            group.addButton(btn)
            layout.addWidget(btn)

        layout.addStretch()

        self.theme_button = QPushButton("")
        self.theme_button.setObjectName("secondary")
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)
        return sidebar

    def apply_theme(self, name):
        theme.set_theme(name)
        QApplication.instance().setStyleSheet(theme.stylesheet())
        self.theme_button.setText("Switch to light mode" if name == "dark" else "Switch to dark mode")
        self.calc_page.macro_bar.update()
        self.goals_page.chart.update()

    def toggle_theme(self):
        name = "light" if theme.name == "dark" else "dark"
        self.apply_theme(name)
        self.settings.setValue("theme", name)  # remembered for next launch


def initial_theme(app, settings):
    saved = settings.value("theme")
    if saved in ("light", "dark"):
        return saved
    try:
        if app.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            return "dark"
    except AttributeError:
        pass
    return "light"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.apply_theme(initial_theme(app, window.settings))
    window.show()
    sys.exit(app.exec())
