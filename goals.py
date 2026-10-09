"""Goals page: projects weight over time toward a target."""

from datetime import date, timedelta

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QPushButton,
    QLabel, QStackedWidget,
)

import engine
from widgets import make_card, field_label, StatTile, ProjectionChart


class GoalsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("page")
        self.profile = None   # set by the calculator page after a successful calculation
        self.imperial = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 12)
        outer.setSpacing(18)

        title = QLabel("Goals")
        title.setObjectName("title")
        subtitle = QLabel("See how long it could take to reach your target weight.")
        subtitle.setObjectName("subtitle")
        outer.addWidget(title)
        outer.addWidget(subtitle)

        body = QHBoxLayout()
        body.setSpacing(20)
        outer.addLayout(body, 1)
        body.addWidget(self.build_form_card(), 4)
        body.addWidget(self.build_results_card(), 7)

    # ---------- layout builders ----------

    def build_form_card(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(10)

        heading = QLabel("Set your goal")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)

        self.current_label = QLabel("")
        self.current_label.setObjectName("subtitle")
        layout.addWidget(self.current_label)

        self.target_label = field_label("TARGET WEIGHT (KG)")
        layout.addWidget(self.target_label)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("e.g. 70")
        self.target_input.returnPressed.connect(self.on_update)
        layout.addWidget(self.target_input)

        layout.addWidget(field_label("PACE"))
        self.pace_combo = QComboBox()
        self.pace_combo.addItem("Gentle  (250 kcal/day)", 250)
        self.pace_combo.addItem("Standard  (500 kcal/day)", 500)
        self.pace_combo.addItem("Fast  (750 kcal/day)", 750)
        self.pace_combo.setCurrentIndex(1)
        self.pace_combo.setToolTip(
            "How far above or below your daily burn (TDEE) you eat. "
            "Faster paces are harder to sustain."
        )
        self.pace_combo.currentIndexChanged.connect(self.on_update)
        layout.addWidget(self.pace_combo)

        layout.addStretch()

        self.error_label = QLabel("")
        self.error_label.setObjectName("error")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        self.warn_label = QLabel("")
        self.warn_label.setObjectName("warning")
        self.warn_label.setWordWrap(True)
        layout.addWidget(self.warn_label)

        self.update_button = QPushButton("Project timeline")
        self.update_button.setObjectName("primary")
        self.update_button.setCursor(Qt.PointingHandCursor)
        self.update_button.clicked.connect(self.on_update)
        layout.addWidget(self.update_button)
        return card

    def build_results_card(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        heading = QLabel("Projected timeline")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self.empty_label = QLabel("")
        self.empty_label.setObjectName("placeholder")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.empty_label)

        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(14)

        row = QHBoxLayout()
        row.setSpacing(12)
        self.time_tile = StatTile("Time to goal", "", "accent")
        self.date_tile = StatTile("Target date", "estimated", "protein")
        self.rate_tile = StatTile("Weekly change", "at the start", "carbs")
        self.cal_tile = StatTile("Daily calories", "kcal to eat", "fat")
        for tile in (self.time_tile, self.date_tile, self.rate_tile, self.cal_tile):
            tile.value_label.setStyleSheet("font-size: 20px;")
            row.addWidget(tile)
        page_layout.addLayout(row)

        self.chart = ProjectionChart()
        page_layout.addWidget(self.chart, 1)

        self.note_label = QLabel("")
        self.note_label.setObjectName("subtitle")
        self.note_label.setWordWrap(True)
        page_layout.addWidget(self.note_label)

        self.stack.addWidget(page)
        self._show_empty()
        return card

    # ---------- public API (called by the main window) ----------

    def set_profile(self, profile):
        """Receive the latest calculator inputs/results; refresh if a goal is set."""
        self.profile = profile
        self._refresh_current_label()
        if self.target_input.text().strip():
            self.on_update()
        else:
            self._show_empty()

    def set_imperial(self, imperial):
        if imperial == self.imperial:
            return
        text = self.target_input.text().strip()
        self.imperial = imperial
        self.target_label.setText("TARGET WEIGHT (LB)" if imperial else "TARGET WEIGHT (KG)")
        self.target_input.setPlaceholderText("e.g. 155" if imperial else "e.g. 70")
        try:
            value = float(text)
            value = value * engine.LB_PER_KG if imperial else value / engine.LB_PER_KG
            self.target_input.setText(f"{value:.1f}")
        except ValueError:
            pass
        self._refresh_current_label()
        if self.profile and self.target_input.text().strip():
            self.on_update()

    # ---------- internals ----------

    def _fmt_weight(self, kg):
        if self.imperial:
            return f"{kg * engine.LB_PER_KG:.1f} lb"
        return f"{kg:.1f} kg"

    def _refresh_current_label(self):
        if self.profile:
            self.current_label.setText(
                f"Current weight: {self._fmt_weight(self.profile['weight_kg'])}"
            )
        else:
            self.current_label.setText("Current weight: not set")

    def _show_empty(self):
        if self.profile:
            self.empty_label.setText("Enter a target weight and press\nProject timeline.")
        else:
            self.empty_label.setText("Run a calculation on the Calculator page first,\nthen come back to set a goal.")
        self.stack.setCurrentIndex(0)

    def _fmt_duration(self, weeks):
        days = round(weeks * 7)
        if days < 14:
            return f"{days} days"
        if weeks < 16:
            return f"{weeks:.0f} weeks"
        return f"{weeks / 4.345:.1f} months"

    def on_update(self):
        self.error_label.setText("")
        self.warn_label.setText("")
        if not self.profile:
            self._show_empty()
            return

        text = self.target_input.text().strip()
        if not text:
            self.error_label.setText("Please enter your target weight.")
            self._show_empty()
            return
        try:
            target = float(text)
            target_kg = engine.lb_to_kg(target) if self.imperial else target
            p = self.profile
            proj = engine.project_weight(
                p["sex"], p["age"], p["height_cm"], p["weight_kg"], p["activity"],
                target_kg, self.pace_combo.currentData(),
            )
        except ValueError as err:
            msg = str(err)
            if msg.startswith("could not convert"):
                msg = "Your target weight must be a number."
            self.error_label.setText(msg)
            self._show_empty()
            return

        # Safety note if the plan dips below commonly suggested calorie floors
        floor = engine.MIN_CALORIES[self.profile["sex"]]
        if proj.intake < floor:
            self.warn_label.setText(
                f"This pace means about {proj.intake:,.0f} kcal/day, below the "
                f"commonly suggested minimum of {floor:,}. Consider a gentler pace."
            )

        total_weeks = proj.points[-1][0]
        weekly = proj.weekly_change_kg
        if self.imperial:
            weekly_text = f"{weekly * engine.LB_PER_KG:+.1f} lb"
        else:
            weekly_text = f"{weekly:+.2f} kg"

        self.cal_tile.set_value(f"{proj.intake:,.0f}")
        self.rate_tile.set_value(weekly_text)
        if proj.reached:
            when = date.today() + timedelta(weeks=total_weeks)
            self.time_tile.set_value(self._fmt_duration(total_weeks), f"to reach {self._fmt_weight(target_kg)}")
            self.date_tile.set_value(f"{when:%b} {when.day}, {when.year}")
            self.note_label.setText(
                "Progress slows slightly over time because a lighter body burns "
                "fewer calories. Real results vary; treat this as a rough guide."
            )
        else:
            self.time_tile.set_value("3+ years", "target not reached")
            self.date_tile.set_value("--")
            self.note_label.setText(
                "At this pace your weight levels off before reaching the target. "
                "Try a faster pace or a closer target."
            )

        self.chart.set_data(proj.points, target_kg, self.imperial)
        self.stack.setCurrentIndex(1)
