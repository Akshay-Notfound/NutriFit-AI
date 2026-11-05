"""
NutriFit AI - Data Preprocessing & Food Dataset Curation Pipeline
Combines USDA Comprehensive Foods with authentic Indian Food Composition Tables (IFCT/ICMR-NIN)
and popular branded packaged foods/snacks.
"""

import os
import pandas as pd
import numpy as np

# Authentic Indian Food Composition Dataset (ICMR-NIN & Food Labels per 100g)
INDIAN_FOODS_DATA = [
    # Grains & Breads
    {"food_name": "Whole Wheat Roti / Chapati", "category": "Breads & Cereals", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 40.0, "serving_unit": "g", "household_serving": "1 roti",
     "calories": 297.0, "carbs": 61.0, "protein": 11.8, "fat": 3.7, "saturated_fat": 0.6,
     "fiber": 11.5, "sugar": 0.4, "sodium": 120.0, "calcium": 48.0, "iron": 4.1, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 85},
    {"food_name": "Bajra Roti (Pearl Millet)", "category": "Breads & Cereals", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 45.0, "serving_unit": "g", "household_serving": "1 roti",
     "calories": 361.0, "carbs": 67.5, "protein": 11.6, "fat": 5.0, "saturated_fat": 0.8,
     "fiber": 11.3, "sugar": 0.6, "sodium": 110.0, "calcium": 42.0, "iron": 8.0, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 90},
    {"food_name": "Jowar Roti (Sorghum)", "category": "Breads & Cereals", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 45.0, "serving_unit": "g", "household_serving": "1 roti",
     "calories": 349.0, "carbs": 72.6, "protein": 10.4, "fat": 1.9, "saturated_fat": 0.4,
     "fiber": 10.2, "sugar": 0.8, "sodium": 95.0, "calcium": 25.0, "iron": 4.1, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 88},
    {"food_name": "Steamed White Rice", "category": "Grains & Rice", "brand": "Generic",
     "food_type": "Cooked Food", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 bowl (cooked)",
     "calories": 130.0, "carbs": 28.2, "protein": 2.7, "fat": 0.3, "saturated_fat": 0.1,
     "fiber": 0.4, "sugar": 0.1, "sodium": 2.0, "calcium": 10.0, "iron": 0.2, "vitamin_c": 0.0,
     "dietary_preference": "Vegan", "health_score": 65},
    {"food_name": "Brown Rice (Cooked)", "category": "Grains & Rice", "brand": "Generic",
     "food_type": "Cooked Food", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 bowl (cooked)",
     "calories": 111.0, "carbs": 23.0, "protein": 2.6, "fat": 0.9, "saturated_fat": 0.2,
     "fiber": 1.8, "sugar": 0.4, "sodium": 5.0, "calcium": 10.0, "iron": 0.5, "vitamin_c": 0.0,
     "dietary_preference": "Vegan", "health_score": 82},
    {"food_name": "Jeera Rice", "category": "Grains & Rice", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 165.0, "carbs": 29.5, "protein": 3.1, "fat": 4.0, "saturated_fat": 1.2,
     "fiber": 0.8, "sugar": 0.2, "sodium": 180.0, "calcium": 18.0, "iron": 0.6, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 68},
    {"food_name": "Plain Paratha (Ghee)", "category": "Breads & Cereals", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 60.0, "serving_unit": "g", "household_serving": "1 paratha",
     "calories": 320.0, "carbs": 44.0, "protein": 6.5, "fat": 13.5, "saturated_fat": 6.0,
     "fiber": 4.5, "sugar": 1.0, "sodium": 220.0, "calcium": 35.0, "iron": 2.5, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 60},
    {"food_name": "Aloo Paratha", "category": "Breads & Cereals", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 100.0, "serving_unit": "g", "household_serving": "1 stuffed paratha",
     "calories": 260.0, "carbs": 38.0, "protein": 5.2, "fat": 10.5, "saturated_fat": 4.2,
     "fiber": 3.8, "sugar": 1.2, "sodium": 310.0, "calcium": 28.0, "iron": 2.1, "vitamin_c": 4.5,
     "dietary_preference": "Vegetarian", "health_score": 62},

    # Dals, Pulses & Legumes
    {"food_name": "Moong Dal Tadka (Yellow Lentils)", "category": "Dals & Legumes", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 180.0, "serving_unit": "g", "household_serving": "1 katori / bowl",
     "calories": 115.0, "carbs": 15.8, "protein": 7.4, "fat": 2.8, "saturated_fat": 0.8,
     "fiber": 4.2, "sugar": 1.1, "sodium": 280.0, "calcium": 32.0, "iron": 1.9, "vitamin_c": 1.5,
     "dietary_preference": "Vegetarian", "health_score": 90},
    {"food_name": "Toor / Arhar Dal (Cooked)", "category": "Dals & Legumes", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 180.0, "serving_unit": "g", "household_serving": "1 katori / bowl",
     "calories": 120.0, "carbs": 16.5, "protein": 7.1, "fat": 3.2, "saturated_fat": 0.9,
     "fiber": 4.0, "sugar": 1.0, "sodium": 260.0, "calcium": 28.0, "iron": 1.8, "vitamin_c": 1.0,
     "dietary_preference": "Vegetarian", "health_score": 88},
    {"food_name": "Chana Dal (Cooked)", "category": "Dals & Legumes", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 180.0, "serving_unit": "g", "household_serving": "1 katori / bowl",
     "calories": 135.0, "carbs": 18.2, "protein": 8.1, "fat": 3.5, "saturated_fat": 0.8,
     "fiber": 5.2, "sugar": 1.2, "sodium": 270.0, "calcium": 40.0, "iron": 2.4, "vitamin_c": 0.5,
     "dietary_preference": "Vegetarian", "health_score": 91},
    {"food_name": "Dal Makhani (Restaurant Style)", "category": "Dals & Legumes", "brand": "Indian Curries",
     "food_type": "Cooked Food", "serving_size": 180.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 210.0, "carbs": 19.5, "protein": 7.8, "fat": 11.5, "saturated_fat": 6.2,
     "fiber": 5.0, "sugar": 2.0, "sodium": 390.0, "calcium": 65.0, "iron": 2.2, "vitamin_c": 1.2,
     "dietary_preference": "Vegetarian", "health_score": 64},
    {"food_name": "Rajma Masala (Red Kidney Beans Curry)", "category": "Dals & Legumes", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 200.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 138.0, "carbs": 19.8, "protein": 8.2, "fat": 3.6, "saturated_fat": 0.7,
     "fiber": 6.4, "sugar": 1.8, "sodium": 320.0, "calcium": 48.0, "iron": 2.8, "vitamin_c": 3.5,
     "dietary_preference": "Vegetarian", "health_score": 92},
    {"food_name": "Chole / Chana Masala (Chickpeas Curry)", "category": "Dals & Legumes", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 200.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 160.0, "carbs": 22.5, "protein": 7.8, "fat": 4.8, "saturated_fat": 0.9,
     "fiber": 6.8, "sugar": 2.2, "sodium": 340.0, "calcium": 52.0, "iron": 2.9, "vitamin_c": 4.0,
     "dietary_preference": "Vegetarian", "health_score": 91},
    {"food_name": "Moong Sprouts Salad", "category": "Salads & Healthy Snacks", "brand": "Generic",
     "food_type": "Raw / Fresh", "serving_size": 100.0, "serving_unit": "g", "household_serving": "1 cup",
     "calories": 30.0, "carbs": 5.9, "protein": 3.0, "fat": 0.2, "saturated_fat": 0.05,
     "fiber": 1.8, "sugar": 4.1, "sodium": 15.0, "calcium": 13.0, "iron": 0.9, "vitamin_c": 13.2,
     "dietary_preference": "Vegan", "health_score": 98},
    {"food_name": "Kala Chana (Boiled Black Chickpeas)", "category": "Dals & Legumes", "brand": "Generic",
     "food_type": "Cooked Food", "serving_size": 100.0, "serving_unit": "g", "household_serving": "1 cup",
     "calories": 164.0, "carbs": 27.4, "protein": 8.9, "fat": 2.6, "saturated_fat": 0.3,
     "fiber": 7.6, "sugar": 4.8, "sodium": 24.0, "calcium": 45.0, "iron": 2.9, "vitamin_c": 1.3,
     "dietary_preference": "Vegan", "health_score": 95},

    # Dairy & Paneer
    {"food_name": "Paneer (Fresh Raw Indian Cottage Cheese)", "category": "Dairy", "brand": "Generic",
     "food_type": "Dairy Food", "serving_size": 100.0, "serving_unit": "g", "household_serving": "100g slice",
     "calories": 296.0, "carbs": 4.5, "protein": 18.3, "fat": 22.5, "saturated_fat": 13.2,
     "fiber": 0.0, "sugar": 3.2, "sodium": 22.0, "calcium": 480.0, "iron": 0.4, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 82},
    {"food_name": "Paneer Tikka (Grilled)", "category": "Appetizers & Starters", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 120.0, "serving_unit": "g", "household_serving": "4 pieces",
     "calories": 240.0, "carbs": 7.5, "protein": 15.2, "fat": 16.8, "saturated_fat": 9.2,
     "fiber": 1.6, "sugar": 2.5, "sodium": 360.0, "calcium": 380.0, "iron": 1.2, "vitamin_c": 8.5,
     "dietary_preference": "Vegetarian", "health_score": 85},
    {"food_name": "Paneer Bhurji", "category": "Indian Curries", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 265.0, "carbs": 6.8, "protein": 14.5, "fat": 20.1, "saturated_fat": 10.8,
     "fiber": 1.8, "sugar": 2.8, "sodium": 340.0, "calcium": 350.0, "iron": 1.1, "vitamin_c": 12.0,
     "dietary_preference": "Vegetarian", "health_score": 80},
    {"food_name": "Palak Paneer", "category": "Indian Curries", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 200.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 185.0, "carbs": 6.2, "protein": 11.2, "fat": 13.5, "saturated_fat": 7.2,
     "fiber": 3.4, "sugar": 2.1, "sodium": 320.0, "calcium": 280.0, "iron": 3.2, "vitamin_c": 16.0,
     "dietary_preference": "Vegetarian", "health_score": 89},
    {"food_name": "Curd / Dahi (Plain Whole Milk)", "category": "Dairy", "brand": "Generic",
     "food_type": "Dairy Food", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 61.0, "carbs": 4.7, "protein": 3.5, "fat": 3.3, "saturated_fat": 2.1,
     "fiber": 0.0, "sugar": 4.7, "sodium": 46.0, "calcium": 121.0, "iron": 0.1, "vitamin_c": 0.5,
     "dietary_preference": "Vegetarian", "health_score": 90},
    {"food_name": "Chaas / Spiced Buttermilk", "category": "Beverages", "brand": "Homemade / Generic",
     "food_type": "Beverage", "serving_size": 200.0, "serving_unit": "ml", "household_serving": "1 glass (200ml)",
     "calories": 40.0, "carbs": 4.8, "protein": 3.3, "fat": 0.9, "saturated_fat": 0.5,
     "fiber": 0.1, "sugar": 4.8, "sodium": 150.0, "calcium": 116.0, "iron": 0.1, "vitamin_c": 1.0,
     "dietary_preference": "Vegetarian", "health_score": 95},
    {"food_name": "Sweet Lassi", "category": "Beverages", "brand": "Indian Dairy",
     "food_type": "Beverage", "serving_size": 200.0, "serving_unit": "ml", "household_serving": "1 glass",
     "calories": 155.0, "carbs": 24.0, "protein": 4.2, "fat": 4.5, "saturated_fat": 2.8,
     "fiber": 0.0, "sugar": 22.0, "sodium": 65.0, "calcium": 140.0, "iron": 0.1, "vitamin_c": 0.5,
     "dietary_preference": "Vegetarian", "health_score": 62},

    # Breakfast & Regional Indian Specialties
    {"food_name": "Idli (Steamed Fermented Rice Cake)", "category": "Breakfast", "brand": "South Indian",
     "food_type": "Cooked Food", "serving_size": 60.0, "serving_unit": "g", "household_serving": "2 pieces",
     "calories": 132.0, "carbs": 26.5, "protein": 4.8, "fat": 0.5, "saturated_fat": 0.1,
     "fiber": 1.8, "sugar": 0.2, "sodium": 140.0, "calcium": 18.0, "iron": 1.1, "vitamin_c": 0.0,
     "dietary_preference": "Vegan", "health_score": 92},
    {"food_name": "Plain Dosa", "category": "Breakfast", "brand": "South Indian",
     "food_type": "Cooked Food", "serving_size": 80.0, "serving_unit": "g", "household_serving": "1 dosa",
     "calories": 168.0, "carbs": 28.5, "protein": 3.9, "fat": 4.2, "saturated_fat": 1.2,
     "fiber": 1.5, "sugar": 0.5, "sodium": 210.0, "calcium": 22.0, "iron": 1.2, "vitamin_c": 0.0,
     "dietary_preference": "Vegan", "health_score": 82},
    {"food_name": "Masala Dosa with Potato Filling", "category": "Breakfast", "brand": "South Indian",
     "food_type": "Cooked Food", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 masala dosa",
     "calories": 245.0, "carbs": 38.0, "protein": 5.4, "fat": 8.5, "saturated_fat": 2.4,
     "fiber": 3.2, "sugar": 1.8, "sodium": 380.0, "calcium": 32.0, "iron": 1.8, "vitamin_c": 6.5,
     "dietary_preference": "Vegetarian", "health_score": 75},
    {"food_name": "Vegetable Sambar", "category": "South Indian", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 75.0, "carbs": 11.2, "protein": 3.8, "fat": 1.8, "saturated_fat": 0.4,
     "fiber": 3.5, "sugar": 2.4, "sodium": 310.0, "calcium": 36.0, "iron": 1.4, "vitamin_c": 8.0,
     "dietary_preference": "Vegan", "health_score": 93},
    {"food_name": "Coconut Chutney", "category": "Condiments & Dips", "brand": "South Indian",
     "food_type": "Cooked Food", "serving_size": 30.0, "serving_unit": "g", "household_serving": "2 tablespoons",
     "calories": 230.0, "carbs": 9.5, "protein": 3.5, "fat": 21.0, "saturated_fat": 18.0,
     "fiber": 4.5, "sugar": 3.0, "sodium": 280.0, "calcium": 20.0, "iron": 1.2, "vitamin_c": 2.0,
     "dietary_preference": "Vegan", "health_score": 68},
    {"food_name": "Poha with Peanuts and Veggies", "category": "Breakfast", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 plate",
     "calories": 180.0, "carbs": 31.0, "protein": 4.5, "fat": 4.8, "saturated_fat": 0.8,
     "fiber": 2.8, "sugar": 1.5, "sodium": 240.0, "calcium": 30.0, "iron": 2.2, "vitamin_c": 9.5,
     "dietary_preference": "Vegan", "health_score": 88},
    {"food_name": "Vegetable Upma", "category": "Breakfast", "brand": "South Indian",
     "food_type": "Cooked Food", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 plate",
     "calories": 172.0, "carbs": 29.5, "protein": 4.2, "fat": 4.4, "saturated_fat": 1.1,
     "fiber": 2.4, "sugar": 1.6, "sodium": 260.0, "calcium": 25.0, "iron": 1.4, "vitamin_c": 4.2,
     "dietary_preference": "Vegetarian", "health_score": 84},
    {"food_name": "Moong Dal Khichdi", "category": "Indian Comfort Food", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 200.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 140.0, "carbs": 24.5, "protein": 5.8, "fat": 2.2, "saturated_fat": 0.6,
     "fiber": 3.2, "sugar": 0.8, "sodium": 240.0, "calcium": 28.0, "iron": 1.6, "vitamin_c": 1.5,
     "dietary_preference": "Vegetarian", "health_score": 94},

    # Healthy Snack Alternatives
    {"food_name": "Roasted Chana (Roasted Bengal Gram)", "category": "Snacks & Nuts", "brand": "Generic",
     "food_type": "Snack Food", "serving_size": 50.0, "serving_unit": "g", "household_serving": "1 handful (50g)",
     "calories": 369.0, "carbs": 58.0, "protein": 18.6, "fat": 5.2, "saturated_fat": 0.6,
     "fiber": 16.8, "sugar": 3.2, "sodium": 45.0, "calcium": 70.0, "iron": 5.3, "vitamin_c": 1.2,
     "dietary_preference": "Vegan", "health_score": 96},
    {"food_name": "Roasted Makhana (Foxnuts / Lotus Seeds)", "category": "Snacks & Nuts", "brand": "Generic",
     "food_type": "Snack Food", "serving_size": 30.0, "serving_unit": "g", "household_serving": "1 bowl (30g)",
     "calories": 347.0, "carbs": 64.5, "protein": 9.7, "fat": 0.5, "saturated_fat": 0.1,
     "fiber": 7.6, "sugar": 0.5, "sodium": 20.0, "calcium": 60.0, "iron": 3.5, "vitamin_c": 0.0,
     "dietary_preference": "Vegan", "health_score": 95},
    {"food_name": "Unsweetened Lemon Water / Nimbu Pani", "category": "Beverages", "brand": "Homemade",
     "food_type": "Beverage", "serving_size": 250.0, "serving_unit": "ml", "household_serving": "1 glass (250ml)",
     "calories": 8.0, "carbs": 1.8, "protein": 0.2, "fat": 0.0, "saturated_fat": 0.0,
     "fiber": 0.3, "sugar": 0.5, "sodium": 12.0, "calcium": 14.0, "iron": 0.1, "vitamin_c": 28.0,
     "dietary_preference": "Vegan", "health_score": 99},
    {"food_name": "Fresh Tender Coconut Water", "category": "Beverages", "brand": "Generic",
     "food_type": "Beverage", "serving_size": 250.0, "serving_unit": "ml", "household_serving": "1 cup",
     "calories": 19.0, "carbs": 3.7, "protein": 0.7, "fat": 0.2, "saturated_fat": 0.1,
     "fiber": 1.1, "sugar": 2.6, "sodium": 105.0, "calcium": 24.0, "iron": 0.3, "vitamin_c": 2.4,
     "dietary_preference": "Vegan", "health_score": 94},
    {"food_name": "Unsweetened Cocoa Greek Yogurt Bowl", "category": "Snacks & Dairy", "brand": "Homemade",
     "food_type": "Prepared Snack", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 95.0, "carbs": 6.5, "protein": 14.0, "fat": 1.5, "saturated_fat": 0.8,
     "fiber": 2.5, "sugar": 3.5, "sodium": 55.0, "calcium": 150.0, "iron": 1.8, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 94},
    {"food_name": "Fresh Fruit & Yogurt Bowl", "category": "Snacks & Dairy", "brand": "Homemade",
     "food_type": "Prepared Snack", "serving_size": 180.0, "serving_unit": "g", "household_serving": "1 bowl",
     "calories": 85.0, "carbs": 13.5, "protein": 6.5, "fat": 1.0, "saturated_fat": 0.5,
     "fiber": 2.4, "sugar": 9.5, "sodium": 42.0, "calcium": 135.0, "iron": 0.4, "vitamin_c": 22.0,
     "dietary_preference": "Vegetarian", "health_score": 95},

    # Branded & Processed Foods (Commonly Tracked Snacks)
    {"food_name": "Lay's India's Magic Masala Potato Chips", "category": "Snacks & Chips", "brand": "Lay's / PepsiCo",
     "food_type": "Packaged Snack", "serving_size": 50.0, "serving_unit": "g", "household_serving": "1 small pack (50g)",
     "calories": 540.0, "carbs": 54.0, "protein": 6.8, "fat": 34.0, "saturated_fat": 14.0,
     "fiber": 3.5, "sugar": 4.5, "sodium": 820.0, "calcium": 25.0, "iron": 1.5, "vitamin_c": 8.0,
     "dietary_preference": "Vegetarian", "health_score": 28},
    {"food_name": "Kurkure Masala Munch", "category": "Snacks & Chips", "brand": "Kurkure / PepsiCo",
     "food_type": "Packaged Snack", "serving_size": 50.0, "serving_unit": "g", "household_serving": "1 pack (50g)",
     "calories": 560.0, "carbs": 56.4, "protein": 5.8, "fat": 34.8, "saturated_fat": 15.2,
     "fiber": 2.2, "sugar": 3.8, "sodium": 890.0, "calcium": 30.0, "iron": 1.8, "vitamin_c": 4.0,
     "dietary_preference": "Vegetarian", "health_score": 25},
    {"food_name": "Cadbury Dairy Milk Chocolate", "category": "Chocolates & Sweets", "brand": "Cadbury / Mondelez",
     "food_type": "Confectionery", "serving_size": 25.0, "serving_unit": "g", "household_serving": "1 small bar (25g)",
     "calories": 534.0, "carbs": 59.8, "protein": 7.8, "fat": 30.4, "saturated_fat": 18.5,
     "fiber": 1.8, "sugar": 57.0, "sodium": 140.0, "calcium": 210.0, "iron": 1.2, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 32},
    {"food_name": "Nestlé KitKat Chocolate Bar", "category": "Chocolates & Sweets", "brand": "Nestlé",
     "food_type": "Confectionery", "serving_size": 38.0, "serving_unit": "g", "household_serving": "4 fingers (38g)",
     "calories": 518.0, "carbs": 64.5, "protein": 6.2, "fat": 26.8, "saturated_fat": 15.4,
     "fiber": 2.0, "sugar": 48.0, "sodium": 85.0, "calcium": 120.0, "iron": 1.0, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 30},
    {"food_name": "Parle-G Glucose Biscuits", "category": "Biscuits & Cookies", "brand": "Parle",
     "food_type": "Packaged Snack", "serving_size": 50.0, "serving_unit": "g", "household_serving": "8 biscuits",
     "calories": 454.0, "carbs": 78.2, "protein": 6.5, "fat": 12.8, "saturated_fat": 5.6,
     "fiber": 2.0, "sugar": 26.0, "sodium": 290.0, "calcium": 45.0, "iron": 2.4, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 42},
    {"food_name": "Maggi 2-Minute Masala Noodles", "category": "Instant Foods", "brand": "Nestlé",
     "food_type": "Instant Noodles", "serving_size": 70.0, "serving_unit": "g", "household_serving": "1 single pack",
     "calories": 427.0, "carbs": 63.5, "protein": 8.0, "fat": 15.7, "saturated_fat": 6.8,
     "fiber": 3.6, "sugar": 2.2, "sodium": 1180.0, "calcium": 105.0, "iron": 3.7, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 35},
    {"food_name": "Haldiram's Aloo Bhujia", "category": "Snacks & Chips", "brand": "Haldiram's",
     "food_type": "Packaged Snack", "serving_size": 50.0, "serving_unit": "g", "household_serving": "1 small pack",
     "calories": 582.0, "carbs": 43.5, "protein": 9.2, "fat": 42.0, "saturated_fat": 16.5,
     "fiber": 4.5, "sugar": 1.5, "sodium": 760.0, "calcium": 35.0, "iron": 2.8, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 27},
    {"food_name": "Coca-Cola / Carbonated Soft Drink", "category": "Beverages", "brand": "Coca-Cola",
     "food_type": "Soft Drink", "serving_size": 250.0, "serving_unit": "ml", "household_serving": "1 can (250ml)",
     "calories": 42.0, "carbs": 10.6, "protein": 0.0, "fat": 0.0, "saturated_fat": 0.0,
     "fiber": 0.0, "sugar": 10.6, "sodium": 4.0, "calcium": 2.0, "iron": 0.0, "vitamin_c": 0.0,
     "dietary_preference": "Vegan", "health_score": 15},
    {"food_name": "Samosa (Potato & Peas Fried)", "category": "Street Food & Snacks", "brand": "Indian Street Food",
     "food_type": "Deep Fried Snack", "serving_size": 80.0, "serving_unit": "g", "household_serving": "1 samosa (80g)",
     "calories": 310.0, "carbs": 32.0, "protein": 4.5, "fat": 18.2, "saturated_fat": 5.4,
     "fiber": 2.8, "sugar": 1.8, "sodium": 420.0, "calcium": 24.0, "iron": 1.8, "vitamin_c": 4.0,
     "dietary_preference": "Vegetarian", "health_score": 40},
    {"food_name": "Gulab Jamun", "category": "Desserts & Sweets", "brand": "Indian Sweets",
     "food_type": "Sweet", "serving_size": 50.0, "serving_unit": "g", "household_serving": "1 piece (50g)",
     "calories": 380.0, "carbs": 52.0, "protein": 5.2, "fat": 16.8, "saturated_fat": 8.5,
     "fiber": 0.5, "sugar": 45.0, "sodium": 110.0, "calcium": 120.0, "iron": 0.6, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 25},

    # Non-Veg & Eggetarian Indian Staples
    {"food_name": "Boiled Whole Egg", "category": "Eggs & Poultry", "brand": "Generic",
     "food_type": "Cooked Food", "serving_size": 50.0, "serving_unit": "g", "household_serving": "1 large egg",
     "calories": 155.0, "carbs": 1.1, "protein": 12.6, "fat": 10.6, "saturated_fat": 3.3,
     "fiber": 0.0, "sugar": 1.1, "sodium": 124.0, "calcium": 50.0, "iron": 1.2, "vitamin_c": 0.0,
     "dietary_preference": "Eggetarian", "health_score": 92},
    {"food_name": "Egg Bhurji (Indian Scrambled Eggs)", "category": "Eggs & Poultry", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 120.0, "serving_unit": "g", "household_serving": "2 eggs with veggies",
     "calories": 175.0, "carbs": 3.5, "protein": 12.2, "fat": 12.5, "saturated_fat": 3.8,
     "fiber": 1.2, "sugar": 1.5, "sodium": 280.0, "calcium": 62.0, "iron": 1.8, "vitamin_c": 8.0,
     "dietary_preference": "Eggetarian", "health_score": 90},
    {"food_name": "Chicken Tikka (Tandoori Grilled)", "category": "Poultry & Meat", "brand": "Indian Cuisine",
     "food_type": "Cooked Food", "serving_size": 150.0, "serving_unit": "g", "household_serving": "1 plate (5-6 pieces)",
     "calories": 160.0, "carbs": 3.2, "protein": 26.5, "fat": 4.5, "saturated_fat": 1.2,
     "fiber": 0.8, "sugar": 1.0, "sodium": 340.0, "calcium": 35.0, "iron": 1.4, "vitamin_c": 6.5,
     "dietary_preference": "Non-Vegetarian", "health_score": 95},
    {"food_name": "Chicken Curry (Home Style)", "category": "Poultry & Meat", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 200.0, "serving_unit": "g", "household_serving": "1 bowl with gravy",
     "calories": 175.0, "carbs": 4.5, "protein": 21.0, "fat": 8.2, "saturated_fat": 2.1,
     "fiber": 1.2, "sugar": 1.8, "sodium": 380.0, "calcium": 25.0, "iron": 1.6, "vitamin_c": 5.0,
     "dietary_preference": "Non-Vegetarian", "health_score": 88},
    {"food_name": "Chicken Biryani (Hyderabadi)", "category": "Rice & Meat", "brand": "Indian Cuisine",
     "food_type": "Cooked Food", "serving_size": 250.0, "serving_unit": "g", "household_serving": "1 plate",
     "calories": 195.0, "carbs": 24.5, "protein": 11.8, "fat": 5.8, "saturated_fat": 1.8,
     "fiber": 1.5, "sugar": 1.2, "sodium": 420.0, "calcium": 28.0, "iron": 1.5, "vitamin_c": 3.5,
     "dietary_preference": "Non-Vegetarian", "health_score": 76},
    {"food_name": "Fish Curry (Rohu / Indian Carp)", "category": "Fish & Seafood", "brand": "Homemade / Generic",
     "food_type": "Cooked Food", "serving_size": 180.0, "serving_unit": "g", "household_serving": "1 piece with curry",
     "calories": 145.0, "carbs": 3.8, "protein": 17.5, "fat": 6.5, "saturated_fat": 1.4,
     "fiber": 1.0, "sugar": 1.2, "sodium": 310.0, "calcium": 75.0, "iron": 1.8, "vitamin_c": 4.0,
     "dietary_preference": "Non-Vegetarian", "health_score": 91},

    # Fitness & Health Supplements
    {"food_name": "Optimum Nutrition Whey Protein Powder", "category": "Protein Supplements", "brand": "Optimum Nutrition",
     "food_type": "Supplement", "serving_size": 30.0, "serving_unit": "g", "household_serving": "1 scoop (30g)",
     "calories": 395.0, "carbs": 9.5, "protein": 78.0, "fat": 4.5, "saturated_fat": 2.5,
     "fiber": 1.5, "sugar": 4.0, "sodium": 350.0, "calcium": 420.0, "iron": 1.2, "vitamin_c": 0.0,
     "dietary_preference": "Vegetarian", "health_score": 95},
    {"food_name": "Rolled Oats (Raw)", "category": "Grains & Cereals", "brand": "Generic",
     "food_type": "Grain", "serving_size": 40.0, "serving_unit": "g", "household_serving": "1/2 cup (40g)",
     "calories": 389.0, "carbs": 66.3, "protein": 16.9, "fat": 6.9, "saturated_fat": 1.2,
     "fiber": 10.6, "sugar": 1.0, "sodium": 2.0, "calcium": 54.0, "iron": 4.7, "vitamin_c": 0.0,
     "dietary_preference": "Vegan", "health_score": 96},
    {"food_name": "Peanut Butter (Natural Unsweetened)", "category": "Nut Butters", "brand": "Generic",
     "food_type": "Spread", "serving_size": 32.0, "serving_unit": "g", "household_serving": "2 tablespoons",
     "calories": 588.0, "carbs": 20.0, "protein": 25.1, "fat": 50.4, "saturated_fat": 10.3,
     "fiber": 6.0, "sugar": 4.2, "sodium": 17.0, "calcium": 43.0, "iron": 1.9, "vitamin_c": 0.0,
     "dietary_preference": "Vegan", "health_score": 88},
    {"food_name": "Raw Almonds", "category": "Nuts & Seeds", "brand": "Generic",
     "food_type": "Raw Nut", "serving_size": 28.0, "serving_unit": "g", "household_serving": "1 ounce / 23 almonds",
     "calories": 579.0, "carbs": 21.6, "protein": 21.2, "fat": 49.9, "saturated_fat": 3.8,
     "fiber": 12.5, "sugar": 4.4, "sodium": 1.0, "calcium": 269.0, "iron": 3.7, "vitamin_c": 0.0,
     "dietary_preference": "Vegan", "health_score": 94},
    {"food_name": "Walnuts (Raw Halves)", "category": "Nuts & Seeds", "brand": "Generic",
     "food_type": "Raw Nut", "serving_size": 28.0, "serving_unit": "g", "household_serving": "1 ounce (14 halves)",
     "calories": 654.0, "carbs": 13.7, "protein": 15.2, "fat": 65.2, "saturated_fat": 6.1,
     "fiber": 6.7, "sugar": 2.6, "sodium": 2.0, "calcium": 98.0, "iron": 2.9, "vitamin_c": 1.3,
     "dietary_preference": "Vegan", "health_score": 92},
]

