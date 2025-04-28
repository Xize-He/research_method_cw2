import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import matplotlib.animation as animation
from matplotlib.patches import Polygon

# Load data
df_adjusted = pd.read_csv('Results_21MAR2022.csv')
df_noadjust = pd.read_csv('Results_21MAR2022_nokcaladjust.csv')

# Indicators
indicators = ['mean_ghgs', 'mean_land', 'mean_watscar', 'mean_eut', 
              'mean_ghgs_ch4', 'mean_ghgs_n2o', 'mean_bio', 'mean_watuse', 'mean_acid']

# Calculate group means
grouped_adjusted = df_adjusted.groupby('diet_group')[indicators].mean()
grouped_noadjust = df_noadjust.groupby('diet_group')[indicators].mean()

# Normalize data by column max
def scale_by_max(df, max_scaled_value=1):
    df_scaled = df.copy()
    for col in df.columns:
        col_max = df[col].max()
        df_scaled[col] = (df[col] / col_max) * max_scaled_value
    return df_scaled

grouped_adjusted_scaled = scale_by_max(grouped_adjusted)
grouped_noadjust_scaled = scale_by_max(grouped_noadjust)

# Diet groups ordered by meat consumption
diet_groups = ['meat100', 'meat', 'meat50', 'fish', 'veggie', 'vegan']

# Color scheme
colors = ['#E41A1C', '#FF7F00', '#F781BF', '#4DAF4A', '#377EB8', '#984EA3']

# Radar chart parameters
n = len(indicators)
angles = [i / float(n) * 2 * pi for i in range(n)]
angles += angles[:1]  # Close the loop

# ==============================================
# 1. Static Comparison Figure
# ==============================================
plt.figure(figsize=(18, 10))

# Left plot: Real-world Impact
ax1 = plt.subplot(121, polar=True)
for i, diet in enumerate(diet_groups):
    values = grouped_noadjust_scaled.loc[diet].values.flatten().tolist()
    values += values[:1]
    ax1.plot(angles, values, linewidth=2, label=diet, color=colors[i])
    ax1.fill(angles, values, color=colors[i], alpha=0.2)

ax1.set_xticks(angles[:-1])
ax1.set_xticklabels(indicators, fontsize=10)
ax1.set_title("Real-world Impact (No kcal Adjustment)", fontsize=16, pad=20)
ax1.set_ylim(0, 1.1)

# Right plot: Efficiency
ax2 = plt.subplot(122, polar=True)
for i, diet in enumerate(diet_groups):
    values = grouped_adjusted_scaled.loc[diet].values.flatten().tolist()
    values += values[:1]
    ax2.plot(angles, values, linewidth=2, label=diet, color=colors[i])
    ax2.fill(angles, values, color=colors[i], alpha=0.2)

ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(indicators, fontsize=10)
ax2.set_title("Efficiency (kcal-Adjusted)", fontsize=16, pad=20)
ax2.set_ylim(0, 1.1)

# Add common legend
plt.legend(
    handles=[plt.Line2D([0], [0], color=colors[i], lw=4, label=diet) for i, diet in enumerate(diet_groups)],
    title="Diet Group", 
    loc='lower center', 
    bbox_to_anchor=(0.5, -0.15), 
    ncol=3, 
    fontsize=12, 
    title_fontsize=14
)

plt.suptitle("Comparison of Dietary Environmental Impacts", fontsize=18, y=1.05)
plt.tight_layout()
plt.savefig('diet_comparison_static.png', dpi=300, bbox_inches='tight')
plt.close()

# ==============================================
# 2. Animated Version
# ==============================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10), subplot_kw=dict(polar=True))

def update_highlight(i):
    # Clear previous artists
    for ax in [ax1, ax2]:
        for artist in ax.get_children():
            if isinstance(artist, Polygon):
                artist.remove()
    
    for j, diet in enumerate(diet_groups):
        # Left plot
        values = grouped_noadjust_scaled.loc[diet].values.flatten().tolist()
        values += values[:1]
        line1, = ax1.plot(angles, values, color=colors[j], label=diet)
        if j == i:
            ax1.fill(angles, values, color=colors[j], alpha=0.6)
            ax1.set_title(f"Real-world: {diet}", fontsize=16, pad=20)
        else:
            ax1.fill(angles, values, color=colors[j], alpha=0.1)
        
        # Right plot
        values = grouped_adjusted_scaled.loc[diet].values.flatten().tolist()
        values += values[:1]
        line2, = ax2.plot(angles, values, color=colors[j], label=diet)
        if j == i:
            ax2.fill(angles, values, color=colors[j], alpha=0.6)
            ax2.set_title(f"Efficiency: {diet}", fontsize=16, pad=20)
        else:
            ax2.fill(angles, values, color=colors[j], alpha=0.1)
    
    # Add legend only once
    if i == 0:
        fig.legend(
            handles=[plt.Line2D([0], [0], color=colors[j], lw=4, label=diet) for j, diet in enumerate(diet_groups)],
            title="Diet Group", 
            loc='lower center', 
            bbox_to_anchor=(0.5, -0.15), 
            ncol=3, 
            fontsize=12, 
            title_fontsize=14
        )
    
    return [ax1, ax2]

# Initialize axes
for ax in [ax1, ax2]:
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(indicators, fontsize=10)
    ax.set_ylim(0, 1.1)

plt.suptitle("Dietary Impact Comparison (Animated)", fontsize=18, y=1.05)
plt.tight_layout()

# Create and save animation
ani = animation.FuncAnimation(
    fig, 
    update_highlight, 
    frames=len(diet_groups), 
    interval=2000,  # 2 seconds per frame
    blit=False
)
ani.save("diet_comparison_animated.mp4", writer="ffmpeg", dpi=150, fps=0.5)
plt.close()