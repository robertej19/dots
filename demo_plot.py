import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import brentq
import matplotlib.collections as mcoll
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

def female_score(lifted_lb):
    """Compute DOTS score for a 170-lb female."""
    return dots_points(170, lifted_lb, A_f, B_f, C_f, D_f, E_f)

def male_score(lifted_lb):
    """Compute DOTS score for a 225-lb male."""
    return dots_points(225, lifted_lb, A_m, B_m, C_m, D_m, E_m)

def male_required(female_lift):
    """
    Given a female lift (in lbs), solve for the male lift (in lbs)
    that produces the same DOTS score.
    """
    target = female_score(female_lift)
    def diff(male_lift):
        return male_score(male_lift) - target
    # brentq finds the root in the interval; adjust if needed.
    return brentq(diff, 50, 2000)

# Generate values for the female lift from 100 to 800 lbs (in 1-lb increments)
female_lifts = np.arange(100, 801, 1)
male_lifts_equivalent = np.array([male_required(f) for f in female_lifts])
dots_values = np.array([female_score(f) for f in female_lifts])  # same as male score for equivalence

# Create a DataFrame to tabulate the results.
df = pd.DataFrame({
    'Female Lift (lbs)': female_lifts,
    'Male Required Lift (lbs)': male_lifts_equivalent,
    'DOTS Score': dots_values
})

print(df.head())

# To create a colored line, we'll use a LineCollection.
# First, create line segments from the data points.
points = np.array([female_lifts, male_lifts_equivalent]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

# Normalize the DOTS scores for the colormap.
norm = plt.Normalize(dots_values.min(), dots_values.max())
lc = mcoll.LineCollection(segments, cmap='viridis', norm=norm)
# Set the color for each segment using the corresponding DOTS score.
lc.set_array(dots_values[:-1])
lc.set_linewidth(2)

# Plotting.
fig, ax = plt.subplots(figsize=(10, 6))
ax.add_collection(lc)
ax.set_xlim(female_lifts.min(), female_lifts.max())
ax.set_ylim(male_lifts_equivalent.min(), male_lifts_equivalent.max())
ax.set_xlabel("Female Lift (lbs)")
ax.set_ylabel("Male Required Lift (lbs)")
ax.set_title("Male Lift Required to Match DOTS Score of a 170 lb Female\n(Color indicates DOTS Score)")
cbar = fig.colorbar(lc, ax=ax)
cbar.set_label("DOTS Score")
ax.grid(True)
plt.show()