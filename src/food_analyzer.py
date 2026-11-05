"""
NutriFit AI - Food Analyzer Module
Provides food search, nutrient scaling, and Open Food Facts / OCR simulation helpers.
"""

import pandas as pd
import numpy as np
import os
from typing import List, Dict, Any, Optional

_df_foods = None

def get_food_dataframe(csv_path="data/food_nutrition.csv") -> pd.DataFrame:
    global _df_foods
    if _df_foods is None:
        if not os.path.exists(csv_path):
            csv_path = "data/processed/food_nutrition.csv"
        _df_foods = pd.read_csv(csv_path)
    return _df_foods

def search_foods(query: str, category_filter: Optional[str] = None, dietary_filter: Optional[str] = None, limit: int = 30) -> List[Dict[str, Any]]:
    """
    Fast, flexible search across food names, categories, and brands.
    Prioritizes exact prefix and whole-word matches.
    """
    df = get_food_dataframe()
    if not query or len(query.strip()) == 0:
        results = df.head(limit)
    else:
        q = query.strip().lower()
        # Search in food_name, brand, category
        mask = (
            df['food_name'].str.lower().str.contains(q, na=False) |
            df['brand'].str.lower().str.contains(q, na=False) |
            df['category'].str.lower().str.contains(q, na=False)
        )
        results = df[mask]

    if category_filter and category_filter != "All":
        results = results[results['category'] == category_filter]

    if dietary_filter and dietary_filter != "All":
        if dietary_filter == "Vegetarian":
            results = results[results['dietary_preference'].isin(["Vegetarian", "Vegan"])]
        elif dietary_filter == "Vegan":
            results = results[results['dietary_preference'] == "Vegan"]
        elif dietary_filter == "Eggetarian":
            results = results[results['dietary_preference'].isin(["Vegetarian", "Vegan", "Eggetarian"])]

    return results.head(limit).to_dict(orient="records")

def get_food_by_id(food_id: int) -> Optional[Dict[str, Any]]:
    df = get_food_dataframe()
    match = df[df['food_id'] == food_id]
    if len(match) == 0:
        return None
    return match.iloc[0].to_dict()

def calculate_serving_nutrients(food: Dict[str, Any], quantity: float) -> Dict[str, Any]:
    """
    Scales nutrients from standard 100g base to the user's logged quantity.
    """
    scale = quantity / 100.0
    return {
        "food_id": food.get('food_id'),
        "food_name": food.get('food_name'),
        "category": food.get('category'),
        "brand": food.get('brand'),
        "quantity": quantity,
        "unit": food.get('serving_unit', 'g'),
        "calories": round(float(food.get('calories', 0.0)) * scale, 1),
        "protein": round(float(food.get('protein', 0.0)) * scale, 1),
        "carbs": round(float(food.get('carbs', 0.0)) * scale, 1),
        "fat": round(float(food.get('fat', 0.0)) * scale, 1),
        "saturated_fat": round(float(food.get('saturated_fat', 0.0)) * scale, 1),
        "fiber": round(float(food.get('fiber', 0.0)) * scale, 1),
        "sugar": round(float(food.get('sugar', 0.0)) * scale, 1),
        "sodium": round(float(food.get('sodium', 0.0)) * scale, 1),
        "calcium": round(float(food.get('calcium', 0.0)) * scale, 1),
        "iron": round(float(food.get('iron', 0.0)) * scale, 1),
        "vitamin_c": round(float(food.get('vitamin_c', 0.0)) * scale, 1),
        "health_score": food.get('health_score', 50.0),
        "dietary_preference": food.get('dietary_preference', 'Vegetarian')
    }

