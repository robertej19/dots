import numpy as np
import matplotlib.pyplot as plt

# Conversion factor from pounds to kilograms.
lb_to_kg = 0.45359237

# Constants for the DOTS formula.
A = -0.000001093
B = 0.0007391293
C = -0.1918759221
D = 24.0900756
E = -307.75076

def dots_points(bodyweight_lb, weight_lifted_lb):
    """
    Calculate the DOTS points given bodyweight and weight lifted in lbs.
    Internally, these values are converted to kg.
    
    Parameters:
      bodyweight_lb      : Bodyweight in lbs.
      weight_lifted_lb   : Weight lifted in lbs.
    
    Returns:
      DOTS points as a float.
    """
    # Convert to kg
    bw_kg = bodyweight_lb * lb_to_kg
    lifted_kg = weight_lifted_lb * lb_to_kg
    # Compute denominator using the polynomial (with x in kg)
    denominator = A * bw_kg**4 + B * bw_kg**3 + C * bw_kg**2 + D * bw_kg + E
    # Calculate the DOTS points
    return lifted_kg * 500 / denominator

# Define ranges in lbs.
bw_vals_lb = np.linspace(100, 400, 300)      # Bodyweight: 100 to 400 lbs
lifted_vals_lb = np.linspace(100, 800, 300)    # Weight lifted: 100 to 800 lbs

# Create a grid for bodyweight and weight lifted.
BW_lb, Lifted_lb = np.meshgrid(bw_vals_lb, lifted_vals_lb)

# Calculate the DOTS points for each combination.
dots = dots_points(BW_lb, Lifted_lb)

plt.figure(figsize=(10, 8))
pcolormesh_plot = plt.pcolormesh(BW_lb, Lifted_lb, dots, shading='auto', cmap='viridis')
plt.colorbar(pcolormesh_plot, label="DOTS Points")

# Set gridlines every 50 lbs in light gray, and place them behind other plot elements.
ax = plt.gca()
ax.set_xticks(np.arange(100, 401, 50))
ax.set_yticks(np.arange(100, 801, 50))
ax.grid(True, color='lightgray', linestyle='-', linewidth=0.5)
#ax.set_axisbelow(True)

# Add labeled contours every 50 DOTS points.
levels = np.arange(50, np.max(dots) + 50, 50)
contours = plt.contour(BW_lb, Lifted_lb, dots, levels=levels, colors='white', linewidths=1)

# Compute manual label positions ensuring we skip any empty segments.
manual_positions = []
for level, seg_list in zip(contours.levels, contours.allsegs):
    if not seg_list:
        continue
    best_seg = None
    best_width = -np.inf
    for seg in seg_list:
        if seg.size == 0:  # Skip empty segments
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

# Increase the font size of the contour labels by setting fontsize to 14.
plt.clabel(contours, manual=manual_positions, inline=True, fontsize=14, fmt='%d')

plt.xlabel("Bodyweight (lbs)")
plt.ylabel("Weight Lifted (lbs)")
plt.title("DOTS Points Colormap (values computed using kg conversion)")

plt.show()
