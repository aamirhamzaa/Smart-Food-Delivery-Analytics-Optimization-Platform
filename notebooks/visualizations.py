import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 150
plt.rcParams["figure.figsize"] = (12, 7)
plt.rcParams["font.size"] = 11

df = pd.read_csv("datas/delivery_data_enriched.csv")


# Chart 1: Weather Impact Bar Chart with Revenue Loss
fig, ax1 = plt.subplots(figsize=(12, 7))

weather_data = df.groupby("Weather").agg(
    avg_time=("ActualDeliveryTime", "mean"),
    revenue_loss=("RevenueLossContribution", "sum"),
).round(2)
weather_order = ["Sunny", "Cloudy", "Rainy", "Stormy"]
weather_data = weather_data.reindex(weather_order)

colors = ["#2ecc71", "#95a5a6", "#3498db", "#e74c3c"]
bars = ax1.bar(weather_data.index, weather_data["avg_time"], color=colors, width=0.5, edgecolor="black", linewidth=0.5)

for bar, val in zip(bars, weather_data["avg_time"]):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{val:.1f} min", ha="center", va="bottom", fontweight="bold")

ax2 = ax1.twinx()
ax2.plot(weather_data.index, weather_data["revenue_loss"], color="#e67e22",
         marker="D", linewidth=2.5, markersize=10, label="Revenue Loss (Rs.)")
for i, v in enumerate(weather_data["revenue_loss"]):
    ax2.annotate(f"Rs.{v:,.0f}", (i, v), textcoords="offset points",
                 xytext=(0, 12), ha="center", fontsize=9, color="#e67e22")

ax1.set_xlabel("Weather Condition", fontsize=13)
ax1.set_ylabel("Average Delivery Time (min)", fontsize=13)
ax2.set_ylabel("Revenue Loss (Rs.)", fontsize=13, color="#e67e22")
ax1.set_title("Weather Impact on Delivery Time and Revenue Loss", fontsize=15, fontweight="bold", pad=20)
fig.legend(loc="upper left", bbox_to_anchor=(0.12, 0.95))
plt.tight_layout()
plt.savefig("output/charts/01_weather_impact.png", bbox_inches="tight")
plt.close()
print("Chart 1 saved: Weather Impact")


# Chart 2: Partner Efficiency Scatter Plot
fig, ax = plt.subplots(figsize=(12, 8))

partner_data = df.groupby("PartnerID").agg(
    avg_rating=("PartnerRating", "mean"),
    avg_time=("ActualDeliveryTime", "mean"),
    total_orders=("OrderID", "count"),
).round(2)

def get_tier(row):
    if row["avg_rating"] >= 4.0 and row["avg_time"] < 35:
        return "Premium"
    elif row["avg_rating"] >= 3.0 and row["avg_time"] < 45:
        return "Standard"
    return "Training"

partner_data["tier"] = partner_data.apply(get_tier, axis=1)
tier_colors = {"Premium": "#2ecc71", "Standard": "#f39c12", "Training": "#e74c3c"}

for tier, color in tier_colors.items():
    subset = partner_data[partner_data["tier"] == tier]
    ax.scatter(subset["avg_rating"], subset["avg_time"],
               s=subset["total_orders"] * 8, c=color, alpha=0.7,
               edgecolors="black", linewidth=0.5, label=f"{tier} ({len(subset)})")

ax.axhline(y=35, color="green", linestyle="--", alpha=0.5, linewidth=1)
ax.axhline(y=45, color="red", linestyle="--", alpha=0.5, linewidth=1)
ax.axvline(x=4.0, color="green", linestyle="--", alpha=0.5, linewidth=1)
ax.axvline(x=3.0, color="red", linestyle="--", alpha=0.5, linewidth=1)

ax.set_xlabel("Average Partner Rating", fontsize=13)
ax.set_ylabel("Average Delivery Time (min)", fontsize=13)
ax.set_title("Partner Efficiency: Rating vs Delivery Time\n(Bubble size = Total Orders)",
             fontsize=15, fontweight="bold")
