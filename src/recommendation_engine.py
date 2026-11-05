"""
NutriFit AI - Recommendation Engine
Hybrid Machine Learning (KNN + Random Forest) + Nutritional Science Rules:
1. KNN Alternative Food Recommender (healthier substitutes)
2. Random Forest Goal Suitability Classifier
3. Dynamic Meal Balancing (continuous adjustment based on consumed snacks/meals)
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from src.food_analyzer import get_food_dataframe, get_food_by_id

FEATURE_COLS = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']

_knn_model = None
_scaler = None
_knn_meta = None
_classifier = None
_clf_meta = None

def load_models():
    global _knn_model, _scaler, _knn_meta, _classifier, _clf_meta
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, "models")

    if _knn_model is None and os.path.exists(os.path.join(models_dir, "food_knn.pkl")):
        _knn_model = joblib.load(os.path.join(models_dir, "food_knn.pkl"))
        _scaler = joblib.load(os.path.join(models_dir, "scaler.pkl"))
        _knn_meta = joblib.load(os.path.join(models_dir, "knn_metadata.pkl"))

    if _classifier is None and os.path.exists(os.path.join(models_dir, "food_classifier.pkl")):
        _classifier = joblib.load(os.path.join(models_dir, "food_classifier.pkl"))
        _clf_meta = joblib.load(os.path.join(models_dir, "classifier_metadata.pkl"))

def find_food_alternatives(
    food_id: int,
    dietary_filter: Optional[str] = None,
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Given a consumed food, identifies healthier alternatives using KNN:
    - Normalizes nutritional distance
    - Filters for items with better nutritional profiles (higher fiber/protein or lower sugar/fat)
    - Enforces dietary preference constraints
    """
    load_models()
    df = get_food_dataframe()
    target_row = df[df['food_id'] == food_id]
    if len(target_row) == 0:
        return []

    target_food = target_row.iloc[0]
    target_vec = np.array([[
        float(target_food.get('calories', 0.0)),
        float(target_food.get('protein', 0.0)),
        float(target_food.get('carbs', 0.0)),
        float(target_food.get('fat', 0.0)),
        float(target_food.get('fiber', 0.0)),
        float(target_food.get('sugar', 0.0)),
        float(target_food.get('sodium', 0.0))
    ]])

    target_scaled = _scaler.transform(target_vec)
    distances, indices = _knn_model.kneighbors(target_scaled, n_neighbors=min(50, len(df)))

    t_cal = float(target_food.get('calories', 0.0))
    t_fat = float(target_food.get('fat', 0.0))
    t_sug = float(target_food.get('sugar', 0.0))
    t_pro = float(target_food.get('protein', 0.0))
    t_fib = float(target_food.get('fiber', 0.0))

    candidates = []
    for dist, idx in zip(distances[0], indices[0]):
        item = df.iloc[idx].to_dict()
        if int(item['food_id']) == int(food_id):
            continue

        # Dietary preference filter
        item_pref = item.get('dietary_preference', 'Vegetarian')
        if dietary_filter and dietary_filter != "All":
            if dietary_filter == "Vegetarian" and item_pref not in ["Vegetarian", "Vegan"]:
                continue
            if dietary_filter == "Vegan" and item_pref != "Vegan":
                continue
            if dietary_filter == "Eggetarian" and item_pref not in ["Vegetarian", "Vegan", "Eggetarian"]:
                continue

        c_cal = float(item.get('calories', 0.0))
        c_fat = float(item.get('fat', 0.0))
        c_sug = float(item.get('sugar', 0.0))
        c_pro = float(item.get('protein', 0.0))
        c_fib = float(item.get('fiber', 0.0))

        # Check why it's a superior nutritional alternative
        reasons = []
        improvement_score = 0

        if t_sug > 10 and c_sug < t_sug * 0.5:
            reasons.append(f"Significantly lower sugar ({c_sug:.1f}g vs {t_sug:.1f}g)")
            improvement_score += 3
        if t_fat > 15 and c_fat < t_fat * 0.6:
            reasons.append(f"Lower total fat ({c_fat:.1f}g vs {t_fat:.1f}g)")
            improvement_score += 2
        if c_pro > t_pro * 1.3 and c_pro >= 4.0:
            reasons.append(f"Higher protein ({c_pro:.1f}g vs {t_pro:.1f}g)")
            improvement_score += 3
        if c_fib > t_fib * 1.3 and c_fib >= 2.0:
            reasons.append(f"More dietary fiber ({c_fib:.1f}g vs {t_fib:.1f}g)")
            improvement_score += 2
        if t_cal > 350 and c_cal < t_cal * 0.7:
            reasons.append(f"Fewer calories ({c_cal:.0f} vs {t_cal:.0f} kcal)")
            improvement_score += 1

        if improvement_score > 0:
            item['recommendation_reason'] = ", ".join(reasons)
            item['similarity_distance'] = float(dist)
            item['improvement_score'] = improvement_score
            candidates.append(item)

    # Curated Smart Healthy Substitutions for classic high-calorie / processed indulgences
    CURATED_HEALTHY_SWAPS = {
        "chips": ["Roasted Chana (Roasted Bengal Gram)", "Roasted Makhana (Foxnuts / Lotus Seeds)", "Moong Sprouts Salad"],
        "kurkure": ["Roasted Makhana (Foxnuts / Lotus Seeds)", "Roasted Chana (Roasted Bengal Gram)", "Moong Sprouts Salad"],
        "chocolate": ["Unsweetened Cocoa Greek Yogurt Bowl", "Fresh Fruit & Yogurt Bowl", "Raw Almonds"],
        "kitkat": ["Unsweetened Cocoa Greek Yogurt Bowl", "Fresh Fruit & Yogurt Bowl", "Raw Almonds"],
        "soft drink": ["Unsweetened Lemon Water / Nimbu Pani", "Fresh Tender Coconut Water", "Chaas / Spiced Buttermilk"],
        "coca-cola": ["Unsweetened Lemon Water / Nimbu Pani", "Fresh Tender Coconut Water", "Chaas / Spiced Buttermilk"],
        "samosa": ["Roasted Makhana (Foxnuts / Lotus Seeds)", "Moong Sprouts Salad", "Roasted Chana (Roasted Bengal Gram)"],
        "paratha": ["Whole Wheat Roti / Chapati", "Bajra Roti (Pearl Millet)", "Jowar Roti (Sorghum)"],
        "biscuit": ["Rolled Oats (Raw)", "Roasted Makhana (Foxnuts / Lotus Seeds)", "Raw Almonds"]
    }

    t_name_lower = target_food.get('food_name', '').lower()
    for kw, swap_names in CURATED_HEALTHY_SWAPS.items():
        if kw in t_name_lower:
            for sname in swap_names:
                match = df[df['food_name'] == sname]
                if len(match) > 0:
                    s_item = match.iloc[0].to_dict()
                    s_item['recommendation_reason'] = f"Healthier Indian smart swap: significantly higher protein/fiber and lower sugar/unhealthy fats"
                    s_item['similarity_distance'] = 0.1
                    s_item['improvement_score'] = 10
                    candidates.insert(0, s_item)
            break

    # Sort candidates by improvement score then similarity
    candidates.sort(key=lambda x: (-x.get('improvement_score', 0), x.get('similarity_distance', 1.0)))

    # Fallback to direct top nearest neighbors if no strict improvement found
    if len(candidates) < top_n:
        for dist, idx in zip(distances[0], indices[0]):
            item = df.iloc[idx].to_dict()
            if int(item['food_id']) == int(food_id) or any(c['food_id'] == item['food_id'] for c in candidates):
                continue
            item['recommendation_reason'] = "Nutritionally similar profile"
            item['similarity_distance'] = float(dist)
            candidates.append(item)
            if len(candidates) >= top_n:
                break

    return candidates[:top_n]

