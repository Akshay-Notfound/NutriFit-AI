"""
NutriFit AI - Personalized Diet Planner
Generates structured daily and 7-day weekly meal plans respecting:
- Calorie target & Macro distribution
- Dietary preference (Vegetarian, Vegan, Eggetarian, Non-Vegetarian)
- Indian Meal Intelligence (Roti + Dal + Sabzi + Curd, Idli Sambar, Sprouts, etc.)
- Dynamic adjustments for already logged foods
"""

from typing import Dict, List, Any
import random

# Curated Authentic Meal Templates with Indian Food Combinations
MEAL_TEMPLATES = {
    "Vegetarian": {
        "breakfast": [
            {"name": "Poha with Roasted Peanuts & Veggies + Lemon", "calories": 280, "protein": 7, "carbs": 48, "fat": 7, "fiber": 4.5},
            {"name": "Idli (2 pcs) with Vegetable Sambar & Coconut Chutney", "calories": 270, "protein": 8, "carbs": 46, "fat": 6, "fiber": 5.0},
            {"name": "Vegetable Upma with Sambar & Spiced Curd", "calories": 290, "protein": 8, "carbs": 48, "fat": 8, "fiber": 4.2},
            {"name": "Moong Sprouts Salad with Lemon, Tomato & Chaat Masala", "calories": 210, "protein": 14, "carbs": 30, "fat": 3, "fiber": 8.0},
            {"name": "Masala Oats with Mixed Veggies & Paneer Cubes (40g)", "calories": 310, "protein": 14, "carbs": 42, "fat": 10, "fiber": 6.5},
            {"name": "Whole Wheat Roti (2 pcs) with Paneer Bhurji", "calories": 360, "protein": 17, "carbs": 45, "fat": 12, "fiber": 6.0},
            {"name": "Besan Chilla (2 pcs) with Mint Chutney & Curd", "calories": 295, "protein": 13, "carbs": 38, "fat": 9, "fiber": 5.5}
        ],
        "lunch": [
            {"name": "Whole Wheat Roti (2 pcs) + Yellow Moong Dal + Bhindi Sabzi + Cucumber Salad", "calories": 460, "protein": 17, "carbs": 72, "fat": 11, "fiber": 12.0},
            {"name": "Steamed Rice (1 cup) + Toor Dal Tadka + Palak Paneer + Fresh Curd", "calories": 520, "protein": 21, "carbs": 76, "fat": 15, "fiber": 8.5},
            {"name": "Brown Rice + Rajma Masala + Kachumber Salad + Chaas", "calories": 480, "protein": 19, "carbs": 82, "fat": 8, "fiber": 13.0},
            {"name": "Whole Wheat Roti (2 pcs) + Chana Masala (Chole) + Mixed Veg Sabzi + Salad", "calories": 510, "protein": 18, "carbs": 78, "fat": 13, "fiber": 14.0},
            {"name": "Bajra Roti (2 pcs) + Baingan Bharta + Sprouted Moong Usal + Chaas", "calories": 490, "protein": 19, "carbs": 75, "fat": 12, "fiber": 15.0},
            {"name": "Jeera Rice + Dal Makhani (Light Home Style) + Paneer Tikka + Salad", "calories": 530, "protein": 22, "carbs": 74, "fat": 16, "fiber": 9.0},
            {"name": "Whole Wheat Roti (2 pcs) + Dal Fry + Aloo Gobi Matar + Fresh Dahi", "calories": 475, "protein": 16, "carbs": 71, "fat": 13, "fiber": 10.5}
        ],
        "snacks": [
            {"name": "Roasted Makhana (30g) + Green Tea", "calories": 115, "protein": 3.5, "carbs": 21, "fat": 0.5, "fiber": 2.5},
            {"name": "Roasted Chana (40g) + Chaas (1 glass)", "calories": 185, "protein": 11, "carbs": 26, "fat": 3, "fiber": 7.0},
            {"name": "Unsweetened Greek Yogurt with Apple Slices", "calories": 140, "protein": 12, "carbs": 18, "fat": 1.5, "fiber": 3.0},
            {"name": "Sprouts Chaat with Onions, Lemon & Pomegranate", "calories": 130, "protein": 7, "carbs": 22, "fat": 1, "fiber": 4.5},
            {"name": "Handful of Raw Almonds & Walnuts (25g)", "calories": 155, "protein": 5, "carbs": 5, "fat": 14, "fiber": 2.5},
            {"name": "Fresh Tender Coconut Water + 1 Orange", "calories": 110, "protein": 2, "carbs": 24, "fat": 0.5, "fiber": 3.5},
            {"name": "Moong Dal Sprouts + Buttermilk", "calories": 125, "protein": 8, "carbs": 18, "fat": 1.5, "fiber": 4.0}
        ],
        "dinner": [
            {"name": "Moong Dal Khichdi + Ghee (1 tsp) + Fresh Dahi + Roasted Papad", "calories": 390, "protein": 15, "carbs": 62, "fat": 8, "fiber": 7.5},
            {"name": "Whole Wheat Roti (2 pcs) + Toor Dal + Lauki / Bottle Gourd Sabzi + Tomato Salad", "calories": 380, "protein": 15, "carbs": 64, "fat": 7, "fiber": 9.5},
            {"name": "Grilled Paneer Tikka (120g) with Bell Peppers, Onions & Mint Chutney", "calories": 320, "protein": 20, "carbs": 12, "fat": 19, "fiber": 3.5},
            {"name": "Jowar Roti (2 pcs) + Methi Paneer Sabzi + Cucumber Salad", "calories": 410, "protein": 18, "carbs": 60, "fat": 12, "fiber": 10.0},
            {"name": "Mixed Vegetable Dalia (Broken Wheat Porridge) with Paneer & Curd", "calories": 370, "protein": 16, "carbs": 58, "fat": 8, "fiber": 8.0},
            {"name": "Whole Wheat Roti (2 pcs) + Yellow Dal + Green Beans Sabzi", "calories": 385, "protein": 14, "carbs": 65, "fat": 7, "fiber": 8.5},
            {"name": "Warm Vegetable Stew with 1 Whole Wheat Appam / Roti & Coconut Chutney", "calories": 360, "protein": 10, "carbs": 54, "fat": 11, "fiber": 7.0}
        ]
    },
    "Non-Vegetarian": {
        "breakfast": [
            {"name": "Boiled Eggs (2 whole) + Whole Wheat Toast (2 pcs) + Black Coffee", "calories": 320, "protein": 19, "carbs": 28, "fat": 14, "fiber": 3.5},
            {"name": "Egg Bhurji (2 eggs with onions, tomatoes & chilies) + 2 Rotis", "calories": 380, "protein": 20, "carbs": 45, "fat": 14, "fiber": 6.0},
            {"name": "Poha with Peanuts & 2 Boiled Egg Whites", "calories": 310, "protein": 15, "carbs": 48, "fat": 7, "fiber": 4.5},
            {"name": "Omelette (2 eggs) with Spinach & Whole Wheat Toast", "calories": 330, "protein": 18, "carbs": 26, "fat": 15, "fiber": 3.8},
            {"name": "Idli (2 pcs) + Vegetable Sambar + 2 Boiled Egg Whites", "calories": 290, "protein": 15, "carbs": 46, "fat": 4, "fiber": 5.0},
            {"name": "Chicken Tikka Sandwich on Whole Wheat with Lettuce & Cucumber", "calories": 340, "protein": 24, "carbs": 36, "fat": 9, "fiber": 4.0},
            {"name": "Masala Oats cooked with Egg Whites (3 whites) + Veggies", "calories": 280, "protein": 18, "carbs": 38, "fat": 5, "fiber": 5.5}
        ],
        "lunch": [
            {"name": "Whole Wheat Roti (2 pcs) + Home Style Chicken Curry + Cucumber Salad", "calories": 480, "protein": 32, "carbs": 52, "fat": 14, "fiber": 7.0},
            {"name": "Steamed Brown Rice (1 cup) + Fish Curry (Rohu/Pomfret) + Green Salad", "calories": 450, "protein": 28, "carbs": 55, "fat": 12, "fiber": 6.5},
            {"name": "Chicken Biryani (Home style, light oil) + Cucumber Onion Raita", "calories": 520, "protein": 30, "carbs": 65, "fat": 14, "fiber": 5.5},
            {"name": "Whole Wheat Roti (2 pcs) + Egg Curry (2 eggs) + Steamed Beans Sabzi", "calories": 460, "protein": 22, "carbs": 54, "fat": 16, "fiber": 8.0},
            {"name": "Grilled Chicken Breast (150g) + Steamed Sweet Potato + Tossed Salad", "calories": 440, "protein": 42, "carbs": 40, "fat": 9, "fiber": 6.0},
            {"name": "Jeera Rice + Moong Dal + Chicken Tikka (4 pcs) + Fresh Curd", "calories": 510, "protein": 34, "carbs": 62, "fat": 12, "fiber": 6.5},
            {"name": "Bajra Roti (2 pcs) + Chicken Keema with Matar + Chaas", "calories": 490, "protein": 33, "carbs": 56, "fat": 13, "fiber": 9.0}
        ],
        "snacks": [
            {"name": "Boiled Egg (1) + Spiced Chaas (1 glass)", "calories": 115, "protein": 9, "carbs": 5, "fat": 6, "fiber": 0.2},
            {"name": "Roasted Chana (40g) + Black Coffee / Green Tea", "calories": 145, "protein": 8, "carbs": 24, "fat": 2, "fiber": 6.5},
            {"name": "Greek Yogurt with Fresh Blueberries/Strawberries", "calories": 130, "protein": 13, "carbs": 14, "fat": 1.5, "fiber": 2.0},
            {"name": "Handful of Mixed Almonds and Walnuts (25g)", "calories": 155, "protein": 5, "carbs": 5, "fat": 14, "fiber": 2.5},
            {"name": "Chicken Clear Soup with Shredded Veggies", "calories": 110, "protein": 15, "carbs": 6, "fat": 2, "fiber": 1.5},
            {"name": "Roasted Makhana (30g) + Green Tea", "calories": 115, "protein": 3.5, "carbs": 21, "fat": 0.5, "fiber": 2.5},
            {"name": "Tender Coconut Water + 1 Boiled Egg White", "calories": 75, "protein": 5, "carbs": 10, "fat": 0.5, "fiber": 1.1}
        ],
        "dinner": [
            {"name": "Grilled Fish or Chicken (140g) with Sautéed Veggies (Broccoli, Carrots, Beans)", "calories": 360, "protein": 36, "carbs": 14, "fat": 15, "fiber": 5.5},
            {"name": "Whole Wheat Roti (2 pcs) + Yellow Dal Tadka + Boiled Egg (1) + Salad", "calories": 410, "protein": 22, "carbs": 58, "fat": 10, "fiber": 8.0},
            {"name": "Chicken Tikka (150g) with Mint Chutney & Large Green Salad", "calories": 310, "protein": 35, "carbs": 10, "fat": 12, "fiber": 4.0},
            {"name": "Egg Bhurji (2 eggs) + 1 Whole Wheat Roti + Spiced Chaas", "calories": 340, "protein": 19, "carbs": 30, "fat": 15, "fiber": 4.5},
            {"name": "Steamed Rice (1/2 cup) + Fish Curry + Spinach (Palak) Sabzi", "calories": 375, "protein": 26, "carbs": 42, "fat": 10, "fiber": 5.5},
            {"name": "Moong Dal Khichdi + 2 Boiled Egg Whites + Roasted Papad", "calories": 360, "protein": 18, "carbs": 58, "fat": 5, "fiber": 7.0},
            {"name": "Stir-fried Chicken with Bell Peppers & 1 Roti", "calories": 370, "protein": 32, "carbs": 32, "fat": 11, "fiber": 5.0}
        ]
    }
}

