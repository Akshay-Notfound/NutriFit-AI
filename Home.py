"""
NutriFit AI - Home Dashboard
Smart Food Analyzer & Personalized Diet Recommendation System
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

# Configure page
st.set_page_config(
    page_title="NutriFit AI - Smart Food & Diet System",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.database import init_db, get_session, User, UserProfile, FoodLog, FoodItem, FoodNutrition, WeightHistory
from src.nutrition_engine import calculate_daily_targets, calculate_bmi
from src.calorie_calculator import calculate_daily_balance
from src.recommendation_engine import generate_dynamic_adjustment_recommendations
from utils.charts import (
    create_circular_calorie_gauge, create_macro_gauge,
    create_weight_trend_chart, create_nutrients_bar_chart
)
from utils.authentication import get_or_create_demo_user
from utils.helpers import inject_custom_css, render_disclaimer

# Inject dark obsidian styling
st.markdown(inject_custom_css(), unsafe_allow_html=True)

# Initialize database
init_db()

# Session State for User
if "user_id" not in st.session_state:
    st.session_state.user_id = get_or_create_demo_user()

session = get_session()
try:
    user = session.query(User).filter_by(user_id=st.session_state.user_id).first()
    profile = user.profile if user else None
    
    # Default profile values if not yet set
    user_name = user.name if user else "Athlete"
    age = profile.age if profile else 22
    sex = profile.sex if profile else "Male"
    height = profile.height if profile else 170.0
    weight = profile.weight if profile else 65.0
    activity = profile.activity_level if profile else "Moderately active"
    goal = profile.goal if profile else "Weight Gain"
    dietary_pref = profile.dietary_preference if profile else "Vegetarian"

    # Calculate nutritional targets
    targets = calculate_daily_targets(weight, height, age, sex, activity, goal)

    # Fetch today's food logs
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    logs = session.query(FoodLog).filter(
        FoodLog.user_id == st.session_state.user_id,
        FoodLog.consumed_at >= today_start,
        FoodLog.consumed_at <= today_end
    ).all()

    consumed_items = []
    for log in logs:
        item = log.food_item
        nutr = item.nutrition if item else None
        scale = log.quantity / 100.0
        if nutr:
            consumed_items.append({
                "log_id": log.log_id,
                "food_name": item.name,
                "meal_type": log.meal_type,
                "quantity": log.quantity,
                "calories": nutr.calories * scale,
                "protein": nutr.protein * scale,
                "carbs": nutr.carbs * scale,
                "fat": nutr.fat * scale,
                "saturated_fat": nutr.saturated_fat * scale,
                "fiber": nutr.fibre * scale,
                "sugar": nutr.sugar * scale,
                "sodium": nutr.sodium * scale,
                "calcium": nutr.calcium * scale,
                "iron": nutr.iron * scale,
                "vitamin_c": nutr.vitamin_c * scale
            })

    # Fetch weight history
    wh_records = session.query(WeightHistory).filter_by(user_id=st.session_state.user_id).order_by(WeightHistory.recorded_at.asc()).all()
    weight_history = [{"weight": r.weight, "recorded_at": r.recorded_at} for r in wh_records]

finally:
    session.close()

# Compute real-time balance
balance = calculate_daily_balance(consumed_items, targets)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### 🥗 **NutriFit AI**")
    st.markdown(f"**User:** `{user_name}`")
    st.markdown(f"**Goal:** `{goal}` | **Diet:** `{dietary_pref}`")
    st.markdown("---")

    st.markdown("#### ⚡ Daily Energy Budget")
    c_cal = balance['consumed']['calories']
    t_cal = targets['target_calories']
    pct_cal = balance['percentages']['calories']
    st.markdown(f"**{c_cal:.0f} kcal** consumed ({pct_cal:.1f}% of {t_cal:.0f} kcal target)")
    st.progress(min(1.0, c_cal / max(t_cal, 1.0)))

    rem = balance['remaining']['calories']
    if rem > 0:
        st.caption(f"🔥 Remaining energy allowance: **{rem:.0f} kcal**")
    else:
        st.caption(f"⚠️ Calorie target exceeded by **{abs(rem):.0f} kcal**")

    st.markdown("---")
    st.markdown("#### 📌 Quick Switch Demo Profile")
    quick_user = st.selectbox("Select Active Profile", ["Rahul Sharma (22M, Gain, 65kg)", "Ananya Iyer (26F, Loss, 68kg)", "Priya Patel (30F, Maint, 58kg)"])
    if st.button("Apply Profile Archetype", use_container_width=True):
        session = get_session()
        try:
            p = session.query(UserProfile).filter_by(user_id=st.session_state.user_id).first()
            if p:
                if "Rahul" in quick_user:
                    p.age, p.sex, p.height, p.weight, p.goal = 22, "Male", 170.0, 65.0, "Weight Gain"
                elif "Ananya" in quick_user:
                    p.age, p.sex, p.height, p.weight, p.goal = 26, "Female", 162.0, 68.0, "Weight Loss"
                else:
                    p.age, p.sex, p.height, p.weight, p.goal = 30, "Female", 165.0, 58.0, "Maintenance"
                session.commit()
                st.success("Profile updated! Refreshing dashboard...")
                st.rerun()
        finally:
            session.close()

# ----------------- MAIN DASHBOARD -----------------
st.title("NutriFit AI: Smart Food & Nutrition Dashboard")
st.markdown("An intelligent machine learning system that analyzes daily food consumption, evaluates nutritional impact, and dynamically adapts recommendations.")

# Top Summary KPI Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(
        label="BMI Screening",
        value=f"{targets['bmi']}",
        delta=f"{targets['bmi_category']}",
        delta_color="normal" if targets['bmi_category'] == "Normal weight" else "off"
    )
with kpi2:
    st.metric(label="Basal Metabolic Rate (BMR)", value=f"{int(targets['bmr'])} kcal")
with kpi3:
    st.metric(label="Total Daily Energy (TDEE)", value=f"{int(targets['tdee'])} kcal")
with kpi4:
    adj = int(targets['target_calories'] - targets['tdee'])
    st.metric(
        label="Daily Energy Target",
        value=f"{int(targets['target_calories'])} kcal",
        delta=f"{adj:+d} kcal ({goal})"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Main UI Card Section: Calories Gauge + Weight Curve (Inspired by user wireframe)
col_left, col_right = st.columns([1, 1.3])

with col_left:
    st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
    st.markdown("#### 🎯 Daily Calorie Progress")
    fig_gauge = create_circular_calorie_gauge(
        balance['consumed']['calories'],
        targets['target_calories']
    )
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("Consumed", f"{int(balance['consumed']['calories'])} kcal")
    col_c2.metric("Target", f"{int(targets['target_calories'])} kcal")
    col_c3.metric("Remaining", f"{int(balance['remaining']['calories'])} kcal")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
    st.markdown("#### 📈 Body Weight Trend (kg)")
    fig_weight = create_weight_trend_chart(weight_history)
    st.plotly_chart(fig_weight, use_container_width=True, config={'displayModeBar': False})
    
    w_curr = weight_history[-1]['weight'] if weight_history else weight
    w_start = weight_history[0]['weight'] if weight_history else weight
    col_w1, col_w2, col_w3 = st.columns(3)
    col_w1.metric("Current", f"{w_curr:.1f} kg")
    col_w2.metric("Initial", f"{w_start:.1f} kg")
    col_w3.metric("Target", f"{profile.target_weight if profile and profile.target_weight else weight:.1f} kg")
    st.markdown("</div>", unsafe_allow_html=True)

# Row 2: Macros Triple Rings + Nutrients Bar
col_m1, col_m2 = st.columns([1.1, 1.1])

with col_m1:
    st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
    st.markdown("#### 🍳 Macronutrient Distribution")
    sub1, sub2, sub3 = st.columns(3)
    with sub1:
        st.markdown("<div style='text-align:center; font-weight:600; color:#00E676;'>PROTEIN</div>", unsafe_allow_html=True)
        fig_pro = create_macro_gauge("Protein", balance['consumed']['protein'], targets['target_protein_g'], "#00E676")
        st.plotly_chart(fig_pro, use_container_width=True, config={'displayModeBar': False})
    with sub2:
        st.markdown("<div style='text-align:center; font-weight:600; color:#00E5FF;'>CARBS</div>", unsafe_allow_html=True)
        fig_carb = create_macro_gauge("Carbs", balance['consumed']['carbs'], targets['target_carbs_g'], "#00E5FF")
        st.plotly_chart(fig_carb, use_container_width=True, config={'displayModeBar': False})
    with sub3:
        st.markdown("<div style='text-align:center; font-weight:600; color:#FF9100;'>FAT</div>", unsafe_allow_html=True)
        fig_fat = create_macro_gauge("Fat", balance['consumed']['fat'], targets['target_fat_g'], "#FF9100")
        st.plotly_chart(fig_fat, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with col_m2:
    st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
    st.markdown("#### 🥦 Essential Nutrients & Health Limits (% RDA)")
    fig_nutr = create_nutrients_bar_chart(balance['consumed'], targets)
    st.plotly_chart(fig_nutr, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# Row 3: AI Dynamic Insight & Food Diary Highlights
st.markdown("<div class='nutri-card-glow'>", unsafe_allow_html=True)
st.markdown("### 🤖 NutriFit AI Dynamic Nutritional Evaluation")

dyn_recs = generate_dynamic_adjustment_recommendations(consumed_items, targets, dietary_pref)
st.write(dyn_recs['clinical_rationale'])

if dyn_recs['suggested_foods']:
    st.markdown("**Recommended foods to balance your remaining meals today:**")
    rec_cols = st.columns(len(dyn_recs['suggested_foods']))
    for idx, f in enumerate(dyn_recs['suggested_foods']):
        with rec_cols[idx]:
            st.markdown(f"""
            <div style="background:#21262D; padding:10px; border-radius:8px; border-top:3px solid #00E676; min-height:100px;">
                <div style="font-weight:700; font-size:13px; color:#FFF;">{f['food_name']}</div>
                <div style="font-size:11px; color:#8B949E;">{f['benefit']}</div>
            </div>
            """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Row 4: Today's Food Diary Snapshot
st.markdown("### 📖 Today's Food Log Snapshot")
if not consumed_items:
    st.info("No meals or snacks logged yet today! Click **'Food Diary'** or **'Food Analyzer'** in the sidebar to log what you eat, or load our demo snack consumption below.")
    if st.button("🍽️ Load Demo Consumption (Lay's Chips 50g + Cadbury Chocolate 25g)"):
        session = get_session()
        try:
            # Add chips
            chips = session.query(FoodItem).filter(FoodItem.name.like("%Lay's India's Magic Masala%")).first()
            choc = session.query(FoodItem).filter(FoodItem.name.like("%Cadbury Dairy Milk%")).first()
            if chips:
                session.add(FoodLog(user_id=st.session_state.user_id, food_id=chips.food_id, quantity=50.0, meal_type="Snacks"))
            if choc:
                session.add(FoodLog(user_id=st.session_state.user_id, food_id=choc.food_id, quantity=25.0, meal_type="Snacks"))
            session.commit()
            st.success("Demo snacks logged! Recalculating dashboard...")
            st.rerun()
        finally:
            session.close()
else:
    df_logs = pd.DataFrame(consumed_items)[['meal_type', 'food_name', 'quantity', 'calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']]
    df_logs.columns = ['Meal', 'Food Item', 'Qty (g)', 'Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Fiber (g)', 'Sugar (g)', 'Sodium (mg)']
    st.dataframe(df_logs, use_container_width=True, hide_index=True)

# Clinical disclaimer
st.markdown(render_disclaimer(), unsafe_allow_html=True)

