import numpy as np
from scipy.optimize import brentq
import plotly.graph_objects as go
import plotly.express as px

lb_to_kg = 0.45359237

# Male DOTS constants.
A_m = -0.000001093
B_m = 0.0007391293
C_m = -0.1918759221
D_m = 24.0900756
E_m = -307.75076

# Female DOTS constants.
A_f  = -0.0000010706
B_f  = 0.0005158568
C_f  = -0.1126655495
D_f  = 13.6175032
E_f = -57.96288 

def dots_points(bodyweight_lb, weight_lifted_lb, A, B, C, D, E):
    """
    Compute DOTS points.
    Both bodyweight and weight lifted are given in lbs.
    """
    bw_kg = bodyweight_lb * lb_to_kg
    lifted_kg = weight_lifted_lb * lb_to_kg
    denominator = A * bw_kg**4 + B * bw_kg**3 + C * bw_kg**2 + D * bw_kg + E
    return lifted_kg * 500 / denominator

def get_dots(lift, bodyweight, gender):
    """Return DOTS score for a given lift, bodyweight, and gender."""
    if gender.lower() == 'male':
        return dots_points(bodyweight, lift, A_m, B_m, C_m, D_m, E_m)
    else:
        return dots_points(bodyweight, lift, A_f, B_f, C_f, D_f, E_f)

def get_required_lift(target, bodyweight, gender):
    """Solve for the required lift that yields the target DOTS score."""
    def diff(lift):
        return get_dots(lift, bodyweight, gender) - target
    return brentq(diff, 50, 2000)

def create_chart(lifter1_bodyweight=170, lifter1_gender='Female',
                 lifter2_bodyweight=225, lifter2_gender='Male'):
    """
    Create a Plotly figure showing Lifter 2's required lift (y-axis) vs.
    Lifter 1's lift (x-axis), given each lifter’s bodyweight and gender.
    All displayed numbers are rounded to whole numbers.
    """
    # Lifter 1 lift values from 100 to 800 lbs.
    lifts1 = np.arange(100, 801, 1)
    # Compute DOTS score for Lifter 1 for each lift.
    dots_values = np.array([get_dots(lift, lifter1_bodyweight, lifter1_gender)
                             for lift in lifts1])
    # Compute required Lifter 2 lift for the same DOTS score.
    required_lifts = np.array([get_required_lift(d, lifter2_bodyweight, lifter2_gender)
                                for d in dots_values])
    
    # Round all values to whole numbers.
    lifts1_round = np.round(lifts1).astype(int)
    dots_round = np.round(dots_values).astype(int)
    required_round = np.round(required_lifts).astype(int)
    
    # Create colored line segments (gradient based on DOTS score).
    traces = []
    for i in range(len(lifts1_round) - 1):
        xseg = [lifts1_round[i], lifts1_round[i+1]]
        yseg = [required_round[i], required_round[i+1]]
        avg_dots = (dots_round[i] + dots_round[i+1]) / 2.0
        # Normalize for the Viridis colorscale.
        fraction = ((avg_dots - dots_round.min()) /
                    (dots_round.max() - dots_round.min())
                    if dots_round.max() > dots_round.min() else 0)
        color = px.colors.sample_colorscale('Viridis', fraction)[0]
        traces.append(go.Scatter(
            x=xseg,
            y=yseg,
            mode='lines',
            line=dict(color=color, width=3),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Create custom hover text for each data point.
    hover_text = [
        f"Lifter 1: {lifter1_gender} ({lifter1_bodyweight} lb) lifting {lift} lbs = {dots} DOTS score<br>"
        f"Lifter 2: {lifter2_gender} ({lifter2_bodyweight} lb) needs to lift {req} lbs for the same score"
        for lift, dots, req in zip(lifts1_round, dots_round, required_round)
    ]
    
    marker_trace = go.Scatter(
        x=lifts1_round,
        y=required_round,
        mode='markers',
        marker=dict(
            size=6,
            color=dots_round,
            colorscale='Viridis',
            colorbar=dict(title="DOTS Score")
        ),
        text=hover_text,
        hovertemplate="%{text}<extra></extra>",
        showlegend=False
    )
    
    # Build the figure with fixed axis ranges.
    fig = go.Figure(data=traces + [marker_trace])
    fig.update_layout(
        title=f"Comparison between {lifter1_bodyweight} lb {lifter1_gender} Lifter and "
              f"{lifter2_bodyweight} lb {lifter2_gender} Lifter",
        xaxis_title="Lifter 1 Lift (lbs)",
        yaxis_title="Lifter 2 Required Lift (lbs)",
        xaxis=dict(range=[100, 800]),
        yaxis=dict(range=[100, 1600]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template="plotly_dark"
    )
    
    return fig