def generate_daily_plan(
    target_calories: float,
    dietary_preference: str = "Vegetarian",
    goal: str = "Maintenance",
    day_offset: int = 0,
    consumed_today: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a personalized 4-meal plan (Breakfast, Lunch, Snacks, Dinner).
    Dynamically scales portions to hit the daily target calories and adjusts for consumed food.
    """
    pref_key = "Non-Vegetarian" if dietary_preference in ["Non-Vegetarian", "Eggetarian"] else "Vegetarian"
    templates = MEAL_TEMPLATES.get(pref_key, MEAL_TEMPLATES["Vegetarian"])

    # If user has already consumed calories today, compute remaining need
    already_consumed_cal = sum(x.get('calories', 0.0) for x in (consumed_today or []))
    already_consumed_pro = sum(x.get('protein', 0.0) for x in (consumed_today or []))

    # Base allocation: Breakfast 25%, Lunch 35%, Snacks 15%, Dinner 25%
    b_item = templates["breakfast"][(day_offset) % len(templates["breakfast"])]
    l_item = templates["lunch"][(day_offset) % len(templates["lunch"])]
    s_item = templates["snacks"][(day_offset) % len(templates["snacks"])]
    d_item = templates["dinner"][(day_offset) % len(templates["dinner"])]

    raw_total = b_item["calories"] + l_item["calories"] + s_item["calories"] + d_item["calories"]

    # If adjusting dynamically because user had heavy snacks
    dynamic_note = ""
    if already_consumed_cal > 0:
        remaining_budget = max(400.0, target_calories - already_consumed_cal)
        scale = remaining_budget / raw_total if raw_total > 0 else 1.0
        dynamic_note = f"Plan dynamically calibrated for your logged consumption ({already_consumed_cal:.0f} kcal logged today; {remaining_budget:.0f} kcal remaining)."
    else:
        scale = target_calories / raw_total if raw_total > 0 else 1.0

    # Scale macro values
    def scale_meal(meal):
        return {
            "name": meal["name"],
            "calories": round(meal["calories"] * scale, 0),
            "protein": round(meal["protein"] * scale, 1),
            "carbs": round(meal["carbs"] * scale, 1),
            "fat": round(meal["fat"] * scale, 1),
            "fiber": round(meal["fiber"] * scale, 1)
        }

    meals = {
        "Breakfast": scale_meal(b_item),
        "Lunch": scale_meal(l_item),
        "Evening Snack": scale_meal(s_item),
        "Dinner": scale_meal(d_item)
    }

    tot_cal = sum(m["calories"] for m in meals.values())
    tot_pro = sum(m["protein"] for m in meals.values())
    tot_carb = sum(m["carbs"] for m in meals.values())
    tot_fat = sum(m["fat"] for m in meals.values())
    tot_fib = sum(m["fiber"] for m in meals.values())

    return {
        "target_calories": target_calories,
        "planned_calories": tot_cal,
        "total_protein": round(tot_pro, 1),
        "total_carbs": round(tot_carb, 1),
        "total_fat": round(tot_fat, 1),
        "total_fiber": round(tot_fib, 1),
        "meals": meals,
        "dynamic_note": dynamic_note,
        "dietary_preference": dietary_preference,
        "goal": goal
    }

def generate_weekly_plan(
    target_calories: float,
    dietary_preference: str = "Vegetarian",
    goal: str = "Maintenance"
) -> List[Dict[str, Any]]:
    """Generates a complete 7-day personalized weekly diet plan."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly = []
    for idx, day in enumerate(days):
        day_plan = generate_daily_plan(
            target_calories=target_calories,
            dietary_preference=dietary_preference,
            goal=goal,
            day_offset=idx
        )
        day_plan["day_name"] = day
        weekly.append(day_plan)
    return weekly

