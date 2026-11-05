"""
NutriFit AI - Model 2: K-Means Nutritional Clustering Engine
Groups foods into distinct nutritional clusters:
- High-Protein Powerhouse
- Fiber & Micronutrient Dense
- Calorie-Dense / Fats & Oils
- High-Sugar / Indulgence
- Hydrating & Low-Calorie Vegetables/Fruits
- Complex Carbohydrate Staples
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']

def name_clusters(cluster_centers, feature_names):
    """Assigns descriptive clinical names to clusters based on center profiles."""
    names = {}
    for idx, center in enumerate(cluster_centers):
        # features: ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']
        cal, pro, carb, fat, fib, sug, sod = center
        if sug > 1.2:
            names[idx] = "High-Sugar & Confectionery Treats"
        elif pro > 1.2:
            names[idx] = "High-Protein & Lean Fuel"
        elif fat > 1.2:
            names[idx] = "Calorie-Dense / Healthy Fats & Oils"
        elif fib > 1.0 or (carb > 0.5 and fib > 0.5):
            names[idx] = "Fiber & Nutrient-Dense Grains/Legumes"
        elif cal < -0.5:
            names[idx] = "Low-Calorie & Hydrating Produce"
        elif sod > 1.5:
            names[idx] = "Savory & Higher-Sodium Foods"
        else:
            names[idx] = "Balanced Carbohydrate & Mixed Meals"
    return names

def train_kmeans(data_path="data/food_nutrition.csv", model_dir="models", k=6):
    print(f"Training K-Means Clustering Model (k={k})...")
    df = pd.read_csv(data_path)

    X = df[FEATURE_COLS].copy()
    for col in FEATURE_COLS:
        X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0.0)

    scaler_path = os.path.join(model_dir, "scaler.pkl")
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        X_scaled = scaler.transform(X)
    else:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        joblib.dump(scaler, scaler_path)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    # Compute silhouette score on a sample for speed & academic reporting
    sample_size = min(5000, len(X_scaled))
    sil_score = silhouette_score(X_scaled[:sample_size], clusters[:sample_size])
    print(f"K-Means training complete. Silhouette Score (sample {sample_size}): {sil_score:.4f}")

    cluster_names = name_clusters(kmeans.cluster_centers_, FEATURE_COLS)
    print("Identified Clusters:")
    for c_id, name in cluster_names.items():
        count = int(np.sum(clusters == c_id))
        print(f"  Cluster {c_id}: {name} ({count} foods)")

    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(kmeans, os.path.join(model_dir, "food_kmeans.pkl"))
    joblib.dump(cluster_names, os.path.join(model_dir, "cluster_names.pkl"))

    # Also save food cluster assignments to CSV for fast access
    df['cluster_id'] = clusters
    df['cluster_name'] = [cluster_names[c] for c in clusters]
    df.to_csv(data_path, index=False)

    return kmeans, cluster_names, sil_score

if __name__ == "__main__":
    train_kmeans()

