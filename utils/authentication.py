"""
NutriFit AI - Authentication & Session Helper
Provides password hashing with bcrypt, user registration, authentication,
and default guest/demo session for immediate exploration.
"""

import bcrypt
from datetime import datetime
from src.database import get_session, User, UserProfile, WeightHistory

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def register_user(name: str, email: str, password: str, profile_data: dict = None) -> tuple[bool, str, int]:
    session = get_session()
    try:
        existing = session.query(User).filter_by(email=email.strip().lower()).first()
        if existing:
            return False, "An account with this email already exists.", existing.user_id

        p_hash = hash_password(password)
        user = User(
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=p_hash
        )
        session.add(user)
        session.flush()

        # Create user profile
        p_data = profile_data or {}
        profile = UserProfile(
            user_id=user.user_id,
            age=int(p_data.get('age', 22)),
            sex=str(p_data.get('sex', 'Male')),
            height=float(p_data.get('height', 170.0)),
            weight=float(p_data.get('weight', 65.0)),
            activity_level=str(p_data.get('activity_level', 'Moderately active')),
            goal=str(p_data.get('goal', 'Weight Gain')),
            target_weight=float(p_data.get('target_weight', 70.0)),
            dietary_preference=str(p_data.get('dietary_preference', 'Vegetarian')),
            allergies=str(p_data.get('allergies', 'None'))
        )
        session.add(profile)

        # Baseline weight history
        wh = WeightHistory(
            user_id=user.user_id,
            weight=float(p_data.get('weight', 65.0)),
            recorded_at=datetime.utcnow()
        )
        session.add(wh)

        session.commit()
        return True, "User registered successfully!", user.user_id
    except Exception as e:
        session.rollback()
        return False, f"Registration error: {e}", 0
    finally:
        session.close()

def authenticate_user(email: str, password: str) -> tuple[bool, str, any]:
    session = get_session()
    try:
        user = session.query(User).filter_by(email=email.strip().lower()).first()
        if not user:
            return False, "Invalid email or password.", None
        if verify_password(password, user.password_hash):
            return True, "Login successful!", user.user_id
        return False, "Invalid email or password.", None
    finally:
        session.close()

def get_or_create_demo_user() -> int:
    """Ensures a default interactive user exists for zero-friction launch."""
    session = get_session()
    try:
        user = session.query(User).filter_by(email="demo@nutrifit.ai").first()
        if user:
            return user.user_id
        
        success, msg, uid = register_user(
            name="Rahul Sharma",
            email="demo@nutrifit.ai",
            password="nutrifitdemo",
            profile_data={
                "age": 22,
                "sex": "Male",
                "height": 170.0,
                "weight": 65.0,
                "activity_level": "Moderately active",
                "goal": "Weight Gain",
                "target_weight": 70.0,
                "dietary_preference": "Vegetarian",
                "allergies": "None"
            }
        )
        return uid
    finally:
        session.close()

