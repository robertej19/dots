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

def female_score(lifted_lb, female_bodyweight):
    """Compute DOTS score for a female of specified weight."""
    return dots_points(female_bodyweight, lifted_lb, A_f, B_f, C_f, D_f, E_f)

def male_score(lifted_lb, male_bodyweight):
    """Compute DOTS score for a male of specified weight."""
    return dots_points(male_bodyweight, lifted_lb, A_m, B_m, C_m, D_m, E_m)

def male_required(female_lift, female_bodyweight, male_bodyweight):
    """
    Given a female lift (in lbs), solve for the male lift (in lbs)
    that produces the same DOTS score.
    """
    target = female_score(female_lift, female_bodyweight)
    def diff(male_lift):
        return male_score(male_lift, male_bodyweight) - target
    return brentq(diff, 50, 2000)

def create_chart(female_bodyweight=170, male_bodyweight=225):
    """
    Create a Plotly figure that shows the required male lift (y-axis) vs.
    female lift (x-axis), based on the given bodyweights.
    """
    # Generate values for the female lift from 100 to 800 lbs (1-lb increments)
    female_lifts = np.arange(100, 801, 1)
    male_lifts_equivalent = np.array([male_required(f, female_bodyweight, male_bodyweight)
                                      for f in female_lifts])
    dots_values = np.array([female_score(f, female_bodyweight) for f in female_lifts])
    
    # Create colored line segments for the gradient line.
    traces = []
    for i in range(len(female_lifts) - 1):
        # Endpoints for the segment.
        xseg = [female_lifts[i], female_lifts[i+1]]
        yseg = [male_lifts_equivalent[i], male_lifts_equivalent[i+1]]
        # Average DOTS value for the segment.
        seg_dots = (dots_values[i] + dots_values[i+1]) / 2.0
        # Normalize to sample the Viridis colorscale.
        fraction = (seg_dots - dots_values.min()) / (dots_values.max() - dots_values.min())
        color = px.colors.sample_colorscale('Viridis', fraction)[0]
        
        traces.append(go.Scatter(
            x=xseg,
            y=yseg,
            mode='lines',
            line=dict(color=color, width=3),
            hoverinfo='skip',  # disable hover on line segments
            showlegend=False
        ))
    
    # Create custom hover text for each data point.
    hover_text = [
        f"{female_bodyweight} lb woman lifting {f} lbs = {d:.2f} DOTS score<br>"
        f"{male_bodyweight} lb man needs to lift {m:.2f} lbs for the same score"
        for f, d, m in zip(female_lifts, dots_values, male_lifts_equivalent)
    ]
    
    # Overlay markers for interactive hover labels.
    marker_trace = go.Scatter(
        x=female_lifts,
        y=male_lifts_equivalent,
        mode='markers',
        marker=dict(
            size=6,
            color=dots_values,
            colorscale='Viridis',
            colorbar=dict(title="DOTS Score")
        ),
        text=hover_text,
        hovertemplate="%{text}<extra></extra>",
        showlegend=False
    )
    
    # Combine all traces into one figure.
    fig = go.Figure(data=traces + [marker_trace])
    
    # Set dynamic title and fixed axis ranges.
    fig.update_layout(
        title=f"Comparison between {female_bodyweight} lb Female Lifter and {male_bodyweight} lb Male Lifter",
        xaxis_title="Female Lift (lbs)",
        yaxis_title="Male Required Lift (lbs)",
        xaxis=dict(range=[100, 800]),
        yaxis=dict(range=[100, 1600]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template="plotly_dark"
    )
    
    return fig
