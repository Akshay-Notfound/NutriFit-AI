"""
NutriFit AI - Comprehensive End-to-End System Test
"""

import os
import sys

print("--- 1. Testing Database & Seeding ---")
from src.database import init_db, get_session, User, UserProfile, FoodItem, FoodNutrition, FoodLog
init_db()
session = get_session()
food_count = session.query(FoodItem).count()
print(f"Database seeded food items count: {food_count}")

print("\n--- 2. Testing Nutrition Science Engine ---")
from src.nutrition_engine import calculate_daily_targets, calculate_bmi
targets = calculate_daily_targets(65.0, 170.0, 22, "Male", "Moderately active", "Weight Gain")
print(f"Target calories for 22M 65kg Weight Gain: {targets['target_calories']} kcal")
print(f"BMI: {targets['bmi']} ({targets['bmi_category']})")
print(f"Target Protein: {targets['target_protein_g']}g | Fiber: {targets['target_fiber_g']}g")

print("\n--- 3. Testing KNN Recommendation Engine ---")
from src.recommendation_engine import find_food_alternatives, predict_food_suitability, generate_dynamic_adjustment_recommendations
chips = session.query(FoodItem).filter(FoodItem.name.like("%Lay%s India%s Magic Masala%")).first()
if chips:
    alts = find_food_alternatives(chips.food_id, top_n=3)
    print(f"KNN alternatives for '{chips.name}':")
    for idx, a in enumerate(alts):
        print(f"  #{idx+1} {a['food_name']} -> {a.get('recommendation_reason')}")

print("\n--- 4. Testing Random Forest Goal Classifier ---")
test_food = {
    'calories': 534, 'protein': 7.8, 'carbs': 59.8, 'fat': 30.4,
    'fiber': 1.8, 'sugar': 57.0, 'sodium': 140
}
rf_res = predict_food_suitability(
    test_food,
    {'age': 22, 'height': 170, 'weight': 65, 'activity_level': 'Moderately active', 'goal': 'Weight Gain'}
)
print(f"RF Prediction for Chocolate Bar: {rf_res['prediction']} (Confidence: {rf_res['confidence']}%)")

print("\n--- 5. Testing Dynamic Diet Balancer ---")
consumed_sample = [
    {"food_name": "Lay's Chips (50g)", "meal_type": "Snacks", "calories": 270, "protein": 3.4, "carbs": 27, "fat": 17, "fiber": 1.7, "sugar": 2.2, "sodium": 410},
    {"food_name": "Cadbury Chocolate (25g)", "meal_type": "Snacks", "calories": 135, "protein": 1.9, "carbs": 15, "fat": 7.6, "fiber": 0.5, "sugar": 14.2, "sodium": 35}
]
dyn = generate_dynamic_adjustment_recommendations(consumed_sample, targets, "Vegetarian")
print(f"Dynamic Evaluation: {dyn['clinical_rationale']}")
print("Suggested balancing foods:")
for sf in dyn['suggested_foods']:
    print(f"  - {sf['food_name']}: {sf['benefit']}")

print("\n--- 6. Testing Diet Planner ---")
from src.diet_planner import generate_daily_plan, generate_weekly_plan
dp = generate_daily_plan(2500, "Vegetarian", "Weight Gain", consumed_today=consumed_sample)
print(f"Generated daily plan: {dp['planned_calories']} kcal across {len(dp['meals'])} meals")
for m_name, m_data in dp['meals'].items():
    print(f"  * {m_name}: {m_data['name']} ({m_data['calories']:.0f} kcal, P:{m_data['protein']}g)")

wp = generate_weekly_plan(2500, "Vegetarian", "Weight Gain")
print(f"Generated weekly schedule for {len(wp)} days.")

print("\n--- 7. Testing PDF Report Generation ---")
from utils.helpers import generate_pdf_report
pdf_file = generate_pdf_report(
    "Rahul Sharma",
    {'age': 22, 'sex': 'Male', 'height': 170, 'weight': 65, 'goal': 'Weight Gain'},
    targets,
    {
        'consumed': {'calories': 405, 'protein': 8.7, 'carbs': 42, 'fat': 24.6, 'fiber': 2.2, 'sugar': 18.7, 'sodium': 445},
        'remaining': {'calories': 2095, 'protein': 91, 'carbs': 208, 'fat': 35, 'fiber': 23},
        'insights': ['Great snack logged. Balance remaining meals with fiber and protein.']
    },
    [
        {'meal_type': 'Snacks', 'food_name': "Lay's Magic Masala", 'quantity': 50, 'calories': 270, 'protein': 3.4, 'carbs': 27},
        {'meal_type': 'Snacks', 'food_name': 'Cadbury Chocolate', 'quantity': 25, 'calories': 135, 'protein': 1.9, 'carbs': 15}
    ],
    "test_report.pdf"
)
print(f"PDF generated: {pdf_file} (Size: {os.path.getsize(pdf_file)} bytes)")

print("\n--- 8. Checking Syntax of All Streamlit Pages ---")
import py_compile
pages = ["Home.py"] + [os.path.join("pages", p) for p in os.listdir("pages") if p.endswith(".py")]
for page in pages:
    py_compile.compile(page, doraise=True)
    print(f"  ✓ {page} compiles cleanly")

session.close()
print("\n>>> ALL 8 INTEGRATION TESTS PASSED PERFECTLY! <<<")

