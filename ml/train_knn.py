"""
NutriFit AI - Model 1: KNN Food Recommendation & Alternative Engine
Trains Nearest Neighbors model using standardized nutritional profiles to:
1. Find similar foods
2. Recommend healthier substitutes (lower sugar/fat, higher protein/fiber)
3. Filter by dietary preference
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']

def train_knn(data_path="data/food_nutrition.csv", model_dir="models"):
    print("Training KNN Food Recommendation Model...")
    df = pd.read_csv(data_path)
    
    # Ensure features are numeric and clean
    X = df[FEATURE_COLS].copy()
    for col in FEATURE_COLS:
        X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0.0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train Nearest Neighbors with cosine metric for profile similarity
    knn_cosine = NearestNeighbors(n_neighbors=25, metric='cosine', algorithm='brute')
    knn_cosine.fit(X_scaled)

    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(knn_cosine, os.path.join(model_dir, "food_knn.pkl"))
    joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))

    # Save mapping for quick inference
    metadata = {
        'feature_cols': FEATURE_COLS,
        'food_ids': df['food_id'].tolist(),
        'food_names': df['food_name'].tolist(),
        'categories': df['category'].tolist(),
        'dietary_prefs': df['dietary_preference'].tolist()
    }
    joblib.dump(metadata, os.path.join(model_dir, "knn_metadata.pkl"))
    print(f"KNN model trained successfully on {len(df)} foods and saved to {model_dir}/")

    return knn_cosine, scaler, metadata

if __name__ == "__main__":
    train_knn()