def predict_food_suitability(
    food: Dict[str, Any],
    user_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Uses the trained Random Forest Classifier to assess if a food fits
    the user's age, BMI, activity level, and fitness goal.
    """
    load_models()
    if _classifier is None:
        return {
            "prediction": "Fits in moderation",
            "confidence": 0.5,
            "badge_color": "warning"
        }

    age = float(user_profile.get('age', 25))
    height = float(user_profile.get('height', 170.0))
    weight = float(user_profile.get('weight', 65.0))
    height_m = height / 100.0 if height > 0 else 1.7
    bmi = round(weight / (height_m ** 2), 1)

    act_str = user_profile.get('activity_level', 'Moderately active')
    act_num = _clf_meta['activity_map'].get(act_str, 3.0)

    goal_str = user_profile.get('goal', 'Maintenance')
    goal_num = _clf_meta['goal_map'].get(goal_str, 1)

    cal = float(food.get('calories', 0.0))
    pro = float(food.get('protein', 0.0))
    carb = float(food.get('carbs', 0.0))
    fat = float(food.get('fat', 0.0))
    fib = float(food.get('fiber', 0.0))
    sug = float(food.get('sugar', 0.0))
    sod = float(food.get('sodium', 0.0))

    X_in = np.array([[age, bmi, act_num, goal_num, cal, pro, carb, fat, fib, sug, sod]])
    pred_idx = _classifier.predict(X_in)[0]
    probs = _classifier.predict_proba(X_in)[0]

    label = _clf_meta['class_labels'][pred_idx]
    confidence = float(probs[pred_idx])

    if pred_idx == 0:
        badge_color = "success" # Green
        badge_icon = "✅"
    elif pred_idx == 1:
        badge_color = "warning" # Yellow
        badge_icon = "⚠️"
    else:
        badge_color = "danger"  # Orange/Red
        badge_icon = "🛑"

    return {
        "prediction": label,
        "confidence": round(confidence * 100, 1),
        "badge_color": badge_color,
        "badge_icon": badge_icon,
        "goal": goal_str
    }

def generate_dynamic_adjustment_recommendations(
    consumed_items: List[Dict[str, Any]],
    targets: Dict[str, Any],
    dietary_preference: str = "Vegetarian"
) -> Dict[str, Any]:
    """
    Continuously evaluates what a user ate and recommends what to eat next.
    Takes snacks/meals into account to balance nutritional gaps.
    """
    total_cal = sum(x.get('calories', 0.0) for x in consumed_items)
    total_pro = sum(x.get('protein', 0.0) for x in consumed_items)
    total_fat = sum(x.get('fat', 0.0) for x in consumed_items)
    total_sug = sum(x.get('sugar', 0.0) for x in consumed_items)
    total_fib = sum(x.get('fiber', 0.0) for x in consumed_items)

    target_cal = targets.get('target_calories', 2000.0)
    target_pro = targets.get('target_protein_g', 100.0)
    target_fib = targets.get('target_fiber_g', 25.0)

    rem_cal = target_cal - total_cal
    rem_pro = max(0.0, target_pro - total_pro)
    rem_fib = max(0.0, target_fib - total_fib)

    df = get_food_dataframe()
    # Filter by dietary preference
    if dietary_preference == "Vegetarian":
        df_pref = df[df['dietary_preference'].isin(["Vegetarian", "Vegan"])]
    elif dietary_preference == "Vegan":
        df_pref = df[df['dietary_preference'] == "Vegan"]
    elif dietary_preference == "Eggetarian":
        df_pref = df[df['dietary_preference'].isin(["Vegetarian", "Vegan", "Eggetarian"])]
    else:
        df_pref = df

    recommended_foods = []
    clinical_rationale = []

    # Check snack impact
    has_high_snack = any(
        (x.get('sugar', 0.0) > 15.0 or x.get('fat', 0.0) > 15.0) and x.get('meal_type') in ['Snacks', 'Breakfast']
        for x in consumed_items
    )

    if has_high_snack:
        clinical_rationale.append(
            "Your logged snacks contributed a relatively high proportion of sugar and fat. "
            "For your upcoming meal, we recommend nutrient-dense whole foods rich in natural dietary fiber and clean protein to stabilize blood glucose and satiety."
        )

    if rem_pro > 15.0:
        clinical_rationale.append(
            f"You have a remaining protein goal of {rem_pro:.1f}g. Adding legumes, paneer, eggs, or tofu will help meet your lean mass requirements."
        )
        # Select protein-dense items
        pro_candidates = df_pref[df_pref['protein'] >= 7.0].sort_values(by=['health_score', 'protein'], ascending=False).head(3)
        for _, r in pro_candidates.iterrows():
            recommended_foods.append({
                "food_name": r['food_name'],
                "category": r['category'],
                "benefit": f"High Protein ({r['protein']:.1f}g/100g) - Supports recovery & satiety",
                "calories": r['calories']
            })

    if rem_fib > 8.0:
        clinical_rationale.append(
            f"Dietary fiber is currently at {total_fib:.1f}g (WHO target: ≥25g). Adding seasonal vegetables or whole grain/sprouts will support digestion and gut health."
        )
        fib_candidates = df_pref[df_pref['fiber'] >= 3.0].sort_values(by=['health_score', 'fiber'], ascending=False).head(3)
        for _, r in fib_candidates.iterrows():
            if not any(f['food_name'] == r['food_name'] for f in recommended_foods):
                recommended_foods.append({
                    "food_name": r['food_name'],
                    "category": r['category'],
                    "benefit": f"High Fiber ({r['fiber']:.1f}g/100g) - Optimizes satiety & cholesterol balance",
                    "calories": r['calories']
                })

    if not clinical_rationale:
        clinical_rationale.append(
            "Your daily intake is nicely balanced. Keep meals diverse and include colorful vegetables and adequate hydration."
        )

    # Deduplicate
    unique_recs = []
    seen = set()
    for f in recommended_foods:
        if f['food_name'] not in seen:
            seen.add(f['food_name'])
            unique_recs.append(f)

    return {
        "remaining_calories": round(rem_cal, 1),
        "remaining_protein": round(rem_pro, 1),
        "remaining_fiber": round(rem_fib, 1),
        "clinical_rationale": " ".join(clinical_rationale),
        "suggested_foods": unique_recs[:6]
    }