ax.legend(title="Performance Tier", fontsize=11)
plt.tight_layout()
plt.savefig("output/charts/02_partner_efficiency.png", bbox_inches="tight")
plt.close()
print("Chart 2 saved: Partner Efficiency")


# Chart 3: Delivery Time Heatmap (Hour vs Day)
fig, ax = plt.subplots(figsize=(14, 6))

heatmap_data = df.pivot_table(
    values="ActualDeliveryTime",
    index="DayType",
    columns="OrderHour",
    aggfunc="mean"
).round(1)

sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="RdYlGn_r",
            linewidths=0.5, ax=ax, cbar_kws={"label": "Avg Delivery Time (min)"})
ax.set_title("Delivery Time Heatmap: Hour of Day vs Day Type",
             fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Hour of Day", fontsize=13)
ax.set_ylabel("Day Type", fontsize=13)
plt.tight_layout()
plt.savefig("output/charts/03_time_heatmap.png", bbox_inches="tight")
plt.close()
print("Chart 3 saved: Time Heatmap")


# Chart 4: Food Type Box Plots
fig, ax = plt.subplots(figsize=(12, 7))

food_order = df.groupby("FoodType")["ActualDeliveryTime"].median().sort_values(ascending=False).index

food_colors = {"Indian": "#ff9933", "Pizza": "#e74c3c", "Chinese": "#e67e22",
               "Fast Food": "#f1c40f", "Desserts": "#2ecc71"}
palette = [food_colors.get(f, "#95a5a6") for f in food_order]

sns.boxplot(data=df, x="FoodType", y="ActualDeliveryTime", order=food_order,
            palette=palette, ax=ax, linewidth=1.2)

medians = df.groupby("FoodType")["ActualDeliveryTime"].median()
for i, food in enumerate(food_order):
    ax.text(i, medians[food] - 2, f"{medians[food]:.0f}",
            ha="center", fontweight="bold", fontsize=10, color="white",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.7))

ax.set_title("Delivery Time Distribution by Food Type", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Food Type", fontsize=13)
ax.set_ylabel("Delivery Time (min)", fontsize=13)
ax.axhline(y=40, color="red", linestyle="--", alpha=0.5, label="Delay Threshold (40 min)")
ax.legend()
plt.tight_layout()
plt.savefig("output/charts/04_food_type_boxplot.png", bbox_inches="tight")
plt.close()
print("Chart 4 saved: Food Type Box Plots")


# Chart 5: Peak Hour Comparison
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

peak_labels = ["Off-Peak", "Peak"]
metrics = ["ActualDeliveryTime", "OrderValue", "EfficiencyScore"]
titles = ["Avg Delivery Time (min)", "Avg Order Value (Rs.)", "Avg Efficiency Score"]
colors_list = [["#2ecc71", "#e74c3c"], ["#3498db", "#e67e22"], ["#9b59b6", "#1abc9c"]]

for i, (metric, title, cols) in enumerate(zip(metrics, titles, colors_list)):
    peak_data = df.groupby("PeakHour")[metric].mean()
    bars = axes[i].bar(peak_labels, peak_data.values, color=cols, edgecolor="black", linewidth=0.5, width=0.5)
    for bar, val in zip(bars, peak_data.values):
        axes[i].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f"{val:.1f}", ha="center", va="bottom", fontweight="bold", fontsize=12)
    axes[i].set_title(title, fontsize=13, fontweight="bold")
    axes[i].set_ylabel(title, fontsize=11)

