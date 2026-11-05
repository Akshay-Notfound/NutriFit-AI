"""
NutriFit AI - Page 4: AI Food Recommendations & Healthier Alternatives
Implements:
1. KNN Food Recommendation for healthier substitutes
2. Random Forest Goal Suitability Classifier
3. K-Means Nutritional Clusters Explorer
4. Dynamic meal balancing for logged snacks
"""

import streamlit as st
import pandas as pd
import joblib
import os
from src.food_analyzer import get_food_dataframe, search_foods
from src.recommendation_engine import find_food_alternatives, predict_food_suitability, generate_dynamic_adjustment_recommendations
from src.database import get_session, User, FoodLog
from src.nutrition_engine import calculate_daily_targets
from utils.charts import create_food_comparison_radar
from utils.helpers import inject_custom_css, render_disclaimer

st.set_page_config(page_title="NutriFit AI - AI Recommendations", page_icon="🤖", layout="wide")
st.markdown(inject_custom_css(), unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

session = get_session()
try:
    user = session.query(User).filter_by(user_id=st.session_state.user_id).first()
    p = user.profile if user else None
    user_profile = {
        "age": p.age if p else 22,
        "sex": p.sex if p else "Male",
        "height": p.height if p else 170.0,
        "weight": p.weight if p else 65.0,
        "activity_level": p.activity_level if p else "Moderately active",
        "goal": p.goal if p else "Weight Gain",
        "dietary_preference": p.dietary_preference if p else "Vegetarian"
    }
finally:
    session.close()

targets = calculate_daily_targets(
    user_profile['weight'], user_profile['height'],
    user_profile['age'], user_profile['sex'],
    user_profile['activity_level'], user_profile['goal']
)

st.title("🤖 AI-Powered Nutritional Recommendations")
st.markdown("Harness machine learning models (KNN, Random Forest, K-Means) to identify smart food swaps, classify goal compatibility, and adapt meals.")

tabs = st.tabs([
    "🔄 Model 1: KNN Healthier Alternatives",
    "🎯 Model 2: Random Forest Goal Classifier",
    "🍱 Dynamic Meal Balancer",
    "🌐 Model 3: K-Means Nutritional Clusters"
])

# ----------------- TAB 1: KNN ALTERNATIVES -----------------
with tabs[0]:
    st.markdown("### 🔄 KNN-Based Smart Alternative Food Finder")
    st.markdown("Select or search a food (e.g. potato chips, chocolate, Kurkure, ice cream, soft drinks) to find nutritionally superior alternatives matching your dietary profile.")

    df_foods = get_food_dataframe()

    col_q1, col_q2 = st.columns([2, 1])
    with col_q1:
        # Popular defaults
        popular_snacks = [
            "Lay's India's Magic Masala Potato Chips",
            "Kurkure Masala Munch",
            "Cadbury Dairy Milk Chocolate",
            "Nestlé KitKat Chocolate Bar",
            "Coca-Cola / Carbonated Soft Drink",
            "Samosa (Potato & Peas Fried)",
            "Haldiram's Aloo Bhujia",
            "Parle-G Glucose Biscuits",
            "Plain Paratha (Ghee)"
        ]
        selected_food_name = st.selectbox("Choose a common snack or meal:", popular_snacks)
    with col_q2:
        alt_diet_pref = st.selectbox("Filter Alternatives By:", ["All", "Vegetarian", "Vegan", "Eggetarian"], index=1)

    # Find food id
    matched_rows = df_foods[df_foods['food_name'] == selected_food_name]
    if len(matched_rows) > 0:
        target_food = matched_rows.iloc[0].to_dict()
        food_id = int(target_food['food_id'])

        # Display target food profile
        st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
        st.markdown(f"#### Selected Food: **{target_food['food_name']}**")
        st.caption(f"Brand: {target_food.get('brand')} | Category: {target_food.get('category')} | Preference: {target_food.get('dietary_preference')}")
        
        tc1, tc2, tc3, tc4, tc5, tc6, tc7 = st.columns(7)
        tc1.metric("Calories", f"{target_food['calories']:.0f} kcal")
        tc2.metric("Protein", f"{target_food['protein']:.1f} g")
        tc3.metric("Carbs", f"{target_food['carbs']:.1f} g")
        tc4.metric("Fat", f"{target_food['fat']:.1f} g")
        tc5.metric("Fiber", f"{target_food['fiber']:.1f} g")
        tc6.metric("Sugar", f"{target_food['sugar']:.1f} g")
        tc7.metric("Sodium", f"{target_food['sodium']:.0f} mg")
        st.markdown("</div>", unsafe_allow_html=True)

        # Run KNN
        with st.spinner("Executing KNN similarity & nutritional enhancement search..."):
            alternatives = find_food_alternatives(food_id, dietary_filter=alt_diet_pref, top_n=5)

        st.markdown("#### 🌟 Recommended Healthier Alternatives (via KNN)")
        if not alternatives:
            st.info("No closer alternatives found under current dietary filter.")
        else:
            col_list, col_chart = st.columns([1.3, 1])

            with col_list:
                for idx, alt in enumerate(alternatives):
                    st.markdown(f"""
                    <div style="background:#161B22; border:1px solid #30363D; border-left:4px solid #00E676; border-radius:10px; padding:12px 16px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:15px; font-weight:700; color:#FFFFFF;">#{idx+1} {alt['food_name']}</span>
                            <span class="badge-success">{alt.get('dietary_preference', 'Vegetarian')}</span>
                        </div>
                        <div style="font-size:12px; color:#00E676; font-weight:600; margin-top:4px;">✨ {alt.get('recommendation_reason', 'Nutritionally superior')}</div>
                        <div style="font-size:12px; color:#8B949E; margin-top:6px;">
                            🔥 {alt['calories']:.0f} kcal | 🍗 Protein: {alt['protein']:.1f}g | 🌾 Fiber: {alt['fiber']:.1f}g | 🍬 Sugar: {alt['sugar']:.1f}g | 🥑 Fat: {alt['fat']:.1f}g
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_chart:
                st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
                st.markdown("##### 🕸️ Side-by-Side Nutritional Radar")
                best_alt = alternatives[0]
                fig_radar = create_food_comparison_radar(target_food, best_alt)
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
                st.caption(f"Comparing **{target_food['food_name'][:20]}** (Red) vs **{best_alt['food_name'][:20]}** (Green).")
                st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TAB 2: RANDOM FOREST GOAL CLASSIFIER -----------------
with tabs[1]:
    st.markdown("### 🎯 Model 2: Random Forest Food-Goal Suitability Classifier")
    st.markdown("Predicts whether any given food fits your specific body composition and target goal (`Weight Loss`, `Maintenance`, or `Weight Gain`).")

    col_cf1, col_cf2 = st.columns([1.1, 1])

    with col_cf1:
        st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
        st.markdown("##### Select Food or Enter Custom Nutritional Values")
        
        eval_food_name = st.selectbox("Preset Food:", [
            "Roasted Chana (Roasted Bengal Gram)",
            "Lay's India's Magic Masala Potato Chips",
            "Moong Dal Tadka (Yellow Lentils)",
            "Cadbury Dairy Milk Chocolate",
            "Moong Sprouts Salad",
            "Optimum Nutrition Whey Protein Powder",
            "Coca-Cola / Carbonated Soft Drink"
        ])

        food_match = df_foods[df_foods['food_name'] == eval_food_name].iloc[0].to_dict()

        c_c, c_p = st.columns(2)
        in_cals = c_c.number_input("Calories (kcal / 100g)", value=float(food_match['calories']))
        in_pro = c_p.number_input("Protein (g / 100g)", value=float(food_match['protein']))

        c_cb, c_f = st.columns(2)
        in_carbs = c_cb.number_input("Carbs (g / 100g)", value=float(food_match['carbs']))
        in_fat = c_f.number_input("Total Fat (g / 100g)", value=float(food_match['fat']))

        c_fb, c_sg = st.columns(2)
        in_fib = c_fb.number_input("Fiber (g / 100g)", value=float(food_match['fiber']))
        in_sug = c_sg.number_input("Sugar (g / 100g)", value=float(food_match['sugar']))
        in_sod = st.number_input("Sodium (mg / 100g)", value=float(food_match['sodium']))

        st.markdown("</div>", unsafe_allow_html=True)

    with col_cf2:
        st.markdown("<div class='nutri-card-glow'>", unsafe_allow_html=True)
        st.markdown("##### 🧠 Machine Learning Prediction")
        
        test_food = {
            "calories": in_cals, "protein": in_pro, "carbs": in_carbs,
            "fat": in_fat, "fiber": in_fib, "sugar": in_sug, "sodium": in_sod
        }
        res = predict_food_suitability(test_food, user_profile)

        badge_class = f"badge-{res['badge_color']}"
        st.markdown(f"### {res['badge_icon']} <span class='{badge_class}' style='font-size:18px;'>{res['prediction']}</span>", unsafe_allow_html=True)
        st.markdown(f"**Confidence Score:** `{res['confidence']}%` | **Evaluating for Goal:** `{res['goal']}`")

        st.markdown("---")
        st.markdown("##### Clinical Rationale:")
        if res['prediction'] == "Fits your daily nutrition goals":
            st.write("✅ This food offers strong nutrient density, valuable micronutrients/protein, and fits comfortably within daily energy and macronutrient allowances.")
        elif res['prediction'] == "Fits in moderation":
            st.write("⚠️ This food can be included within your dietary pattern in controlled portion sizes. Monitor cumulative daily sodium, sugar, or saturated fat.")
        else:
            st.write("🛑 This food features high caloric density with minimal dietary fiber or protein ('empty energy'). For your goal, prioritize wholesome substitutes.")

        # Model accuracy note
        if os.path.exists("models/classifier_metadata.pkl"):
            meta = joblib.load("models/classifier_metadata.pkl")
            acc = meta.get('report', {}).get('accuracy', 0.99) * 100
            st.caption(f"Random Forest Classifier Accuracy on Test Set: **{acc:.1f}%** (trained on clinical nutritional rules)")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TAB 3: DYNAMIC MEAL BALANCER -----------------
with tabs[2]:
    st.markdown("### 🍱 Dynamic Meal Balancer (Continuous Adaptation)")
    st.markdown("Simulate what happens when you consume snacks or meals. The system recalculates remaining targets and dynamically recommends balancing dishes.")

    sim_snack = st.selectbox("Simulate eating this snack:", [
        "1 Packet of Lay's Chips (50g) + 1 Cadbury Chocolate Bar (25g)",
        "1 Samosa (80g) + 1 Sweet Lassi (200ml)",
        "2 Boiled Eggs (100g) + 1 Bowl of Sprouts Salad (150g)",
        "1 Bottle of Coca-Cola (330ml) + 1 Kurkure Pack (50g)"
    ])

    # Convert simulation to consumed nutrients
    if "Lay's" in sim_snack:
        sim_items = [
            {"food_name": "Lay's Chips (50g)", "meal_type": "Snacks", "calories": 270, "protein": 3.4, "carbs": 27, "fat": 17, "fiber": 1.7, "sugar": 2.2, "sodium": 410},
            {"food_name": "Cadbury Chocolate (25g)", "meal_type": "Snacks", "calories": 135, "protein": 1.9, "carbs": 15, "fat": 7.6, "fiber": 0.5, "sugar": 14.2, "sodium": 35}
        ]
    elif "Samosa" in sim_snack:
        sim_items = [
            {"food_name": "Samosa (80g)", "meal_type": "Snacks", "calories": 310, "protein": 4.5, "carbs": 32, "fat": 18, "fiber": 2.8, "sugar": 1.8, "sodium": 420},
            {"food_name": "Sweet Lassi (200ml)", "meal_type": "Snacks", "calories": 155, "protein": 4.2, "carbs": 24, "fat": 4.5, "fiber": 0.0, "sugar": 22.0, "sodium": 65}
        ]
    elif "Boiled Eggs" in sim_snack:
        sim_items = [
            {"food_name": "Boiled Eggs (2 pcs)", "meal_type": "Breakfast", "calories": 155, "protein": 12.6, "carbs": 1.1, "fat": 10.6, "fiber": 0.0, "sugar": 1.1, "sodium": 124},
            {"food_name": "Moong Sprouts (150g)", "meal_type": "Breakfast", "calories": 45, "protein": 4.5, "carbs": 8.8, "fat": 0.3, "fiber": 2.7, "sugar": 6.1, "sodium": 22}
        ]
    else:
        sim_items = [
            {"food_name": "Coca-Cola (330ml)", "meal_type": "Snacks", "calories": 139, "protein": 0.0, "carbs": 35.0, "fat": 0.0, "fiber": 0.0, "sugar": 35.0, "sodium": 13},
            {"food_name": "Kurkure (50g)", "meal_type": "Snacks", "calories": 280, "protein": 2.9, "carbs": 28.2, "fat": 17.4, "fiber": 1.1, "sugar": 1.9, "sodium": 445}
        ]

    st.markdown("<div class='nutri-card-glow'>", unsafe_allow_html=True)
    dyn_eval = generate_dynamic_adjustment_recommendations(sim_items, targets, user_profile['dietary_preference'])
    
    tot_s_cal = sum(x['calories'] for x in sim_items)
    tot_s_sug = sum(x['sugar'] for x in sim_items)
    tot_s_fat = sum(x['fat'] for x in sim_items)

    st.markdown(f"#### 💡 Simulated Consumption Impact ({tot_s_cal} kcal, {tot_s_fat}g fat, {tot_s_sug}g sugar)")
    st.write(f"**NutriFit AI Evaluation:** {dyn_eval['clinical_rationale']}")
    
    st.markdown("##### Recommended Next Meal Counterbalances:")
    cols = st.columns(len(dyn_eval['suggested_foods']))
    for i, sf in enumerate(dyn_eval['suggested_foods']):
        with cols[i]:
            st.markdown(f"""
            <div style="background:#21262D; padding:12px; border-radius:8px; border-top:3px solid #00E676; min-height:110px;">
                <div style="font-weight:700; color:#FFFFFF;">{sf['food_name']}</div>
                <div style="font-size:11px; color:#8B949E; margin-top:4px;">{sf['benefit']}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TAB 4: K-MEANS CLUSTERS -----------------
with tabs[3]:
    st.markdown("### 🌐 Model 3: K-Means Nutritional Clustering Explorer")
    st.markdown("The K-Means clustering algorithm partitions 29,000+ foods into 6 distinct nutritional archetypes based on their normalized macronutrient vectors.")

    if os.path.exists("models/cluster_names.pkl"):
        cluster_names = joblib.load("models/cluster_names.pkl")
        sel_c = st.selectbox("Select Cluster to Explore:", list(cluster_names.keys()), format_func=lambda cid: f"Cluster {cid}: {cluster_names[cid]}")

        # Show sample foods in this cluster
        if 'cluster_id' in df_foods.columns:
            c_foods = df_foods[df_foods['cluster_id'] == sel_c].head(15)[['food_name', 'category', 'calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar']]
            st.dataframe(c_foods, use_container_width=True, hide_index=True)
        else:
            st.info("Cluster data ready.")

st.markdown(render_disclaimer(), unsafe_allow_html=True)

