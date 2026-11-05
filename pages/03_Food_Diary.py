"""
NutriFit AI - Page 3: Food Diary & Consumption Tracker
Records and aggregates daily meals (Breakfast, Lunch, Snacks, Dinner),
calculates remaining allowances, and dynamically flags imbalances.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.database import get_session, User, FoodLog, FoodItem, FoodNutrition
from src.nutrition_engine import calculate_daily_targets
from src.calorie_calculator import calculate_daily_balance
from src.recommendation_engine import generate_dynamic_adjustment_recommendations
from utils.helpers import inject_custom_css, render_disclaimer

st.set_page_config(page_title="NutriFit AI - Food Diary", page_icon="📖", layout="wide")
st.markdown(inject_custom_css(), unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

st.title("📖 Daily Food Diary & Consumption Tracker")
st.markdown("Review and record what you eat across Breakfast, Lunch, Snacks, and Dinner with real-time balance calculations.")

# Date picker for tracking
selected_date = st.date_input("Select Diary Date", value=date.today())
start_dt = datetime.combine(selected_date, datetime.min.time())
end_dt = datetime.combine(selected_date, datetime.max.time())

session = get_session()
try:
    user = session.query(User).filter_by(user_id=st.session_state.user_id).first()
    p = user.profile if user else None

    age = p.age if p else 22
    sex = p.sex if p else "Male"
    height = p.height if p else 170.0
    weight = p.weight if p else 65.0
    activity = p.activity_level if p else "Moderately active"
    goal = p.goal if p else "Weight Gain"
    dietary_pref = p.dietary_preference if p else "Vegetarian"

    targets = calculate_daily_targets(weight, height, age, sex, activity, goal)

    logs = session.query(FoodLog).filter(
        FoodLog.user_id == st.session_state.user_id,
        FoodLog.consumed_at >= start_dt,
        FoodLog.consumed_at <= end_dt
    ).order_by(FoodLog.consumed_at.asc()).all()

    consumed_items = []
    for log in logs:
        item = log.food_item
        nutr = item.nutrition if item else None
        scale = log.quantity / 100.0
        if nutr:
            consumed_items.append({
                "log_id": log.log_id,
                "food_id": item.food_id,
                "food_name": item.name,
                "meal_type": log.meal_type,
                "quantity": log.quantity,
                "calories": round(nutr.calories * scale, 1),
                "protein": round(nutr.protein * scale, 1),
                "carbs": round(nutr.carbs * scale, 1),
                "fat": round(nutr.fat * scale, 1),
                "saturated_fat": round(nutr.saturated_fat * scale, 1),
                "fiber": round(nutr.fibre * scale, 1),
                "sugar": round(nutr.sugar * scale, 1),
                "sodium": round(nutr.sodium * scale, 1),
                "consumed_at": log.consumed_at.strftime("%H:%M")
            })
finally:
    session.close()

balance = calculate_daily_balance(consumed_items, targets)

# Top KPI progress bar row
k1, k2, k3, k4, k5 = st.columns(5)
c_cals = balance['consumed']['calories']
t_cals = targets['target_calories']
rem_cals = balance['remaining']['calories']

k1.metric("Calories Consumed", f"{c_cals:.0f} kcal", f"{t_cals:.0f} target")
k2.metric("Protein", f"{balance['consumed']['protein']:.1f} g", f"{targets['target_protein_g']:.0f}g target")
k3.metric("Carbohydrates", f"{balance['consumed']['carbs']:.1f} g", f"{targets['target_carbs_g']:.0f}g target")
k4.metric("Total Fat", f"{balance['consumed']['fat']:.1f} g", f"{targets['target_fat_g']:.0f}g target")
k5.metric("Remaining Energy", f"{rem_cals:.0f} kcal")

st.markdown("---")

# Quick Add Custom / Preset Meal
with st.expander("➕ Log a Quick Food or Snack into Today's Diary", expanded=not bool(consumed_items)):
    col_a1, col_a2, col_a3, col_a4 = st.columns([2, 1, 1, 1])
    with col_a1:
        # Search food from DB
        session = get_session()
        try:
            food_options = session.query(FoodItem.food_id, FoodItem.name).order_by(FoodItem.name.asc()).limit(300).all()
            food_dict = {f.name: f.food_id for f in food_options}
            chosen_food_name = st.selectbox("Select Food:", list(food_dict.keys()))
            chosen_food_id = food_dict[chosen_food_name]
        finally:
            session.close()
    with col_a2:
        meal_type = st.selectbox("Meal Category:", ["Breakfast", "Lunch", "Snacks", "Dinner"])
    with col_a3:
        logged_qty = st.number_input("Quantity (g / ml):", min_value=5.0, max_value=1500.0, value=100.0, step=10.0)
    with col_a4:
        st.write("")
        st.write("")
        if st.button("Log Food", type="primary", use_container_width=True):
            session = get_session()
            try:
                session.add(FoodLog(
                    user_id=st.session_state.user_id,
                    food_id=chosen_food_id,
                    quantity=logged_qty,
                    meal_type=meal_type,
                    consumed_at=datetime.combine(selected_date, datetime.now().time())
                ))
                session.commit()
                st.success(f"Logged {logged_qty}g of {chosen_food_name}!")
                st.rerun()
            finally:
                session.close()

# Categorized Meals Breakdown
st.markdown("### 🍽️ Meals Recorded for " + selected_date.strftime("%A, %B %d, %Y"))

if not consumed_items:
    st.info("No meals recorded yet for this date. Log your breakfast, lunch, snacks or dinner above!")
else:
    meal_categories = ["Breakfast", "Lunch", "Snacks", "Dinner"]
    
    for meal in meal_categories:
        m_items = [x for x in consumed_items if x['meal_type'] == meal]
        m_cal = sum(x['calories'] for x in m_items)
        m_pro = sum(x['protein'] for x in m_items)
        m_carb = sum(x['carbs'] for x in m_items)
        m_fat = sum(x['fat'] for x in m_items)

        st.markdown(f"#### {meal} <span style='font-size:14px; color:#8B949E;'>({m_cal:.0f} kcal | P: {m_pro:.1f}g | C: {m_carb:.1f}g | F: {m_fat:.1f}g)</span>", unsafe_allow_html=True)
        
        if not m_items:
            st.caption(f"No {meal.lower()} logged yet.")
        else:
            for item in m_items:
                col_i1, col_i2, col_i3, col_i4, col_i5, col_del = st.columns([3, 1.2, 1.2, 1.2, 1.2, 0.8])
                col_i1.markdown(f"**{item['food_name']}** ({item['quantity']:.0f}g)")
                col_i2.write(f"🔥 {item['calories']:.0f} kcal")
                col_i3.write(f"🍗 {item['protein']:.1f}g pro")
                col_i4.write(f"🍞 {item['carbs']:.1f}g carb")
                col_i5.write(f"🥑 {item['fat']:.1f}g fat")
                
                if col_del.button("🗑️", key=f"del_{item['log_id']}", help="Delete item"):
                    session = get_session()
                    try:
                        session.query(FoodLog).filter_by(log_id=item['log_id']).delete()
                        session.commit()
                        st.toast("Item removed!")
                        st.rerun()
                    finally:
                        session.close()
        st.markdown("<hr style='margin: 8px 0; border-color:#21262D;'>", unsafe_allow_html=True)

# Dynamic AI Dietary Adjustment Section
st.markdown("<div class='nutri-card-glow'>", unsafe_allow_html=True)
st.markdown("### 🧠 Continuous AI Adaptation Engine")

dyn = generate_dynamic_adjustment_recommendations(consumed_items, targets, dietary_pref)
st.write(dyn['clinical_rationale'])

c_r1, c_r2, c_r3 = st.columns(3)
c_r1.metric("Remaining Calories", f"{dyn['remaining_calories']:.0f} kcal")
c_r2.metric("Remaining Protein Goal", f"{dyn['remaining_protein']:.1f} g")
c_r3.metric("Remaining Fiber Goal", f"{dyn['remaining_fiber']:.1f} g")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(render_disclaimer(), unsafe_allow_html=True)

