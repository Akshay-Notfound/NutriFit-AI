"""
NutriFit AI - Database Layer (SQLAlchemy ORM)
Supports PostgreSQL via DATABASE_URL or SQLite default (sqlite:///nutrifit.db).
"""

import os
from datetime import datetime, date
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import pandas as pd

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    weight_history = relationship("WeightHistory", back_populates="user", cascade="all, delete-orphan")
    diet_plans = relationship("DietPlan", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True, nullable=False)
    age = Column(Integer, nullable=False, default=25)
    sex = Column(String(10), nullable=False, default='Male') # Male, Female
    height = Column(Float, nullable=False, default=170.0) # in cm
    weight = Column(Float, nullable=False, default=65.0) # in kg
    activity_level = Column(String(30), nullable=False, default='Moderately active')
    goal = Column(String(30), nullable=False, default='Maintenance') # Weight Loss, Maintenance, Weight Gain
    target_weight = Column(Float, nullable=True)
    dietary_preference = Column(String(30), default='Vegetarian') # Vegetarian, Vegan, Eggetarian, Non-Vegetarian
    allergies = Column(String(255), default='')

    user = relationship("User", back_populates="profile")

class FoodItem(Base):
    __tablename__ = 'food_items'
    food_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default='General')
    brand = Column(String(100), default='Generic')
    food_type = Column(String(50), default='Food')
    serving_size = Column(Float, default=100.0)
    serving_unit = Column(String(20), default='g')
    household_serving = Column(String(100), default='100 g')
    dietary_preference = Column(String(30), default='Vegetarian')

    nutrition = relationship("FoodNutrition", back_populates="item", uselist=False, cascade="all, delete-orphan")
    food_logs = relationship("FoodLog", back_populates="food_item")
    plan_items = relationship("DietPlanItem", back_populates="food_item")

class FoodNutrition(Base):
    __tablename__ = 'food_nutrition'
    id = Column(Integer, primary_key=True, autoincrement=True)
    food_id = Column(Integer, ForeignKey('food_items.food_id'), unique=True, nullable=False)
    calories = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fibre = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    saturated_fat = Column(Float, default=0.0)
    sugar = Column(Float, default=0.0)
    sodium = Column(Float, default=0.0)
    calcium = Column(Float, default=0.0)
    iron = Column(Float, default=0.0)
    vitamin_c = Column(Float, default=0.0)
    health_score = Column(Float, default=50.0)

    item = relationship("FoodItem", back_populates="nutrition")

class FoodLog(Base):
    __tablename__ = 'food_logs'
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    food_id = Column(Integer, ForeignKey('food_items.food_id'), nullable=False)
    quantity = Column(Float, nullable=False, default=100.0) # grams or ml
    consumed_at = Column(DateTime, default=datetime.utcnow)
    meal_type = Column(String(30), nullable=False, default='Snacks') # Breakfast, Lunch, Dinner, Snacks

    user = relationship("User", back_populates="food_logs")
    food_item = relationship("FoodItem", back_populates="food_logs")

class DietPlan(Base):
    __tablename__ = 'diet_plans'
    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    date = Column(Date, default=date.today)
    goal = Column(String(50), default='Maintenance')
    calorie_target = Column(Float, default=2000.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="diet_plans")
    items = relationship("DietPlanItem", back_populates="plan", cascade="all, delete-orphan")

class DietPlanItem(Base):
    __tablename__ = 'diet_plan_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey('diet_plans.plan_id'), nullable=False)
    food_id = Column(Integer, ForeignKey('food_items.food_id'), nullable=False)
    meal_type = Column(String(30), nullable=False) # Breakfast, Lunch, Dinner, Snacks
    quantity = Column(Float, default=100.0) # grams / ml

    plan = relationship("DietPlan", back_populates="items")
    food_item = relationship("FoodItem", back_populates="plan_items")

class WeightHistory(Base):
    __tablename__ = 'weight_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    weight = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="weight_history")

class Recommendation(Base):
    __tablename__ = 'recommendations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    food_id = Column(Integer, ForeignKey('food_items.food_id'), nullable=False)
    recommendation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")

# Database connection setup
def get_database_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        # Default to local SQLite database in project directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "nutrifit.db")
        url = f"sqlite:///{db_path}"
    elif url.startswith("postgres://"):
        # Fix for modern SQLAlchemy
        url = url.replace("postgres://", "postgresql://", 1)
    return url

_engine = None
_SessionFactory = None

def get_engine():
    global _engine
    if _engine is None:
        db_url = get_database_url()
        connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
        _engine = create_engine(db_url, connect_args=connect_args)
    return _engine

def get_session():
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _SessionFactory()

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    seed_foods_if_empty()

def seed_foods_if_empty():
    session = get_session()
    try:
        count = session.query(FoodItem).count()
        if count > 0:
            return
        
        # Load CSV
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, "data", "food_nutrition.csv")
        if not os.path.exists(csv_path):
            csv_path = os.path.join(base_dir, "data", "processed", "food_nutrition.csv")
        
        if not os.path.exists(csv_path):
            return

        print("Seeding database with food items...")
        df = pd.read_csv(csv_path)
        
        # Insert in batches
        food_items = []
        food_nutritions = []

        for _, row in df.iterrows():
            fid = int(row['food_id'])
            food_items.append(FoodItem(
                food_id=fid,
                name=str(row['food_name']),
                category=str(row.get('category', 'General')),
                brand=str(row.get('brand', 'Generic')),
                food_type=str(row.get('food_type', 'Food')),
                serving_size=float(row.get('serving_size', 100.0)),
                serving_unit=str(row.get('serving_unit', 'g')),
                household_serving=str(row.get('household_serving', '100 g')),
                dietary_preference=str(row.get('dietary_preference', 'Vegetarian'))
            ))
            food_nutritions.append(FoodNutrition(
                food_id=fid,
                calories=float(row.get('calories', 0.0)),
                protein=float(row.get('protein', 0.0)),
                carbs=float(row.get('carbs', 0.0)),
                fibre=float(row.get('fiber', 0.0)),
                fat=float(row.get('fat', 0.0)),
                saturated_fat=float(row.get('saturated_fat', 0.0)),
                sugar=float(row.get('sugar', 0.0)),
                sodium=float(row.get('sodium', 0.0)),
                calcium=float(row.get('calcium', 0.0)),
                iron=float(row.get('iron', 0.0)),
                vitamin_c=float(row.get('vitamin_c', 0.0)),
                health_score=float(row.get('health_score', 50.0))
            ))

        session.bulk_save_objects(food_items)
        session.bulk_save_objects(food_nutritions)
        session.commit()
        print(f"Seeded {len(food_items)} food items into the database!")
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    init_db()

