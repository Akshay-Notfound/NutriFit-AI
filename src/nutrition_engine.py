"""
NutriFit AI - Nutrition Engine
Implements deterministic, clinically validated nutritional science formulas:
- BMI & Body Composition Screening
- Mifflin-St Jeor Basal Metabolic Rate (BMR)
- Total Daily Energy Expenditure (TDEE)
- Dynamic Macro & Micronutrient Distribution
- Scaling for custom serving sizes
"""

from typing import Dict, Any, Tuple

ACTIVITY_FACTORS = {
    "Sedentary": 1.2,                # Little to no exercise, desk job
    "Lightly active": 1.375,         # Light exercise / sports 1-3 days/week
    "Moderately active": 1.55,       # Moderate exercise / sports 3-5 days/week
    "Very active": 1.725,            # Hard exercise / sports 6-7 days/week
    "Extra active": 1.9              # Very hard exercise, physical job or training 2x/day
}

GOAL_CALORIE_ADJUSTMENTS = {
    "Weight Loss": -450,             # Moderate safe caloric deficit (~0.4-0.5 kg/week)
    "Maintenance": 0,                # Energy balance
    "Weight Gain": 400               # Moderate lean surplus
}

def calculate_bmi(weight_kg: float, height_cm: float) -> Tuple[float, str, str, Tuple[float, float]]:
    """
    Calculates BMI, clinical classification, description, and healthy weight range.
    Formula: BMI = weight (kg) / (height (m))^2
    """
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0, "Unknown", "Invalid height or weight values", (0.0, 0.0)

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 2)

    # WHO BMI categories
    if bmi < 18.5:
        category = "Underweight"
        desc = "Your BMI indicates underweight. A nutrient-dense diet with caloric surplus is advised."
    elif 18.5 <= bmi < 25.0:
        category = "Normal weight"
        desc = "Your BMI is in the healthy reference range. Maintain balanced nutrient intake."
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
        desc = "Your BMI indicates overweight. A structured moderate deficit and increased activity are recommended."
    else:
        category = "Obese"
        desc = "Your BMI indicates obesity. Focus on whole foods, fiber adequacy, and medical guidance."

    # Healthy weight range (BMI 18.5 to 24.9)
    min_healthy_weight = round(18.5 * (height_m ** 2), 1)
    max_healthy_weight = round(24.9 * (height_m ** 2), 1)

    return bmi, category, desc, (min_healthy_weight, max_healthy_weight)

def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """
    Calculates Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation.
    Male:   BMR = 10 * W + 6.25 * H - 5 * A + 5
    Female: BMR = 10 * W + 6.25 * H - 5 * A - 161
    """
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    if sex.strip().capitalize() == "Male":
        bmr = base + 5.0
    else:
        bmr = base - 161.0
    return round(max(bmr, 800.0), 1)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculates Total Daily Energy Expenditure (TDEE).
    TDEE = BMR * ActivityFactor
    """
    factor = ACTIVITY_FACTORS.get(activity_level, 1.375)
    return round(bmr * factor, 1)

def calculate_daily_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str,
    activity_level: str,
    goal: str
) -> Dict[str, Any]:
    """
    Computes complete personalized nutrition targets:
    - Calories
    - Protein (g), Carbs (g), Fat (g), Saturated Fat limit (g)
    - Dietary Fiber (g), Sugar limit (g), Sodium limit (mg)
    - Calcium (mg), Iron (mg), Vitamin C (mg), Water (L)
    """
    bmi, bmi_category, bmi_desc, healthy_range = calculate_bmi(weight_kg, height_cm)
    bmr = calculate_bmr(weight_kg, height_cm, age, sex)
    tdee = calculate_tdee(bmr, activity_level)

    adjustment = GOAL_CALORIE_ADJUSTMENTS.get(goal, 0)
    target_calories = max(round(tdee + adjustment, 0), 1200.0) # Never advise under 1200 kcal without clinical supervision

    # Protein target (g per kg bodyweight)
    if goal == "Weight Gain":
        protein_g_per_kg = 2.0
    elif goal == "Weight Loss":
        protein_g_per_kg = 1.6 # Preserve lean muscle mass during deficit
    else:
        protein_g_per_kg = 1.3 # Maintenance

    target_protein_g = round(weight_kg * protein_g_per_kg, 1)
    protein_calories = target_protein_g * 4.0

    # Dietary Fat target: 25% - 28% of total daily energy
    fat_calories = target_calories * 0.27
    target_fat_g = round(fat_calories / 9.0, 1)
    target_sat_fat_limit_g = round((target_calories * 0.08) / 9.0, 1) # <8% of calories from sat fat

    # Carbohydrates target: Remaining calories
    carb_calories = max(target_calories - protein_calories - fat_calories, 0.0)
    target_carbs_g = round(carb_calories / 4.0, 1)

    # Dietary Fiber: WHO recommends min 25-30g / day, or 14g per 1000 kcal
    target_fiber_g = round(max(25.0, (target_calories / 1000.0) * 14.0), 1)

    # Added Sugar limit: WHO recommends < 5-10% of total calories
    sugar_limit_g = round((target_calories * 0.07) / 4.0, 1)

    # Sodium limit: WHO guideline < 2000 mg/day
    sodium_limit_mg = 2000.0

    # Micronutrients RDA (adult standards)
    calcium_mg = 1000.0
    iron_mg = 18.0 if sex.lower() == 'female' else 10.0
    vitamin_c_mg = 75.0 if sex.lower() == 'female' else 90.0
    water_liters = round((weight_kg * 0.035), 1) # ~35ml per kg

    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmi_desc": bmi_desc,
        "healthy_weight_range": healthy_range,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_calories,
        "target_protein_g": target_protein_g,
        "target_carbs_g": target_carbs_g,
        "target_fat_g": target_fat_g,
        "target_sat_fat_limit_g": target_sat_fat_limit_g,
        "target_fiber_g": target_fiber_g,
        "sugar_limit_g": sugar_limit_g,
        "sodium_limit_mg": sodium_limit_mg,
        "target_calcium_mg": calcium_mg,
        "target_iron_mg": iron_mg,
        "target_vitamin_c_mg": vitamin_c_mg,
        "target_water_l": water_liters
    }

def scale_nutrition_for_serving(nutrients_100g: Dict[str, float], serving_quantity: float) -> Dict[str, float]:
    """
    Given nutrients per 100g and a serving quantity in grams or ml,
    calculates exact scaled nutritional values.
    """
    factor = serving_quantity / 100.0
    return {
        k: round(v * factor, 2) if isinstance(v, (int, float)) else v
        for k, v in nutrients_100g.items()
    }

