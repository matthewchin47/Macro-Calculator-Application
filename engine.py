"""Calculation engine for the Macro Calculator.

Pure Python with no GUI dependencies, so it can be unit-tested on its own
and called from the Tkinter layer.
"""

from dataclasses import dataclass

KCAL_PER_GRAM = {"protein": 4, "carbs": 4, "fat": 9}

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,        # little or no exercise
    "light": 1.375,          # 1-3 days/week
    "moderate": 1.55,        # 3-5 days/week
    "active": 1.725,         # 6-7 days/week
    "very_active": 1.9,      # hard exercise or physical job
}

GOAL_ADJUSTMENTS = {
    "lose": -500,
    "maintain": 0,
    "gain": 500,
}

# Fractions of total calories: (protein, carbs, fat)
MACRO_PRESETS = {
    "balanced": (0.30, 0.40, 0.30),
    "low_carb": (0.40, 0.20, 0.40),
    "high_carb": (0.25, 0.55, 0.20),
}

LB_PER_KG = 2.20462
CM_PER_INCH = 2.54


@dataclass
class Results:
    bmr: float
    tdee: float
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


def lb_to_kg(lb: float) -> float:
    return lb / LB_PER_KG


def inches_to_cm(inches: float) -> float:
    return inches * CM_PER_INCH


def validate_inputs(sex: str, age: int, height_cm: float, weight_kg: float,
                    activity: str, goal: str) -> None:
    """Raise ValueError with a user-facing message if any input is invalid."""
    if sex not in ("male", "female"):
        raise ValueError("Sex must be 'male' or 'female'.")
    if not 15 <= age <= 100:
        raise ValueError("Age must be between 15 and 100.")
    if not 100 <= height_cm <= 250:
        raise ValueError("Height must be between 100 and 250 cm.")
    if not 30 <= weight_kg <= 300:
        raise ValueError("Weight must be between 30 and 300 kg.")
    if activity not in ACTIVITY_MULTIPLIERS:
        raise ValueError(f"Unknown activity level: {activity}")
    if goal not in GOAL_ADJUSTMENTS:
        raise ValueError(f"Unknown goal: {goal}")


def calculate_bmr(sex: str, age: int, height_cm: float, weight_kg: float) -> float:
    """Basal metabolic rate using the Mifflin-St Jeor equation."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == "male" else base - 161


def calculate_tdee(bmr: float, activity: str) -> float:
    return bmr * ACTIVITY_MULTIPLIERS[activity]


def calculate_target_calories(tdee: float, goal: str) -> float:
    return tdee + GOAL_ADJUSTMENTS[goal]


def calculate_macros(calories: float, ratio: tuple[float, float, float]) -> tuple[float, float, float]:
    """Split calories into grams of (protein, carbs, fat) given a ratio that sums to 1."""
    if abs(sum(ratio) - 1.0) > 0.001:
        raise ValueError("Macro percentages must add up to 100%.")
    protein, carbs, fat = ratio
    return (
        calories * protein / KCAL_PER_GRAM["protein"],
        calories * carbs / KCAL_PER_GRAM["carbs"],
        calories * fat / KCAL_PER_GRAM["fat"],
    )


def calculate(sex: str, age: int, height_cm: float, weight_kg: float,
              activity: str, goal: str,
              ratio: tuple[float, float, float] = MACRO_PRESETS["balanced"]) -> Results:
    """Run the full pipeline: validate -> BMR -> TDEE -> target calories -> macros."""
    validate_inputs(sex, age, height_cm, weight_kg, activity, goal)
    bmr = calculate_bmr(sex, age, height_cm, weight_kg)
    tdee = calculate_tdee(bmr, activity)
    calories = calculate_target_calories(tdee, goal)
    protein_g, carbs_g, fat_g = calculate_macros(calories, ratio)
    return Results(bmr, tdee, calories, protein_g, carbs_g, fat_g)


if __name__ == "__main__":
    r = calculate("male", 25, 178, 75, "moderate", "maintain")
    print(f"BMR:      {r.bmr:.0f} kcal")
    print(f"TDEE:     {r.tdee:.0f} kcal")
    print(f"Target:   {r.calories:.0f} kcal")
    print(f"Protein:  {r.protein_g:.0f} g")
    print(f"Carbs:    {r.carbs_g:.0f} g")
    print(f"Fat:      {r.fat_g:.0f} g")
