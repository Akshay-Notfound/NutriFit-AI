"""
NutriFit AI - Charts & Visual Analytics
Plotly visualization functions styled for the modern dark dashboard aesthetic:
- Circular Calorie Gauge
- Triple Macro Rings (Protein, Carbs, Fat)
- Weight Trend Graph with smooth gradient fill
- Nutrients Adherence Bar Chart
- Macro Breakdown Donut
- Radar Chart for Food Comparison
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any

# Theme Palette matching user UI mockup (dark obsidian, vibrant emerald, cyan, amber, coral)
BG_COLOR = "#0D1117"
CARD_BG = "#161B22"
ACCENT_GREEN = "#00E676"
ACCENT_CYAN = "#00E5FF"
ACCENT_ORANGE = "#FF9100"
ACCENT_PURPLE = "#7C4DFF"
TEXT_COLOR = "#E6EDF3"
TEXT_MUTED = "#8B949E"

def create_circular_calorie_gauge(consumed: float, target: float) -> go.Figure:
    """
    Creates the main circular energy progress indicator matching DietScan/Calkilo style.
    """
    pct = min(100.0, (consumed / target * 100.0)) if target > 0 else 0
    rem = max(0.0, target - consumed)

    fig = go.Figure(go.Pie(
        values=[consumed, rem],
        labels=["Consumed", "Remaining"],
        hole=0.76,
        sort=False,
        direction='clockwise',
        marker=dict(
            colors=[ACCENT_GREEN, "#21262D"],
            line=dict(color="#0D1117", width=3)
        ),
        textinfo='none',
        hoverinfo='label+value'
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=220,
        annotations=[
            dict(
                text=f"<span style='font-size:32px; font-weight:800; color:#FFFFFF;'>{int(consumed)}</span><br>"
                     f"<span style='font-size:13px; font-weight:600; color:{ACCENT_GREEN};'>CALORIES</span><br>"
                     f"<span style='font-size:11px; color:{TEXT_MUTED};'>of {int(target)} kcal</span>",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(family="sans-serif")
            )
        ]
    )
    return fig

def create_macro_gauge(label: str, consumed: float, target: float, color: str) -> go.Figure:
    """Single macro ring gauge for Protein, Carbs, or Fat."""
    pct = min(100.0, (consumed / target * 100.0)) if target > 0 else 0
    rem = max(0.0, target - consumed)

    fig = go.Figure(go.Pie(
        values=[consumed, rem],
        hole=0.72,
        sort=False,
        direction='clockwise',
        marker=dict(
            colors=[color, "#21262D"],
            line=dict(color="#0D1117", width=2)
        ),
        textinfo='none',
        hoverinfo='label+value'
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(t=5, b=5, l=5, r=5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=140,
        annotations=[
            dict(
                text=f"<span style='font-size:18px; font-weight:700; color:#FFFFFF;'>{int(consumed)}g</span><br>"
                     f"<span style='font-size:10px; color:{TEXT_MUTED};'>of {int(target)}g</span>",
                x=0.5, y=0.5,
                showarrow=False
            )
        ]
    )
    return fig

def create_weight_trend_chart(history: List[Dict[str, Any]]) -> go.Figure:
    """
    Renders the weight history curve with glowing line and points matching the user wireframe.
    """
    if not history:
        # Default placeholder curve if no logs yet
        dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weights = [66.0, 65.8, 65.5, 65.4, 65.2, 65.1, 65.0]
    else:
        dates = [h['recorded_at'].strftime("%b %d") if hasattr(h['recorded_at'], 'strftime') else str(h['recorded_at'])[:10] for h in history]
        weights = [float(h['weight']) for h in history]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=weights,
        mode='lines+markers',
        line=dict(color=ACCENT_GREEN, width=3, shape='spline'),
        marker=dict(size=8, color=ACCENT_GREEN, line=dict(color='#FFFFFF', width=1.5)),
        fill='tozeroy',
        fillcolor='rgba(0, 230, 118, 0.08)',
        hoverinfo='x+y'
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(t=15, b=25, l=35, r=15),
        xaxis=dict(
            showgrid=False,
            color=TEXT_MUTED,
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#21262D",
            color=TEXT_MUTED,
            tickfont=dict(size=11)
        )
    )
    return fig

def create_nutrients_bar_chart(consumed: Dict[str, float], targets: Dict[str, Any]) -> go.Figure:
    """
    Vertical bar chart tracking % target / threshold for:
    Fiber, Sugar, Saturated Fat, Sodium, Calcium.
    """
    nutrients = ["Fiber", "Sugar", "Sat Fat", "Sodium", "Calcium"]
    percentages = [
        min(150.0, (consumed.get('fiber', 0.0) / max(targets.get('target_fiber_g', 25.0), 1)) * 100.0),
        min(150.0, (consumed.get('sugar', 0.0) / max(targets.get('sugar_limit_g', 35.0), 1)) * 100.0),
        min(150.0, (consumed.get('saturated_fat', 0.0) / max(targets.get('target_sat_fat_limit_g', 20.0), 1)) * 100.0),
        min(150.0, (consumed.get('sodium', 0.0) / max(targets.get('sodium_limit_mg', 2000.0), 1)) * 100.0),
        min(150.0, (consumed.get('calcium', 0.0) / max(targets.get('target_calcium_mg', 1000.0), 1)) * 100.0)
    ]
    colors = [
        ACCENT_GREEN,
        ACCENT_ORANGE if percentages[1] > 90 else ACCENT_GREEN,
        ACCENT_ORANGE if percentages[2] > 90 else ACCENT_CYAN,
        "#FF5252" if percentages[3] > 100 else ACCENT_CYAN,
        ACCENT_PURPLE
    ]

    fig = go.Figure(go.Bar(
        x=nutrients,
        y=percentages,
        marker=dict(color=colors, cornerradius=6),
        text=[f"{int(p)}%" for p in percentages],
        textposition='outside',
        textfont=dict(size=10, color=TEXT_COLOR)
    ))

    fig.add_hline(y=100, line_dash="dash", line_color="#30363D", annotation_text="100% Target", annotation_position="top right")

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(t=25, b=25, l=30, r=15),
        xaxis=dict(showgrid=False, color=TEXT_MUTED, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="#21262D", color=TEXT_MUTED, range=[0, 160], tickfont=dict(size=10)),
        showlegend=False
    )
    return fig

def create_food_comparison_radar(food1: Dict[str, Any], food2: Optional[Dict[str, Any]] = None) -> go.Figure:
    """Radar chart comparing two foods across standardized nutritional dimensions."""
    categories = ['Protein', 'Fiber', 'Low Fat', 'Low Sugar', 'Micronutrients']

    def calc_scores(f):
        pro_score = min(100, (float(f.get('protein', 0.0)) / 25.0) * 100)
        fib_score = min(100, (float(f.get('fiber', 0.0)) / 10.0) * 100)
        fat_score = max(0, 100 - (float(f.get('fat', 0.0)) / 30.0 * 100))
        sug_score = max(0, 100 - (float(f.get('sugar', 0.0)) / 40.0 * 100))
        micro_score = min(100, ((float(f.get('calcium', 0.0)) / 300.0) + (float(f.get('vitamin_c', 0.0)) / 40.0)) * 50)
        return [pro_score, fib_score, fat_score, sug_score, micro_score]

    scores1 = calc_scores(food1)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores1 + [scores1[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=food1.get('food_name', 'Original Food')[:22],
        line=dict(color='#FF5252', width=2)
    ))

    if food2:
        scores2 = calc_scores(food2)
        fig.add_trace(go.Scatterpolar(
            r=scores2 + [scores2[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=food2.get('food_name', 'Alternative')[:22],
            line=dict(color=ACCENT_GREEN, width=2)
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color=TEXT_MUTED, gridcolor="#21262D"),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=260,
        margin=dict(t=25, b=25, l=35, r=35),
        legend=dict(orientation="h", y=-0.15, font=dict(color=TEXT_COLOR, size=10))
    )
    return fig

