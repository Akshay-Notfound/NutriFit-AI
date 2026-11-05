"""
NutriFit AI - Model 3: Random Forest Food-Goal Suitability Classifier
Predicts whether a specific food item fits the user's personal nutritional profile and goal:
- 'Fits your daily nutrition goals'
- 'Fits in moderation'
- 'Consider a more nutrient-dense alternative'

Features:
['age', 'bmi', 'activity_level_num', 'fitness_goal_num', 'calories', 'protein', 'carbohydrates', 'fat', 'fiber', 'sugar', 'sodium']
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

ACTIVITY_MAP = {
    "Sedentary": 1.0,
    "Lightly active": 2.0,
    "Moderately active": 3.0,
    "Very active": 4.0,
    "Extra active": 5.0
}

GOAL_MAP = {
    "Weight Loss": 0,
    "Maintenance": 1,
    "Weight Gain": 2
}

CLASS_LABELS = [
    "Fits your daily nutrition goals",
    "Fits in moderation",
    "Consider a more nutrient-dense alternative"
]

def generate_clinically_grounded_training_data(df_foods, n_samples=15000, random_state=42):
    """
    Synthesizes diverse user-food evaluation scenarios adhering to established
    nutrition principles (WHO, ICMR-NIN, Dietary Guidelines for Americans).
    """
    np.random.seed(random_state)

    # Sample user profile archetypes
    ages = np.random.randint(18, 65, size=n_samples)
    bmis = np.round(np.random.normal(25.0, 4.5, size=n_samples).clip(17.5, 40.0), 1)
    activity_keys = list(ACTIVITY_MAP.keys())
    activities = np.random.choice(activity_keys, size=n_samples, p=[0.25, 0.35, 0.25, 0.10, 0.05])
    goals = np.random.choice(list(GOAL_MAP.keys()), size=n_samples, p=[0.45, 0.30, 0.25])

    # Sample foods from curated dataset
    sampled_foods = df_foods.sample(n=n_samples, replace=True, random_state=random_state).reset_index(drop=True)

    records = []
    labels = []

    for i in range(n_samples):
        age = ages[i]
        bmi = bmis[i]
        act_str = activities[i]
        act_num = ACTIVITY_MAP[act_str]
        goal_str = goals[i]
        goal_num = GOAL_MAP[goal_str]

        row = sampled_foods.iloc[i]
        cal = float(row.get('calories', 0.0))
        pro = float(row.get('protein', 0.0))
        carb = float(row.get('carbs', 0.0))
        fat = float(row.get('fat', 0.0))
        fib = float(row.get('fiber', 0.0))
        sug = float(row.get('sugar', 0.0))
        sod = float(row.get('sodium', 0.0))

        # Clinical labeling logic
        # 0: Fits goals, 1: Moderation, 2: Consider alternative
        if goal_str == "Weight Loss":
            if (sug > 22.0 or (cal > 400 and fib < 2.0 and pro < 5.0) or (fat > 25.0 and pro < 6.0)):
                label = 2 # Consider alternative
            elif (sug > 10.0 or cal > 280.0 or sod > 700.0):
                label = 1 # In moderation
            elif (fib >= 3.0 or pro >= 10.0 or cal < 160.0):
                label = 0 # Fits goals
            else:
                label = 1
        elif goal_str == "Weight Gain":
            if (sug > 35.0 and pro < 3.0 and fib < 1.0):
                label = 2 # Empty calories, poor for lean muscle
            elif (pro >= 12.0 or (cal >= 250.0 and fib >= 2.5) or (fat >= 12.0 and sug < 10.0)):
                label = 0 # Great nutrient-dense fuel for weight gain
            elif (cal < 80.0 and pro < 2.0):
                label = 1 # Too low energy density for gaining
            else:
                label = 0
        else: # Maintenance
            if (sug > 28.0 or (cal > 450 and fib < 1.5)):
                label = 2
            elif (sug > 12.0 or sod > 800.0 or fat > 22.0):
                label = 1
            else:
                label = 0

        records.append([age, bmi, act_num, goal_num, cal, pro, carb, fat, fib, sug, sod])
        labels.append(label)

    feature_cols = [
        "age", "bmi", "activity_level", "fitness_goal",
        "calories", "protein", "carbohydrates", "fat", "fiber", "sugar", "sodium"
    ]
    df_train = pd.DataFrame(records, columns=feature_cols)
    df_train['target'] = labels
    return df_train, feature_cols

def train_classifier(data_path="data/food_nutrition.csv", model_dir="models"):
    print("Generating clinically grounded training scenarios...")
    df_foods = pd.read_csv(data_path)
    df_train, feature_cols = generate_clinically_grounded_training_data(df_foods, n_samples=18000)

    X = df_train[feature_cols]
    y = df_train['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Training Random Forest Classifier (100 estimators)...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=14, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=CLASS_LABELS, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    print("\n--- Model Evaluation Report ---")
    print(classification_report(y_test, y_pred, target_names=CLASS_LABELS))
    print("Confusion Matrix:")
    print(cm)

    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(clf, os.path.join(model_dir, "food_classifier.pkl"))

    metadata = {
        "feature_cols": feature_cols,
        "class_labels": CLASS_LABELS,
        "activity_map": ACTIVITY_MAP,
        "goal_map": GOAL_MAP,
        "report": report,
        "confusion_matrix": cm.tolist()
    }
    joblib.dump(metadata, os.path.join(model_dir, "classifier_metadata.pkl"))
    print(f"Classifier saved to {model_dir}/food_classifier.pkl")

    return clf, metadata

if __name__ == "__main__":
    train_classifier()

