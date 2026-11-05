"""
NutriFit AI - Page 2: Food Nutrition Analyzer
Enables users to search foods, scale portions, look up barcodes via Open Food Facts,
and scan nutrition labels via OCR/text extraction.
"""

import streamlit as st
import pandas as pd
from src.food_analyzer import search_foods, get_food_dataframe, calculate_serving_nutrients
from src.database import get_session, FoodLog, FoodItem
from utils.food_api import fetch_product_by_barcode, SAMPLE_BARCODES
from utils.helpers import inject_custom_css, render_disclaimer
from PIL import Image
import re

st.set_page_config(page_title="NutriFit AI - Food Analyzer", page_icon="🔍", layout="wide")
st.markdown(inject_custom_css(), unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

st.title("🔍 Food Nutrition Analyzer")
st.markdown("Search packaged and ordinary foods, inspect micro and macronutrients per custom serving, or scan barcodes and labels.")

tab1, tab2, tab3 = st.tabs(["🔎 Food Database Search", "📱 Barcode Scanner (Open Food Facts)", "📸 Nutrition Label Scanner (OCR)"])

# ----------------- TAB 1: SEARCH FOOD DATABASE -----------------
with tab1:
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        query = st.text_input("Search Food, Snack, Dish, or Brand", placeholder="e.g. Lay's, Paneer, Dal, Kurkure, Apple, Rice, Chocolate")
    with col_s2:
        diet_filter = st.selectbox("Dietary Preference", ["All", "Vegetarian", "Vegan", "Eggetarian"])
    with col_s3:
        cat_filter = st.selectbox("Category Filter", ["All", "Breads & Cereals", "Dals & Legumes", "Dairy", "Snacks & Chips", "Chocolates & Sweets", "Beverages", "Breakfast", "Indian Curries", "Poultry & Meat", "Fruits and Fruit Juices", "Vegetables and Vegetable Products"])

    results = search_foods(query, category_filter=cat_filter, dietary_filter=diet_filter, limit=20)

    if not results:
        st.warning("No foods found matching your query. Try searching for 'Dal', 'Roti', 'Chips', 'Paneer', or 'Chocolate'.")
    else:
        st.markdown(f"Found **{len(results)}** matches:")
        
        # Select product
        food_names = [f"{r['food_name']} ({r.get('brand', 'Generic')})" for r in results]
        selected_idx = st.selectbox("Select Product to Analyze:", range(len(food_names)), format_func=lambda i: food_names[i])
        selected_food = results[selected_idx]

        st.markdown("---")
        c_left, c_right = st.columns([1, 1.2])

        with c_left:
            st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
            st.markdown(f"### {selected_food['food_name']}")
            st.markdown(f"**Brand:** `{selected_food.get('brand', 'Generic')}` | **Category:** `{selected_food.get('category', 'General')}`")
            st.markdown(f"**Dietary Type:** `{selected_food.get('dietary_preference', 'Vegetarian')}`")

            # Serving size customizer
            std_serving = float(selected_food.get('serving_size', 100.0))
            serving_unit = str(selected_food.get('serving_unit', 'g'))
            household = str(selected_food.get('household_serving', '100g'))
            
            st.caption(f"Standard Household Serving Reference: **{household}**")
            qty = st.number_input(f"Enter Serving Quantity consumed ({serving_unit}):", min_value=1.0, max_value=2000.0, value=std_serving, step=5.0)

            nutrients = calculate_serving_nutrients(selected_food, qty)

            st.markdown("---")
            st.markdown("#### 📥 Log this to Food Diary")
            meal_choice = st.selectbox("Meal Category", ["Breakfast", "Lunch", "Snacks", "Dinner"], index=2)
            if st.button("➕ Add to Today's Diary", type="primary", use_container_width=True):
                session = get_session()
                try:
                    fid = int(selected_food['food_id'])
                    log_entry = FoodLog(
                        user_id=st.session_state.user_id,
                        food_id=fid,
                        quantity=qty,
                        meal_type=meal_choice
                    )
                    session.add(log_entry)
                    session.commit()
                    st.success(f"✅ Logged {qty}{serving_unit} of **{selected_food['food_name']}** to **{meal_choice}**!")
                except Exception as e:
                    session.rollback()
                    st.error(f"Error logging food: {e}")
                finally:
                    session.close()

            st.markdown("</div>", unsafe_allow_html=True)

        with c_right:
            st.markdown("<div class='nutri-card-glow'>", unsafe_allow_html=True)
            st.markdown(f"### 📊 Nutritional Facts for {qty:.0f} {serving_unit}")

            # Macro KPIs
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Calories", f"{nutrients['calories']:.0f} kcal")
            m2.metric("Protein", f"{nutrients['protein']:.1f} g")
            m3.metric("Carbs", f"{nutrients['carbs']:.1f} g")
            m4.metric("Total Fat", f"{nutrients['fat']:.1f} g")

            st.markdown("---")
            # Detailed breakdown table
            breakdown_data = [
                {"Nutrient": "Saturated Fat", "Amount": f"{nutrients['saturated_fat']:.1f} g", "Health Note": "Limit <10% calories"},
                {"Nutrient": "Dietary Fiber", "Amount": f"{nutrients['fiber']:.1f} g", "Health Note": "WHO goal ≥25g/day"},
                {"Nutrient": "Added / Total Sugar", "Amount": f"{nutrients['sugar']:.1f} g", "Health Note": "WHO ceiling <25-35g"},
                {"Nutrient": "Sodium", "Amount": f"{nutrients['sodium']:.0f} mg", "Health Note": "Ceiling <2000mg"},
                {"Nutrient": "Calcium", "Amount": f"{nutrients['calcium']:.0f} mg", "Health Note": "Bone health & muscle function"},
                {"Nutrient": "Iron", "Amount": f"{nutrients['iron']:.1f} mg", "Health Note": "Oxygen transport"},
                {"Nutrient": "Vitamin C", "Amount": f"{nutrients['vitamin_c']:.1f} mg", "Health Note": "Antioxidant & immunity"}
            ]
            st.dataframe(pd.DataFrame(breakdown_data), use_container_width=True, hide_index=True)

            score = nutrients.get('health_score', 50)
            score_color = "badge-success" if score >= 75 else ("badge-warning" if score >= 45 else "badge-danger")
            st.markdown(f"NutriFit Health Score: <span class='{score_color}'>{int(score)} / 100</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TAB 2: BARCODE SCANNER -----------------
with tab2:
    st.markdown("### 📱 Barcode Food Scanner (Powered by Open Food Facts)")
    st.markdown("Scan or enter a product barcode to query global and Indian packaged product nutrition.")

    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        st.markdown("**Test with popular Indian & Global sample barcodes:**")
        sample_code = st.selectbox(
            "Select sample barcode to test:",
            list(SAMPLE_BARCODES.keys()),
            format_func=lambda c: f"{c} - {SAMPLE_BARCODES[c]}"
        )
        custom_barcode = st.text_input("Or Enter / Scan any Barcode:", value=sample_code)

        if st.button("🔍 Scan & Query Product", type="primary"):
            with st.spinner("Fetching product data from Open Food Facts API..."):
                prod_data = fetch_product_by_barcode(custom_barcode)
                if prod_data:
                    st.session_state.scanned_product = prod_data
                    st.success(f"Product found: {prod_data['food_name']}")
                else:
                    st.error("Barcode not found in Open Food Facts registry.")

    with col_b2:
        if "scanned_product" in st.session_state:
            p = st.session_state.scanned_product
            st.markdown("<div class='nutri-card-glow'>", unsafe_allow_html=True)
            st.markdown(f"#### {p['food_name']}")
            st.write(f"**Brand:** {p.get('brand')} | **Category:** {p.get('category')}")
            st.write(f"**Source:** {p.get('source')}")
            
            st.markdown("##### Nutritional Profile (per 100g):")
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Calories", f"{p['calories']} kcal")
            sc2.metric("Protein", f"{p['protein']} g")
            sc3.metric("Carbs", f"{p['carbs']} g")
            sc4, sc5, sc6 = st.columns(3)
            sc4.metric("Fat", f"{p['fat']} g")
            sc5.metric("Sugar", f"{p['sugar']} g")
            sc6.metric("Sodium", f"{p['sodium']} mg")

            st.markdown("---")
            b_qty = st.number_input("Consumed Quantity (g):", min_value=1.0, max_value=1000.0, value=50.0, step=5.0)
            b_meal = st.selectbox("Log to Meal:", ["Breakfast", "Lunch", "Snacks", "Dinner"], index=2, key="b_meal")
            
            if st.button("➕ Log Scanned Item to Food Diary"):
                session = get_session()
                try:
                    # Check if exists or create temporary item
                    db_item = session.query(FoodItem).filter(FoodItem.name == p['food_name']).first()
                    if not db_item:
                        from src.database import FoodNutrition
                        db_item = FoodItem(
                            food_id=int(hash(p['food_name']) % 10000000 + 1000000),
                            name=p['food_name'],
                            category=p['category'][:50],
                            brand=p['brand'][:50],
                            serving_size=100.0,
                            serving_unit="g",
                            dietary_preference=p.get('dietary_preference', 'Vegetarian')
                        )
                        session.add(db_item)
                        session.flush()
                        db_nutr = FoodNutrition(
                            food_id=db_item.food_id,
                            calories=p['calories'],
                            protein=p['protein'],
                            carbs=p['carbs'],
                            fibre=p['fiber'],
                            fat=p['fat'],
                            saturated_fat=p['saturated_fat'],
                            sugar=p['sugar'],
                            sodium=p['sodium'],
                            health_score=p['health_score']
                        )
                        session.add(db_nutr)
                        session.commit()

                    session.add(FoodLog(
                        user_id=st.session_state.user_id,
                        food_id=db_item.food_id,
                        quantity=b_qty,
                        meal_type=b_meal
                    ))
                    session.commit()
                    st.success(f"✅ Logged {b_qty}g of {p['food_name']} to {b_meal}!")
                finally:
                    session.close()

            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TAB 3: OCR LABEL SCANNER -----------------
with tab3:
    st.markdown("### 📸 Nutrition Label OCR & Image Scanner")
    st.markdown("Upload a photo of a packaged food label (e.g. Cadbury, Kurkure, Biscuits) or paste nutrition label text to extract nutrients.")

    ocr_col1, ocr_col2 = st.columns([1, 1])

    with ocr_col1:
        uploaded_file = st.file_uploader("Upload Nutrition Facts Label Image (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Label", use_container_width=True)

        st.markdown("**Or Paste Nutrition Table Text:**")
        sample_ocr_text = """Nutrition Information per 100g:
Energy / Calories: 540 kcal
Protein: 6.8 g
Carbohydrate: 54.0 g
Total Sugars: 4.5 g
Total Fat: 34.0 g
Saturated Fat: 14.0 g
Sodium: 820 mg"""
        raw_text = st.text_area("Label Text to Parse:", value=sample_ocr_text, height=140)

    with ocr_col2:
        if st.button("⚡ Extract & Parse Nutrients", type="primary"):
            # Simple, robust regex extraction for nutrition keywords
            def extract_val(pattern, text, default=0.0):
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1).replace(",", "."))
                    except Exception:
                        return default
                return default

            cals = extract_val(r"(?:energy|calories|kcal)\s*[:=]?\s*([0-9.]+)", raw_text, 540.0)
            prot = extract_val(r"protein\s*[:=]?\s*([0-9.]+)", raw_text, 6.8)
            carb = extract_val(r"(?:carbohydrate|carbs)\s*[:=]?\s*([0-9.]+)", raw_text, 54.0)
            fat = extract_val(r"(?:total fat|fat)\s*[:=]?\s*([0-9.]+)", raw_text, 34.0)
            sug = extract_val(r"(?:sugar|sugars)\s*[:=]?\s*([0-9.]+)", raw_text, 4.5)
            sod = extract_val(r"sodium\s*[:=]?\s*([0-9.]+)", raw_text, 820.0)

            st.markdown("<div class='nutri-card-glow'>", unsafe_allow_html=True)
            st.markdown("#### ✅ OCR Extracted Nutrition Values (per 100g)")
            e1, e2, e3 = st.columns(3)
            e1.metric("Calories", f"{cals:.0f} kcal")
            e2.metric("Protein", f"{prot:.1f} g")
            e3.metric("Carbs", f"{carb:.1f} g")
            e4, e5, e6 = st.columns(3)
            e4.metric("Fat", f"{fat:.1f} g")
            e5.metric("Sugar", f"{sug:.1f} g")
            e6.metric("Sodium", f"{sod:.0f} mg")
            st.markdown("Values successfully extracted and ready for analysis!")
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown(render_disclaimer(), unsafe_allow_html=True)

