"""
NutriFit AI - Progress Tracker Module
Tracks historical body weight, adherence trends, and provides experimental trend estimation.
Note: Weight changes depend on energy balance, hydration, glycogen, and metabolic factors.
Estimations are statistical approximations, not medical diagnoses.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import numpy as np

def compute_weight_trend(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    history: List of dicts with keys: ['weight', 'recorded_at'] sorted by date.
    Returns: current weight, initial weight, net change, and 30-day projection trend.
    """
    if not history:
        return {
            "current_weight": 0.0,
            "starting_weight": 0.0,
            "net_change": 0.0,
            "weekly_rate": 0.0,
            "trend_direction": "Stable",
            "projection_30d": 0.0,
            "disclaimer": "No weight logs recorded yet."
        }

    weights = [float(h['weight']) for h in history]
    dates = [h['recorded_at'] for h in history]

    current_w = weights[-1]
    starting_w = weights[0]
    net_change = round(current_w - starting_w, 2)

    if len(weights) < 2:
        return {
            "current_weight": current_w,
            "starting_weight": starting_w,
            "net_change": 0.0,
            "weekly_rate": 0.0,
            "trend_direction": "Baseline logged",
            "projection_30d": current_w,
            "disclaimer": "Log at least 2 weight readings over time to view statistical trend estimates."
        }

    # Calculate days from baseline
    t0 = dates[0] if isinstance(dates[0], datetime) else datetime.fromisoformat(str(dates[0]))
    day_nums = []
    for d in dates:
        dt = d if isinstance(d, datetime) else datetime.fromisoformat(str(d))
        day_nums.append((dt - t0).total_seconds() / 86400.0)

    # Linear regression slope (kg / day)
    x = np.array(day_nums)
    y = np.array(weights)
    if np.max(x) > 0:
        slope, intercept = np.polyfit(x, y, 1)
        weekly_rate = round(slope * 7.0, 2)
        projected_30d = round(current_w + (slope * 30.0), 1)
    else:
        weekly_rate = 0.0
        projected_30d = current_w

    if weekly_rate < -0.1:
        trend_direction = "Downwards (Losing)"
    elif weekly_rate > 0.1:
        trend_direction = "Upwards (Gaining)"
    else:
        trend_direction = "Stable (Maintaining)"

    return {
        "current_weight": current_w,
        "starting_weight": starting_w,
        "net_change": net_change,
        "weekly_rate": weekly_rate,
        "trend_direction": trend_direction,
        "projection_30d": projected_30d,
        "disclaimer": "Projections are mathematical trend approximations based on recent logs and do not account for metabolic adaptation."
    }

def compute_calorie_adherence(daily_logs: List[Dict[str, Any]], target_calories: float) -> Dict[str, Any]:
    """
    Computes adherence percentage (% of days intake was within ±15% of target).
    """
    if not daily_logs:
        return {"adherence_rate": 100.0, "compliant_days": 0, "total_days": 0}

    compliant = 0
    tolerance = target_calories * 0.15
    for day in daily_logs:
        cals = day.get('total_calories', 0.0)
        if (target_calories - tolerance) <= cals <= (target_calories + tolerance):
            compliant += 1

    rate = round((compliant / len(daily_logs)) * 100.0, 1) if daily_logs else 100.0
    return {
        "adherence_rate": rate,
        "compliant_days": compliant,
        "total_days": len(daily_logs)
    }

