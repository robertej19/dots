import numpy as np
import matplotlib.pyplot as plt
#test comment
# Conversion factor from pounds to kilograms.
lb_to_kg = 0.45359237

# Male DOTS constants.
A_m = -0.000001093
B_m = 0.0007391293
C_m = -0.1918759221
D_m = 24.0900756
E_m = -307.75076

# Female DOTS constants.
A_f = -0.000001120
B_f = 0.000684
C_f = -0.177
D_f = 21.384
E_f = -239.85

def dots_points_custom(bodyweight_lb, weight_lifted_lb, A, B, C, D, E):
    """
    Calculate the DOTS points given bodyweight and weight lifted in lbs,
    using the provided polynomial coefficients.
    """
    bw_kg = bodyweight_lb * lb_to_kg
    lifted_kg = weight_lifted_lb * lb_to_kg
    denominator = A * bw_kg**4 + B * bw_kg**3 + C * bw_kg**2 + D * bw_kg + E
    return lifted_kg * 500 / denominator

# Define ranges in lbs.
bw_vals_lb = np.linspace(100, 400, 300)      # Bodyweight: 100 to 400 lbs
lifted_vals_lb = np.linspace(100, 800, 300)    # Weight lifted: 100 to 800 lbs

# Create a grid for bodyweight and weight lifted.
BW_lb, Lifted_lb = np.meshgrid(bw_vals_lb, lifted_vals_lb)

# Calculate DOTS points for males and females.
male_dots = dots_points_custom(BW_lb, Lifted_lb, A_m, B_m, C_m, D_m, E_m)
female_dots = dots_points_custom(BW_lb, Lifted_lb, A_f, B_f, C_f, D_f, E_f)

plt.figure(figsize=(10, 8))

# Define contour levels and discrete colors.
levels = np.array([50, 100, 150, 200, 250])
discrete_colors = ["red", "orange", "yellow", "green", "blue"]

# Plot male contours with dashed lines.
male_contours = plt.contour(
    BW_lb, Lifted_lb, male_dots, levels=levels,
    colors=discrete_colors, linestyles=["dashed"]*len(levels), linewidths=1.5
)

# Plot female contours with solid lines.
female_contours = plt.contour(
    BW_lb, Lifted_lb, female_dots, levels=levels,
    colors=discrete_colors, linestyles=["solid"]*len(levels), linewidths=1.5
)

# Function to compute manual label positions so labels appear near the horizontal center.
def compute_manual_positions(contour):
    manual_positions = []
    for level, seg_list in zip(contour.levels, contour.allsegs):
        if not seg_list:
            continue
        best_seg = None
        best_width = -np.inf
        for seg in seg_list:
            if seg.size == 0:
                continue
            xs = seg[:, 0]
            if xs.size == 0:
                continue
            width = xs.max() - xs.min()
            if width > best_width:
                best_width = width
                best_seg = seg
        if best_seg is not None and best_seg.size > 0:
            xs = best_seg[:, 0]
            center_x = (xs.max() + xs.min()) / 2.0
            idx = np.argmin(np.abs(xs - center_x))
            label_point = best_seg[idx]
            manual_positions.append(label_point)
    return manual_positions

male_manual_positions = compute_manual_positions(male_contours)
female_manual_positions = compute_manual_positions(female_contours)

plt.clabel(male_contours, manual=male_manual_positions, inline=True, fontsize=10, fmt='%d')
plt.clabel(female_contours, manual=female_manual_positions, inline=True, fontsize=10, fmt='%d')

plt.xlabel("Bodyweight (lbs)")
plt.ylabel("Weight Lifted (lbs)")
plt.title("DOTS Points Contours (50-250)\nFemales (solid) vs Males (dashed)")

plt.show()