def preprocess_and_merge_datasets(usda_path="comprehensive_foods_usda.csv", output_dir="data"):
    print("Loading USDA comprehensive foods dataset...")
    df_usda = pd.read_csv(usda_path)
    print(f"Loaded {len(df_usda)} USDA items.")

    # Select and standardize columns
    # USDA columns: ['fdc_id', 'food_name', 'data_type', 'food_category', 'brand_owner', 'brand_name',
    # 'ingredients', 'serving_size', 'serving_unit', 'household_serving', 'calories', 'carbs_g', 'calcium_mg',
    # 'fat_g', 'protein_g', 'saturated_fat_g', 'vitamin_c_mg', 'fiber_g', 'iron_mg', 'sodium_mg', 'sugar_g',
    # 'cholesterol_mg', 'health_score', 'food_type']

    rename_map = {
        'fdc_id': 'food_id',
        'food_category': 'category',
        'brand_name': 'brand',
        'carbs_g': 'carbs',
        'fat_g': 'fat',
        'protein_g': 'protein',
        'saturated_fat_g': 'saturated_fat',
        'fiber_g': 'fiber',
        'sugar_g': 'sugar',
        'sodium_mg': 'sodium',
        'calcium_mg': 'calcium',
        'iron_mg': 'iron',
        'vitamin_c_mg': 'vitamin_c'
    }
    df_usda = df_usda.rename(columns=rename_map)

    # Filter out records with invalid calories or protein
    df_usda = df_usda.dropna(subset=['calories', 'protein', 'food_name']).copy()
    df_usda = df_usda[(df_usda['calories'] >= 0) & (df_usda['calories'] <= 950)]
    
    # Fill numeric columns with 0 if NaN
    num_cols = ['carbs', 'protein', 'fat', 'saturated_fat', 'fiber', 'sugar', 'sodium', 'calcium', 'iron', 'vitamin_c']
    for col in num_cols:
        if col in df_usda.columns:
            df_usda[col] = pd.to_numeric(df_usda[col], errors='coerce').fillna(0.0)
        else:
            df_usda[col] = 0.0

    df_usda['serving_size'] = pd.to_numeric(df_usda['serving_size'], errors='coerce').fillna(100.0)
    df_usda['serving_unit'] = df_usda['serving_unit'].fillna('g')
    df_usda['brand'] = df_usda['brand'].fillna(df_usda['brand_owner']).fillna('Generic')
    df_usda['household_serving'] = df_usda['household_serving'].fillna('100 g')

    # Infer dietary preference for USDA items
    def infer_dietary_pref(row):
        name = str(row['food_name']).lower()
        cat = str(row.get('category', '')).lower()
        non_veg_terms = ['chicken', 'beef', 'pork', 'fish', 'turkey', 'lamb', 'bacon', 'salmon', 'tuna', 'shrimp', 'meat', 'mutton']
        egg_terms = ['egg', 'omelet', 'omelette']
        dairy_terms = ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'whey']

        if any(term in name or term in cat for term in non_veg_terms):
            return "Non-Vegetarian"
        if any(term in name for term in egg_terms):
            return "Eggetarian"
        if any(term in name or term in cat for term in dairy_terms):
            return "Vegetarian"
        return "Vegan"

    print("Inferring dietary preferences...")
    df_usda['dietary_preference'] = df_usda.apply(infer_dietary_pref, axis=1)

    # Convert Indian foods list to DataFrame
    df_indian = pd.DataFrame(INDIAN_FOODS_DATA)
    # Assign unique food_ids to Indian foods starting above max USDA food_id
    max_id = int(df_usda['food_id'].max()) if len(df_usda) > 0 else 1000000
    df_indian['food_id'] = range(max_id + 1, max_id + 1 + len(df_indian))

    # Ensure required columns align
    all_cols = [
        'food_id', 'food_name', 'category', 'brand', 'food_type', 'serving_size', 'serving_unit',
        'household_serving', 'calories', 'carbs', 'protein', 'fat', 'saturated_fat', 'fiber',
        'sugar', 'sodium', 'calcium', 'iron', 'vitamin_c', 'dietary_preference', 'health_score'
    ]

    for col in all_cols:
        if col not in df_usda.columns:
            df_usda[col] = 0.0

    df_usda_sub = df_usda[all_cols].copy()
    df_indian_sub = df_indian[all_cols].copy()

    # Prepend Indian foods so they are easily discoverable & prominent in searches
    df_combined = pd.concat([df_indian_sub, df_usda_sub], ignore_index=True)
    df_combined['food_name'] = df_combined['food_name'].astype(str).str.strip()

    # Deduplicate by food_name lower
    df_combined['name_lower'] = df_combined['food_name'].str.lower()
    df_combined = df_combined.drop_duplicates(subset=['name_lower']).drop(columns=['name_lower'])

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "processed"), exist_ok=True)

    out_csv = os.path.join(output_dir, "food_nutrition.csv")
    out_processed_csv = os.path.join(output_dir, "processed", "food_nutrition.csv")

    df_combined.to_csv(out_csv, index=False)
    df_combined.to_csv(out_processed_csv, index=False)

    print(f"Successfully processed {len(df_combined)} foods!")
    print(f"Saved to:\n  - {out_csv}\n  - {out_processed_csv}")
    return df_combined

if __name__ == "__main__":
    preprocess_and_merge_datasets()