fig.suptitle("Peak Hour vs Off-Peak Performance Comparison", fontsize=16, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("output/charts/05_peak_comparison.png", bbox_inches="tight")
plt.close()
print("Chart 5 saved: Peak Hour Comparison")


# Chart 6: Distance vs Delivery Time with regression
fig, ax = plt.subplots(figsize=(12, 7))

sns.regplot(data=df, x="DistanceKM", y="ActualDeliveryTime",
            scatter_kws={"alpha": 0.3, "s": 20, "color": "#3498db"},
            line_kws={"color": "#e74c3c", "linewidth": 2},
            ax=ax)

correlation = df["DistanceKM"].corr(df["ActualDeliveryTime"])
ax.text(0.05, 0.95, f"Correlation: {correlation:.3f}",
        transform=ax.transAxes, fontsize=13, fontweight="bold",
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

ax.set_title("Distance vs Delivery Time Correlation", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Distance (KM)", fontsize=13)
ax.set_ylabel("Delivery Time (min)", fontsize=13)
ax.axhline(y=40, color="red", linestyle="--", alpha=0.4, label="Delay Threshold")
ax.legend()
plt.tight_layout()
plt.savefig("output/charts/06_distance_correlation.png", bbox_inches="tight")
plt.close()
print("Chart 6 saved: Distance Correlation")


# Chart 7: Customer Area Performance Radar-style grouped bar
fig, ax = plt.subplots(figsize=(12, 7))

area_stats = df.groupby("CustomerArea").agg(
    avg_time=("ActualDeliveryTime", "mean"),
    avg_satisfaction=("CustomerSatisfactionIndex", "mean"),
    delay_pct=("IsDelayed", "mean"),
    avg_efficiency=("EfficiencyScore", "mean"),
).round(2)

x = np.arange(len(area_stats.index))
width = 0.2

bars1 = ax.bar(x - 1.5*width, area_stats["avg_time"], width, label="Avg Time (min)", color="#e74c3c")
bars2 = ax.bar(x - 0.5*width, area_stats["avg_satisfaction"], width, label="Satisfaction Index", color="#2ecc71")
bars3 = ax.bar(x + 0.5*width, area_stats["delay_pct"]*100, width, label="Delay %", color="#f39c12")
bars4 = ax.bar(x + 1.5*width, area_stats["avg_efficiency"], width, label="Efficiency Score", color="#3498db")

ax.set_xticks(x)
ax.set_xticklabels(area_stats.index, fontsize=12)
ax.set_title("Customer Area Performance Comparison", fontsize=15, fontweight="bold", pad=15)
ax.legend(fontsize=10)
ax.set_ylabel("Value", fontsize=13)
plt.tight_layout()
plt.savefig("output/charts/07_area_comparison.png", bbox_inches="tight")
plt.close()
print("Chart 7 saved: Area Comparison")


# Chart 8: Hourly order volume and delivery time
fig, ax1 = plt.subplots(figsize=(14, 7))

hourly = df.groupby("OrderHour").agg(
    order_count=("OrderID", "count"),
    avg_time=("ActualDeliveryTime", "mean"),
).round(2)

color1 = "#3498db"
ax1.bar(hourly.index, hourly["order_count"], color=color1, alpha=0.7, label="Order Count")
ax1.set_xlabel("Hour of Day", fontsize=13)
ax1.set_ylabel("Number of Orders", fontsize=13, color=color1)
ax1.tick_params(axis="y", labelcolor=color1)

ax2 = ax1.twinx()
color2 = "#e74c3c"
ax2.plot(hourly.index, hourly["avg_time"], color=color2, marker="o", linewidth=2.5, label="Avg Delivery Time")
ax2.set_ylabel("Avg Delivery Time (min)", fontsize=13, color=color2)
ax2.tick_params(axis="y", labelcolor=color2)

peak_hours = [11, 12, 13, 18, 19, 20, 21]
for ph in peak_hours:
    ax1.axvspan(ph - 0.4, ph + 0.4, alpha=0.1, color="red")

fig.suptitle("Hourly Order Volume and Average Delivery Time", fontsize=15, fontweight="bold")
fig.legend(loc="upper left", bbox_to_anchor=(0.12, 0.92))
plt.tight_layout()
plt.savefig("output/charts/08_hourly_analysis.png", bbox_inches="tight")
plt.close()
print("Chart 8 saved: Hourly Analysis")

print("\nAll charts saved to output/charts/")