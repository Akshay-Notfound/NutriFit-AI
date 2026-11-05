"""
NutriFit AI - Page 7: Analytics Reports & Document Exports
Generates downloadable PDF clinical nutrition summaries, CSV food log exports,
and WHO dietary guideline compliance audits.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from src.database import get_session, User, FoodLog
from src.nutrition_engine import calculate_daily_targets
from src.calorie_calculator import calculate_daily_balance
from utils.helpers import inject_custom_css, render_disclaimer, generate_pdf_report

st.set_page_config(page_title="NutriFit AI - Reports & Exports", page_icon="📄", layout="wide")
st.markdown(inject_custom_css(), unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

session = get_session()
try:
    user = session.query(User).filter_by(user_id=st.session_state.user_id).first()
    p = user.profile if user else None

    user_name = user.name if user else "Rahul Sharma"
    user_email = user.email if user else "demo@nutrifit.ai"
    profile_dict = {
        "name": user_name,
        "age": p.age if p else 22,
        "sex": p.sex if p else "Male",
        "height": p.height if p else 170.0,
        "weight": p.weight if p else 65.0,
        "activity_level": p.activity_level if p else "Moderately active",
        "goal": p.goal if p else "Weight Gain",
        "dietary_preference": p.dietary_preference if p else "Vegetarian"
    }

    targets = calculate_daily_targets(
        profile_dict['weight'], profile_dict['height'],
        profile_dict['age'], profile_dict['sex'],
        profile_dict['activity_level'], profile_dict['goal']
    )

    # Fetch all logs
    all_logs = session.query(FoodLog).filter_by(user_id=st.session_state.user_id).order_by(FoodLog.consumed_at.desc()).all()
    food_logs = []
    for log in all_logs:
        it = log.food_item
        nu = it.nutrition if it else None
        if nu:
            sc = log.quantity / 100.0
            food_logs.append({
                "meal_type": log.meal_type,
                "food_name": it.name,
                "quantity": log.quantity,
                "calories": round(nu.calories * sc, 1),
                "protein": round(nu.protein * sc, 1),
                "carbs": round(nu.carbs * sc, 1),
                "fat": round(nu.fat * sc, 1),
                "fiber": round(nu.fibre * sc, 1),
                "sugar": round(nu.sugar * sc, 1),
                "sodium": round(nu.sodium * sc, 1),
                "consumed_at": log.consumed_at.strftime("%Y-%m-%d %H:%M")
            })
finally:
    session.close()

balance = calculate_daily_balance(food_logs, targets)

st.title("📄 Clinical Reports & Data Exports")
st.markdown("Generate and download comprehensive dietitian-ready PDF summaries, export tabular consumption history, and verify guideline compliance.")

col_rep1, col_rep2 = st.columns([1.2, 1])

# Left: WHO Dietary Guidelines Compliance Audit
with col_rep1:
    st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
    st.markdown("### 🌐 WHO Dietary Guidelines Compliance Audit")
    st.caption("Benchmarking your consumption against World Health Organization (WHO) and ICMR-NIN evidence standards:")

    tot_fib = balance['consumed']['fiber']
    tot_sug = balance['consumed']['sugar']
    tot_sod = balance['consumed']['sodium']

    # 1. Fiber
    fib_ok = tot_fib >= 25.0
    st.markdown(f"""
    **1. Dietary Fiber Intake:** `{tot_fib:.1f}g` / ≥ 25.0g target  
    Status: <span class='{'badge-success' if fib_ok else 'badge-warning'}'>{'Meets WHO Target' if fib_ok else 'Below Recommended Intake'}</span>
    """, unsafe_allow_html=True)

    # 2. Sugar
    sug_lim = targets['sugar_limit_g']
    sug_ok = tot_sug <= sug_lim
    st.markdown(f"""
    **2. Added Sugar Ceiling:** `{tot_sug:.1f}g` / < {sug_lim:.0f}g limit  
    Status: <span class='{'badge-success' if sug_ok else 'badge-danger'}'>{'Within Safe Limits' if sug_ok else 'Exceeds WHO Ceiling'}</span>
    """, unsafe_allow_html=True)

    # 3. Sodium
    sod_ok = tot_sod <= 2000.0
    st.markdown(f"""
    **3. Sodium Intake:** `{tot_sod:.0f}mg` / < 2000mg limit  
    Status: <span class='{'badge-success' if sod_ok else 'badge-danger'}'>{'Optimal Cardiovascular Range' if sod_ok else 'High Sodium Alert'}</span>
    """, unsafe_allow_html=True)

    # 4. Energy Balance
    rem_c = balance['remaining']['calories']
    c_status = "Optimal Deficit" if profile_dict['goal'] == "Weight Loss" and rem_c >= 0 else ("Optimal Surplus" if profile_dict['goal'] == "Weight Gain" and balance['consumed']['calories'] >= targets['target_calories'] * 0.9 else "Balanced")
    st.markdown(f"""
    **4. Energy Target Adherence:** `{balance['consumed']['calories']:.0f}` / `{targets['target_calories']:.0f} kcal`  
    Status: <span class='badge-success'>{c_status}</span>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Right: PDF & CSV Download Center
with col_rep2:
    st.markdown("<div class='nutri-card-glow'>", unsafe_allow_html=True)
    st.markdown("### 📥 Document Export Center")
    st.markdown("Generate a PDF report including metabolic analysis, macro distributions, logged food tables, and dynamic AI notes.")

    pdf_filename = f"nutrifit_report_{user_name.replace(' ', '_').lower()}.pdf"
    
    # Generate PDF button
    if st.button("📄 Generate PDF Nutrition Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            pdf_path = generate_pdf_report(
                user_name=user_name,
                profile=profile_dict,
                targets=targets,
                balance=balance,
                food_logs=food_logs,
                output_path=pdf_filename
            )
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="⬇️ Download PDF File",
                data=pdf_bytes,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )
            st.success("Report generated successfully!")

    st.markdown("---")
    st.markdown("#### 📊 Export Food Logs to CSV")
    if food_logs:
        df_export = pd.DataFrame(food_logs)
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Food History (CSV)",
            data=csv_data,
            file_name="nutrifit_food_history.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No food history available yet to export.")

    st.markdown("</div>", unsafe_allow_html=True)

# Bottom Full History Table
st.markdown("### 📋 Complete Food Consumption Ledger")
if food_logs:
    st.dataframe(pd.DataFrame(food_logs), use_container_width=True, hide_index=True)
else:
    st.info("No food logs recorded in ledger.")

st.markdown(render_disclaimer(), unsafe_allow_html=True)

