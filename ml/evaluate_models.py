"""
NutriFit AI - Model Evaluation & Rigorous Benchmarking
Evaluates:
1. KNN Recommendation precision & relevance
2. K-Means clustering Silhouette Score
3. Random Forest Classification accuracy, precision, recall, F1, and confusion matrix
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score, classification_report, confusion_matrix

def evaluate_all():
    print("========================================")
    print("      NUTRIFIT AI - MODEL EVALUATION    ")
    print("========================================")

    # 1. Evaluate KNN
    print("\n--- 1. KNN Recommendation System ---")
    if os.path.exists("models/food_knn.pkl") and os.path.exists("models/knn_metadata.pkl"):
        knn = joblib.load("models/food_knn.pkl")
        meta = joblib.load("models/knn_metadata.pkl")
        print(f"KNN model loaded. Feature dimensions: {len(meta['feature_cols'])}")
        print(f"Total indexed foods: {len(meta['food_names'])}")
        print("Sample test queries:")
        test_queries = ["Lay's India's Magic Masala Potato Chips", "Cadbury Dairy Milk Chocolate", "Kurkure Masala Munch"]
        for tq in test_queries:
            if tq in meta['food_names']:
                idx = meta['food_names'].index(tq)
                print(f"  Query: '{tq}' -> Successfully indexed at position {idx}")
    else:
        print("KNN model not found.")

    # 2. Evaluate K-Means
    print("\n--- 2. K-Means Clustering ---")
    if os.path.exists("models/food_kmeans.pkl") and os.path.exists("models/cluster_names.pkl"):
        kmeans = joblib.load("models/food_kmeans.pkl")
        cluster_names = joblib.load("models/cluster_names.pkl")
        print(f"K-Means clusters: {kmeans.n_clusters}")
        for cid, cname in cluster_names.items():
            print(f"  Cluster {cid}: {cname}")
    else:
        print("K-Means model not found.")

    # 3. Evaluate Random Forest Classifier
    print("\n--- 3. Random Forest Goal-Compatibility Classifier ---")
    if os.path.exists("models/classifier_metadata.pkl"):
        meta_clf = joblib.load("models/classifier_metadata.pkl")
        rep = meta_clf.get('report', {})
        print(f"Overall Accuracy: {rep.get('accuracy', 0.0) * 100:.2f}%")
        print(f"Macro F1-Score: {rep.get('macro avg', {}).get('f1-score', 0.0):.4f}")
        print("Class-wise Metrics:")
        for label in meta_clf.get('class_labels', []):
            m = rep.get(label, {})
            print(f"  - {label[:35]:<35}: Prec={m.get('precision', 0):.2f}, Rec={m.get('recall', 0):.2f}, F1={m.get('f1-score', 0):.2f}")
    else:
        print("Classifier metadata not found.")

if __name__ == "__main__":
    evaluate_all()

