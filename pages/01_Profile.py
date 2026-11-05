"""
NutriFit AI - Page 1: User Profile & Body Analysis
Manages biometric details, dietary constraints, and computes Mifflin-St Jeor BMR, TDEE, and BMI.
"""

import streamlit as st
import pandas as pd
from src.database import get_session, User, UserProfile, WeightHistory
from src.nutrition_engine import calculate_daily_targets, calculate_bmi, calculate_bmr, calculate_tdee
from utils.helpers import inject_custom_css, render_disclaimer

st.set_page_config(page_title="NutriFit AI - User Profile", page_icon="👤", layout="wide")
st.markdown(inject_custom_css(), unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

session = get_session()
try:
    user = session.query(User).filter_by(user_id=st.session_state.user_id).first()
    p = user.profile if user else None

    curr_name = user.name if user else "Rahul Sharma"
    curr_email = user.email if user else "demo@nutrifit.ai"
    curr_age = p.age if p else 22
    curr_sex = p.sex if p else "Male"
    curr_height = p.height if p else 170.0
    curr_weight = p.weight if p else 65.0
    curr_act = p.activity_level if p else "Moderately active"
    curr_goal = p.goal if p else "Weight Gain"
    curr_target_w = p.target_weight if p and p.target_weight else 70.0
    curr_diet = p.dietary_preference if p else "Vegetarian"
    curr_allergies = p.allergies if p else "None"
finally:
    session.close()

st.title("👤 User Profile & Body Composition Analysis")
st.markdown("Configure your physical characteristics, metabolic parameters, and fitness objectives.")

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
    st.markdown("### Personal & Biometric Details")
    
    name = st.text_input("Full Name", value=curr_name)
    email = st.text_input("Email Address", value=curr_email)
    
    c_a, c_s = st.columns(2)
    with c_a:
        age = st.number_input("Age (years)", min_value=18, max_value=100, value=int(curr_age))
    with c_s:
        sex = st.selectbox("Biological Sex (required for BMR equation)", ["Male", "Female"], index=0 if curr_sex=="Male" else 1)

    c_h, c_w = st.columns(2)
    with c_h:
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(curr_height), step=0.5)
    with c_w:
        weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=250.0, value=float(curr_weight), step=0.5)

    c_goal, c_targ = st.columns(2)
    with c_goal:
        goal_options = ["Weight Loss", "Maintenance", "Weight Gain"]
        goal = st.selectbox("Fitness Goal", goal_options, index=goal_options.index(curr_goal) if curr_goal in goal_options else 2)
    with c_targ:
        target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=250.0, value=float(curr_target_w), step=0.5)

    activity_options = ["Sedentary", "Lightly active", "Moderately active", "Very active", "Extra active"]
    activity_level = st.selectbox(
        "Activity Level",
        activity_options,
        index=activity_options.index(curr_act) if curr_act in activity_options else 2,
        help="Sedentary (desk job), Lightly active (1-3 days exercise), Moderately active (3-5 days), Very active (6-7 days)"
    )

    c_diet, c_al = st.columns(2)
    with c_diet:
        diet_options = ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"]
        dietary_preference = st.selectbox("Dietary Preference", diet_options, index=diet_options.index(curr_diet) if curr_diet in diet_options else 0)
    with c_al:
        allergies = st.text_input("Allergies & Sensitivities (e.g. Peanuts, Gluten, Dairy)", value=curr_allergies)

    if st.button("💾 Save Profile Changes", use_container_width=True, type="primary"):
        session = get_session()
        try:
            u = session.query(User).filter_by(user_id=st.session_state.user_id).first()
            if u:
                u.name = name.strip()
                u.email = email.strip()
                if u.profile:
                    u.profile.age = age
                    u.profile.sex = sex
                    u.profile.height = height
                    u.profile.weight = weight
                    u.profile.activity_level = activity_level
                    u.profile.goal = goal
                    u.profile.target_weight = target_weight
                    u.profile.dietary_preference = dietary_preference
                    u.profile.allergies = allergies
                session.commit()
                st.success("✅ Profile updated successfully! Formulas recalculated.")
                st.rerun()
        finally:
            session.close()
    st.markdown("</div>", unsafe_allow_html=True)

# Right Column: Real-time Scientific Calculations & Formulas
with col2:
    targets = calculate_daily_targets(weight, height, age, sex, activity_level, goal)
    
    st.markdown("<div class='nutri-card-glow'>", unsafe_allow_html=True)
    st.markdown("### 🔬 Real-Time Clinical Nutrition Metrics")

    # BMI Card
    st.markdown(f"#### 1. Body Mass Index (BMI): **{targets['bmi']}**")
    cat_badge = "badge-success" if targets['bmi_category'] == "Normal weight" else "badge-warning"
    st.markdown(f"Classification: <span class='{cat_badge}'>{targets['bmi_category']}</span>", unsafe_allow_html=True)
    st.caption(f"Healthy weight reference for your height: **{targets['healthy_weight_range'][0]} kg – {targets['healthy_weight_range'][1]} kg**")
    st.markdown(f"<span style='font-size:12px; color:#8B949E;'>Formula: BMI = Weight(kg) / (Height(m))² = {weight:.1f} / ({height/100:.2f})²</span>", unsafe_allow_html=True)

    st.markdown("---")
    # BMR Card
    st.markdown(f"#### 2. Basal Metabolic Rate (BMR): **{int(targets['bmr'])} kcal**")
    st.caption("Estimated energy expended at complete rest via Mifflin-St Jeor equation:")
    if sex == "Male":
        st.markdown(f"<span style='font-size:11px; color:#8B949E;'>BMR = 10 × {weight:.1f} + 6.25 × {height:.1f} - 5 × {age} + 5</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='font-size:11px; color:#8B949E;'>BMR = 10 × {weight:.1f} + 6.25 × {height:.1f} - 5 × {age} - 161</span>", unsafe_allow_html=True)

    st.markdown("---")
    # TDEE Card
    st.markdown(f"#### 3. Total Daily Energy Expenditure (TDEE): **{int(targets['tdee'])} kcal**")
    st.caption(f"TDEE = BMR × Activity Factor ({activity_level})")

    st.markdown("---")
    # Calorie & Macro Target Card
    st.markdown(f"#### 4. Calibrated Daily Target: **{int(targets['target_calories'])} kcal**")
    st.markdown(f"**Goal:** `{goal}` (Target Protein: `{targets['target_protein_g']}g`, Carbs: `{targets['target_carbs_g']}g`, Fat: `{targets['target_fat_g']}g`)")
    
    st.markdown("##### Micronutrient & Health Ceilings:")
    st.write(f"- 🌾 **Dietary Fiber:** ≥ {targets['target_fiber_g']}g / day (WHO guideline)")
    st.write(f"- 🍬 **Added Sugar Ceiling:** < {targets['sugar_limit_g']}g / day")
    st.write(f"- 🧂 **Sodium Ceiling:** < {targets['sodium_limit_mg']}mg / day")
    st.write(f"- 💧 **Recommended Water:** ~{targets['target_water_l']} Liters / day")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(render_disclaimer(), unsafe_allow_html=True)

