# Macro Calculator Application

A desktop app that calculates how many calories you should eat each day, plus how much protein, carbs, and fat that works out to, based on your stats and whether you want to lose, maintain, or gain weight..

## What it does

You enter:
- Age, sex, height, and weight (metric or imperial)
- Activity level (sedentary through extra active)
- Your goal: lose, maintain, or gain weight

And the app gives you:
- Your BMR and TDEE
- A daily calorie target for your goal
- A protein / carbs / fat breakdown in grams
- An option to export your results as a PDF

## How the math works

**BMR (Basal Metabolic Rate)** is how many calories your body burns just existing. I'm using the Mifflin-St Jeor equation:

- Men: `10 × weight(kg) + 6.25 × height(cm) − 5 × age + 5`
- Women: `10 × weight(kg) + 6.25 × height(cm) − 5 × age − 161`

**TDEE (Total Daily Energy Expenditure)** is your BMR multiplied by an activity factor, which ranges from 1.2 (sedentary) up to 1.9 (extra active).

**Goal adjustment:**
- Lose: TDEE − 500 calories (about 1 lb per week)
- Maintain: just your TDEE
- Gain: TDEE + 500 calories (about 1 lb per week)

Then the calories get split into protein, carbs, and fat by percentage. You can use a preset (balanced, high-protein, low-carb) or enter your own.

## Built with

- Python
- PyQt6 for the interface
- PyInstaller to turn it into a single `.exe`
- VS Code

## Current Progress:


