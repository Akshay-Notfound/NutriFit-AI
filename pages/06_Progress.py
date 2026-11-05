"""
NutriFit AI - Page 6: Progress Analytics & Weight Tracker
Tracks body weight records, BMI transitions, adherence rates, and provides
experimental trend estimations without making false medical promises.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from src.database import get_session, User, WeightHistory, FoodLog
from src.nutrition_engine import calculate_bmi, calculate_daily_targets
from src.progress_tracker import compute_weight_trend, compute_calorie_adherence
from utils.charts import create_weight_trend_chart
from utils.helpers import inject_custom_css, render_disclaimer

st.set_page_config(page_title="NutriFit AI - Progress Analytics", page_icon="📈", layout="wide")
st.markdown(inject_custom_css(), unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

session = get_session()
try:
    user = session.query(User).filter_by(user_id=st.session_state.user_id).first()
    p = user.profile if user else None

    height = p.height if p else 170.0
    curr_weight = p.weight if p else 65.0
    target_weight = p.target_weight if p and p.target_weight else 70.0
    goal = p.goal if p else "Weight Gain"

    wh_records = session.query(WeightHistory).filter_by(user_id=st.session_state.user_id).order_by(WeightHistory.recorded_at.asc()).all()
    history = [{"weight": r.weight, "recorded_at": r.recorded_at} for r in wh_records]
finally:
    session.close()

st.title("📈 Fitness Goal & Progress Analytics")
st.markdown("Monitor long-term body weight changes, consistency adherence, and review empirical trend estimates.")

col_p1, col_p2 = st.columns([1, 1.4])

# Left: Log New Weight
with col_p1:
    st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
    st.markdown("### ⚖️ Log Today's Weight")
    new_w = st.number_input("Recorded Weight (kg):", min_value=30.0, max_value=250.0, value=float(curr_weight), step=0.1)
    rec_date = st.date_input("Date of Measurement:", value=date.today())

    if st.button("📌 Record Weight Entry", type="primary", use_container_width=True):
        session = get_session()
        try:
            # Update user profile current weight
            u = session.query(User).filter_by(user_id=st.session_state.user_id).first()
            if u and u.profile:
                u.profile.weight = new_w
            
            # Append to history
            wh = WeightHistory(
                user_id=st.session_state.user_id,
                weight=new_w,
                recorded_at=datetime.combine(rec_date, datetime.now().time())
            )
            session.add(wh)
            session.commit()
            st.success(f"✅ Recorded {new_w:.1f} kg for {rec_date.strftime('%b %d, %Y')}!")
            st.rerun()
        finally:
            session.close()

    # Pre-populate sample multi-day history button for demonstration
    if len(history) < 3:
        st.markdown("---")
        st.caption("Need sample data to see trend curves?")
        if st.button("📊 Populate 7-Day Demo Weight History"):
            session = get_session()
            try:
                base_w = curr_weight - 1.2 if goal == "Weight Gain" else curr_weight + 1.2
                for i in range(7, 0, -1):
                    dt = datetime.now() - timedelta(days=i)
                    step = 0.18 if goal == "Weight Gain" else -0.18
                    session.add(WeightHistory(
                        user_id=st.session_state.user_id,
                        weight=round(base_w + (step * (7 - i)), 1),
                        recorded_at=dt
                    ))
                session.commit()
                st.success("Sample history added!")
                st.rerun()
            finally:
                session.close()

    st.markdown("</div>", unsafe_allow_html=True)

# Right: Chart & Metric KPIs
with col_p2:
    st.markdown("<div class='nutri-card-glow'>", unsafe_allow_html=True)
    st.markdown("### 📊 Weight History Trajectory")
    fig_w = create_weight_trend_chart(history)
    st.plotly_chart(fig_w, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# Trend Statistics & Statistical Projection
trend_data = compute_weight_trend(history)

st.markdown("### 🔬 Statistical Trend & Rate of Change")
t1, t2, t3, t4 = st.columns(4)
t1.metric("Current Weight", f"{trend_data['current_weight']:.1f} kg")
t2.metric("Total Net Change", f"{trend_data['net_change']:+.1f} kg")
t3.metric("Estimated Weekly Rate", f"{trend_data['weekly_rate']:+.2f} kg / wk")
t4.metric("30-Day Trend Projection", f"{trend_data['projection_30d']:.1f} kg")

st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
st.markdown(f"**Observed Direction:** <span class='badge-success'>{trend_data['trend_direction']}</span>", unsafe_allow_html=True)
st.caption(f"ℹ️ {trend_data['disclaimer']}")

# Healthy BMI check
curr_bmi, cat, _, (min_w, max_w) = calculate_bmi(trend_data['current_weight'], height)
st.write(f"- Current BMI: **{curr_bmi}** ({cat})")
st.write(f"- Healthy weight interval for your height ({height:.0f}cm): **{min_w} kg to {max_w} kg**")
st.write(f"- Target Goal Weight: **{target_weight:.1f} kg** (Remaining to goal: **{abs(trend_data['current_weight'] - target_weight):.1f} kg**)")
st.markdown("</div>", unsafe_allow_html=True)

# Historical Records Table
if history:
    with st.expander("📋 View All Recorded Weight Logs"):
        df_wh = pd.DataFrame(history)
        df_wh['recorded_at'] = pd.to_datetime(df_wh['recorded_at']).dt.strftime('%Y-%m-%d %H:%M')
        df_wh.columns = ['Weight (kg)', 'Logged Timestamp']
        st.dataframe(df_wh, use_container_width=True, hide_index=True)

st.markdown(render_disclaimer(), unsafe_allow_html=True)

