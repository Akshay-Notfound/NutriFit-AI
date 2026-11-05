"""
NutriFit AI - Page 5: Personalized Diet Planner
Generates structured, clinically balanced daily and 7-day weekly meal plans
featuring authentic Indian food intelligence and continuous dynamic adjustments.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.database import get_session, User, DietPlan, DietPlanItem, FoodItem, FoodLog
from src.nutrition_engine import calculate_daily_targets
from src.diet_planner import generate_daily_plan, generate_weekly_plan
from utils.helpers import inject_custom_css, render_disclaimer

st.set_page_config(page_title="NutriFit AI - Diet Planner", page_icon="🍱", layout="wide")
st.markdown(inject_custom_css(), unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

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

    # Fetch today's logged food items to enable dynamic adjustment
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    today_logs = session.query(FoodLog).filter(
        FoodLog.user_id == st.session_state.user_id,
        FoodLog.consumed_at >= today_start,
        FoodLog.consumed_at <= today_end
    ).all()

    consumed_today = []
    for log in today_logs:
        it = log.food_item
        nu = it.nutrition if it else None
        if nu:
            sc = log.quantity / 100.0
            consumed_today.append({
                "food_name": it.name,
                "calories": nu.calories * sc,
                "protein": nu.protein * sc,
                "fat": nu.fat * sc,
                "sugar": nu.sugar * sc
            })
finally:
    session.close()

st.title("🍱 Personalized Diet Planner")
st.markdown("Generates evidence-based, culturally tailored daily and weekly meal plans with dynamic adjustment based on what you actually consume.")

col_c1, col_c2, col_c3 = st.columns([1, 1, 1.2])
with col_c1:
    target_cals = st.number_input("Target Daily Calories (kcal):", min_value=1200.0, max_value=4500.0, value=float(targets['target_calories']), step=50.0)
with col_c2:
    selected_pref = st.selectbox("Dietary Preference:", ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"], index=["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"].index(dietary_pref))
with col_c3:
    adjust_for_diary = st.checkbox("⚡ Apply Dynamic Adjustment (Factor in today's logged food diary)", value=bool(consumed_today))

# Inform user of already consumed calories if dynamic adjustment is enabled
if adjust_for_diary and consumed_today:
    c_cal = sum(x['calories'] for x in consumed_today)
    st.info(f"💡 You have already consumed **{c_cal:.0f} kcal** today. The daily planner will recalibrate remaining meal portions automatically.")

plan_tabs = st.tabs(["📅 Today's Optimized Meal Plan", "📆 7-Day Weekly Meal Schedule"])

# ----------------- TAB 1: DAILY MEAL PLAN -----------------
with plan_tabs[0]:
    day_plan = generate_daily_plan(
        target_calories=target_cals,
        dietary_preference=selected_pref,
        goal=goal,
        consumed_today=consumed_today if adjust_for_diary else None
    )

    if day_plan.get("dynamic_note"):
        st.markdown(f"<div class='badge-warning' style='margin-bottom:12px;'>{day_plan['dynamic_note']}</div>", unsafe_allow_html=True)

    # Top Macro Summary of Plan
    m_p1, m_p2, m_p3, m_p4 = st.columns(4)
    m_p1.metric("Planned Calories", f"{day_plan['planned_calories']:.0f} kcal", f"Goal: {target_cals:.0f}")
    m_p2.metric("Total Protein", f"{day_plan['total_protein']:.1f} g")
    m_p3.metric("Total Carbohydrates", f"{day_plan['total_carbs']:.1f} g")
    m_p4.metric("Total Dietary Fiber", f"{day_plan['total_fiber']:.1f} g", "WHO goal: ≥25g")

    st.markdown("---")
    meal_icons = {"Breakfast": "🥞", "Lunch": "🍛", "Evening Snack": "☕", "Dinner": "🍲"}

    for m_type, m_info in day_plan["meals"].items():
        st.markdown(f"""
        <div class='nutri-card'>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:16px; font-weight:700; color:#FFFFFF;">{meal_icons.get(m_type, '🍽️')} {m_type}</span>
                <span style="font-weight:700; color:#00E676;">{m_info['calories']:.0f} kcal</span>
            </div>
            <div style="font-size:15px; color:#E6EDF3; margin-top:8px; font-weight:600;">{m_info['name']}</div>
            <div style="font-size:12px; color:#8B949E; margin-top:6px;">
                🍗 Protein: <strong>{m_info['protein']:.1f}g</strong> | 🍞 Carbs: <strong>{m_info['carbs']:.1f}g</strong> | 🥑 Fat: <strong>{m_info['fat']:.1f}g</strong> | 🌾 Fiber: <strong>{m_info['fiber']:.1f}g</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Save to Database Button
    if st.button("💾 Save this Diet Plan to My Account", type="primary"):
        session = get_session()
        try:
            dp = DietPlan(
                user_id=st.session_state.user_id,
                date=date.today(),
                goal=goal,
                calorie_target=target_cals
            )
            session.add(dp)
            session.commit()
            st.success("✅ Diet Plan successfully saved to database!")
        except Exception as e:
            session.rollback()
            st.error(f"Error saving diet plan: {e}")
        finally:
            session.close()

# ----------------- TAB 2: WEEKLY MEAL SCHEDULE -----------------
with plan_tabs[1]:
    st.markdown("### 📆 7-Day Indian Cultural Meal Plan")
    st.markdown("Nutritionally balanced, rotated schedule respecting traditional combinations (Roti + Dal + Sabzi + Curd, Idli Sambar, Sprouts, etc.).")

    weekly = generate_weekly_plan(target_cals, selected_pref, goal)

    for day in weekly:
        with st.expander(f"📌 {day['day_name']} — {day['planned_calories']:.0f} kcal (Protein: {day['total_protein']:.0f}g, Carbs: {day['total_carbs']:.0f}g, Fat: {day['total_fat']:.0f}g)"):
            for m_type, m_info in day['meals'].items():
                st.markdown(f"**{m_type} ({m_info['calories']:.0f} kcal):** {m_info['name']}")
                st.caption(f"P: {m_info['protein']:.1f}g | C: {m_info['carbs']:.1f}g | F: {m_info['fat']:.1f}g | Fiber: {m_info['fiber']:.1f}g")

st.markdown(render_disclaimer(), unsafe_allow_html=True)

