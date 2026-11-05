"""
NutriFit AI - Helpers & Report Generators
Includes WHO dietary principles, clinical disclaimers, PDF report generation, and UI badge formatters.
"""

import os
from fpdf import FPDF
from datetime import datetime
from typing import Dict, Any, List

def inject_custom_css():
    """Injects high-end dark glassmorphism styling into the Streamlit app."""
    css = """
    <style>
    /* Dark Obsidian Background */
    .stApp {
        background-color: #0B0E14;
        color: #E6EDF3;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Sleek card container */
    .nutri-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .nutri-card-glow {
        background: linear-gradient(145deg, #161B22, #1F242C);
        border: 1px solid #00E67644;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0, 230, 118, 0.08);
    }

    /* Badges */
    .badge-success {
        background-color: rgba(0, 230, 118, 0.15);
        color: #00E676;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        border: 1px solid rgba(0, 230, 118, 0.3);
    }
    .badge-warning {
        background-color: rgba(255, 145, 0, 0.15);
        color: #FF9100;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        border: 1px solid rgba(255, 145, 0, 0.3);
    }
    .badge-danger {
        background-color: rgba(255, 82, 82, 0.15);
        color: #FF5252;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        border: 1px solid rgba(255, 82, 82, 0.3);
    }

    /* Metric pill */
    .metric-pill {
        display: inline-block;
        background: #21262D;
        padding: 6px 12px;
        border-radius: 8px;
        margin-right: 8px;
        margin-bottom: 8px;
        font-size: 13px;
    }
    </style>
    """
    return css

def render_disclaimer():
    """Renders the responsible nutrition science disclaimer required by guidelines."""
    return """
    <div style="background-color: #161B22; border-left: 4px solid #FF9100; padding: 12px 16px; border-radius: 6px; font-size: 12px; color: #8B949E; margin-top: 24px;">
        <strong>NutriFit AI Responsible Nutrition Notice:</strong>
        This system is designed for educational, dietary self-monitoring, and fitness screening purposes in healthy adults aged 18+.
        Nutrient estimates (BMR, TDEE, BMI) and food alternatives are based on population reference equations (Mifflin-St Jeor, WHO, ICMR-NIN) and machine learning models.
        They do not constitute medical diagnoses, clinical treatment plans, or eating disorder management. Consult a licensed dietitian or physician for specialized clinical needs.
    </div>
    """

def generate_pdf_report(
    user_name: str,
    profile: Dict[str, Any],
    targets: Dict[str, Any],
    balance: Dict[str, Any],
    food_logs: List[Dict[str, Any]],
    output_path: str = "nutrifit_summary_report.pdf"
) -> str:
    """
    Generates a PDF Nutrition & Diet Report using fpdf2.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "NutriFit AI - Comprehensive Nutrition & Diet Report", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Subject: {user_name}", ln=True, align="C")
    pdf.ln(5)

    # Profile & Biomarkers
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "1. User Profile & Metabolic Energetics", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Age: {profile.get('age', 22)} years | Sex: {profile.get('sex', 'Male')}", ln=0)
    pdf.cell(95, 6, f"Goal: {profile.get('goal', 'Maintenance')}", ln=1)
    pdf.cell(95, 6, f"Height: {profile.get('height', 170)} cm | Weight: {profile.get('weight', 65)} kg", ln=0)
    pdf.cell(95, 6, f"BMI: {targets.get('bmi', 22.5)} ({targets.get('bmi_category', 'Normal')})", ln=1)
    pdf.cell(95, 6, f"Estimated BMR: {int(targets.get('bmr', 1600))} kcal/day", ln=0)
    pdf.cell(95, 6, f"Estimated TDEE: {int(targets.get('tdee', 2200))} kcal/day", ln=1)
    pdf.cell(0, 6, f"Target Daily Calorie Allowance: {int(targets.get('target_calories', 2000))} kcal", ln=1)
    pdf.ln(5)

    # Daily Nutrition Balance
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "2. Daily Nutritional Tracking Summary", ln=True)
    consumed = balance.get('consumed', {})
    remaining = balance.get('remaining', {})
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Energy Intake: {int(consumed.get('calories', 0))} kcal consumed ({int(remaining.get('calories', 0))} kcal remaining)", ln=1)
    pdf.cell(0, 6, f"Protein: {consumed.get('protein', 0):.1f}g consumed / {targets.get('target_protein_g', 100):.0f}g target", ln=1)
    pdf.cell(0, 6, f"Carbohydrates: {consumed.get('carbs', 0):.1f}g consumed / {targets.get('target_carbs_g', 250):.0f}g target", ln=1)
    pdf.cell(0, 6, f"Total Fat: {consumed.get('fat', 0):.1f}g consumed / {targets.get('target_fat_g', 60):.0f}g target", ln=1)
    pdf.cell(0, 6, f"Dietary Fiber: {consumed.get('fiber', 0):.1f}g consumed (WHO minimum: 25g)", ln=1)
    pdf.cell(0, 6, f"Added Sugar: {consumed.get('sugar', 0):.1f}g (Recommended ceiling: < {targets.get('sugar_limit_g', 35):.0f}g)", ln=1)
    pdf.cell(0, 6, f"Sodium: {consumed.get('sodium', 0):.0f}mg (Recommended ceiling: < 2000mg)", ln=1)
    pdf.ln(5)

    # Food Log Table
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "3. Consumed Food Log Details", ln=True)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(25, 6, "Meal Type", 1)
    pdf.cell(75, 6, "Food Item", 1)
    pdf.cell(25, 6, "Quantity", 1)
    pdf.cell(25, 6, "Calories", 1)
    pdf.cell(20, 6, "Protein", 1)
    pdf.cell(20, 6, "Carbs", 1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    if not food_logs:
        pdf.cell(190, 6, "No foods recorded today.", 1, ln=1, align="C")
    else:
        for item in food_logs:
            pdf.cell(25, 6, str(item.get('meal_type', 'Snack'))[:12], 1)
            pdf.cell(75, 6, str(item.get('food_name', 'Item'))[:36], 1)
            pdf.cell(25, 6, f"{item.get('quantity', 100):.0f}g", 1)
            pdf.cell(25, 6, f"{item.get('calories', 0):.0f} kcal", 1)
            pdf.cell(20, 6, f"{item.get('protein', 0):.1f}g", 1)
            pdf.cell(20, 6, f"{item.get('carbs', 0):.1f}g", 1)
            pdf.ln()

    pdf.ln(6)
    # AI Clinical Insights
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "4. AI Dietitian Insights & Next Steps", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for insight in balance.get('insights', []):
        clean_text = insight.replace("**", "").replace("⚠️", "[!]")
        pdf.multi_cell(0, 6, f"- {clean_text}")

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 5, "Disclaimer: NutriFit AI is an automated machine learning and nutrition science analytical system. It does not replace advice from certified clinical nutritionists or healthcare professionals.")

    pdf.output(output_path)
    return output_path

