"""
NutriFit AI - Calorie Calculator & Daily Balance Engine
Computes real-time daily totals, remaining allowances, and nutritional gap analytics.
"""

from typing import Dict, Any, List

def calculate_daily_balance(consumed_items: List[Dict[str, Any]], targets: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregates all foods consumed today and compares against user's daily nutritional targets.
    consumed_items: list of dicts with keys:
      ['calories', 'protein', 'carbs', 'fat', 'saturated_fat', 'fiber', 'sugar', 'sodium', 'calcium', 'iron', 'vitamin_c']
    targets: dict output from calculate_daily_targets()
    """
    total_calories = sum(item.get('calories', 0.0) for item in consumed_items)
    total_protein = sum(item.get('protein', 0.0) for item in consumed_items)
    total_carbs = sum(item.get('carbs', 0.0) for item in consumed_items)
    total_fat = sum(item.get('fat', 0.0) for item in consumed_items)
    total_sat_fat = sum(item.get('saturated_fat', 0.0) for item in consumed_items)
    total_fiber = sum(item.get('fiber', 0.0) or item.get('fibre', 0.0) for item in consumed_items)
    total_sugar = sum(item.get('sugar', 0.0) for item in consumed_items)
    total_sodium = sum(item.get('sodium', 0.0) for item in consumed_items)
    total_calcium = sum(item.get('calcium', 0.0) for item in consumed_items)
    total_iron = sum(item.get('iron', 0.0) for item in consumed_items)
    total_vitamin_c = sum(item.get('vitamin_c', 0.0) for item in consumed_items)

    target_cal = targets.get('target_calories', 2000.0)
    target_pro = targets.get('target_protein_g', 100.0)
    target_carb = targets.get('target_carbs_g', 250.0)
    target_fat = targets.get('target_fat_g', 60.0)
    target_fib = targets.get('target_fiber_g', 25.0)
    sugar_limit = targets.get('sugar_limit_g', 35.0)
    sodium_limit = targets.get('sodium_limit_mg', 2000.0)

    # Remaining balances
    rem_calories = round(target_cal - total_calories, 1)
    rem_protein = round(max(0.0, target_pro - total_protein), 1)
    rem_carbs = round(max(0.0, target_carb - total_carbs), 1)
    rem_fat = round(max(0.0, target_fat - total_fat), 1)
    rem_fiber = round(max(0.0, target_fib - total_fiber), 1)

    # Percentage completions
    cal_pct = round((total_calories / target_cal * 100.0), 1) if target_cal > 0 else 0
    pro_pct = round((total_protein / target_pro * 100.0), 1) if target_pro > 0 else 0
    carb_pct = round((total_carbs / target_carb * 100.0), 1) if target_carb > 0 else 0
    fat_pct = round((total_fat / target_fat * 100.0), 1) if target_fat > 0 else 0
    fib_pct = round((total_fiber / target_fib * 100.0), 1) if target_fib > 0 else 0

    # Qualitative clinical assessment & insights
    insights = []
    if rem_calories > 300:
        insights.append(f"You have **{rem_calories:.0f} kcal** remaining in your daily energy budget.")
    elif -100 <= rem_calories <= 300:
        insights.append(f"You are right on track with your daily energy target ({total_calories:.0f} / {target_cal:.0f} kcal).")
    else:
        overshoot = abs(rem_calories)
        insights.append(f"You have exceeded your target energy by **{overshoot:.0f} kcal**. We will adjust your next meal to prioritize high-satiety, low-energy vegetables and lean protein.")

    if total_sugar > sugar_limit:
        insights.append(f"⚠️ Added sugar intake is **{total_sugar:.1f}g** (recommended limit: {sugar_limit:.0f}g). Prioritize water and unsweetened beverages.")
    elif total_sugar > sugar_limit * 0.7:
        insights.append(f"Sugar intake is approaching the daily ceiling ({total_sugar:.1f}g / {sugar_limit:.0f}g).")

    if total_sodium > sodium_limit:
        insights.append(f"⚠️ Sodium intake is **{total_sodium:.0f}mg** (recommended limit: 2000mg). Keep upcoming meal seasonings light and increase potassium-rich produce.")

    if rem_protein > 20:
        insights.append(f"You still need **{rem_protein:.1f}g of protein** to hit your goal. Focus on dal, paneer, eggs, tofu, or sprouts for your upcoming meal.")

    if rem_fiber > 10:
        insights.append(f"Fiber intake is currently **{total_fiber:.1f}g** (target: {target_fib:.0f}g). Add salads, green sabzi, whole fruits, or millets.")

    return {
        "consumed": {
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fat": round(total_fat, 1),
            "saturated_fat": round(total_sat_fat, 1),
            "fiber": round(total_fiber, 1),
            "sugar": round(total_sugar, 1),
            "sodium": round(total_sodium, 1),
            "calcium": round(total_calcium, 1),
            "iron": round(total_iron, 1),
            "vitamin_c": round(total_vitamin_c, 1)
        },
        "remaining": {
            "calories": rem_calories,
            "protein": rem_protein,
            "carbs": rem_carbs,
            "fat": rem_fat,
            "fiber": rem_fiber
        },
        "percentages": {
            "calories": cal_pct,
            "protein": pro_pct,
            "carbs": carb_pct,
            "fat": fat_pct,
            "fiber": fib_pct
        },
        "insights": insights
    }

