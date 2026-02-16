import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

df = pd.read_csv("datas/delivery_data_enriched.csv")

total_revenue = df["OrderValue"].sum()
total_loss = df["RevenueLossContribution"].sum()
avg_delivery = df["ActualDeliveryTime"].mean()
delay_rate = df["IsDelayed"].mean() * 100
avg_satisfaction = df["CustomerSatisfactionIndex"].mean()
total_orders = len(df)

best_partner = df.groupby("PartnerID").agg(
    avg_rating=("PartnerRating", "mean"),
    avg_time=("ActualDeliveryTime", "mean"),
    orders=("OrderID", "count")
).sort_values("avg_rating", ascending=False).head(1)

bp_id = best_partner.index[0]
bp_rating = best_partner["avg_rating"].values[0]


# Main Dashboard
fig = make_subplots(
    rows=4, cols=3,
    subplot_titles=(
        "Revenue at Risk", "Avg Delivery Time", "Top Partner",
        "Delay Rate", "Avg Satisfaction", "Total Orders",
        "Delivery Time by Weather", "Partner Rating Distribution", "Hourly Order Volume",
        "Food Type Revenue", "Area Performance", "Efficiency Score Distribution"
    ),
    specs=[
        [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
        [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
        [{"type": "bar"}, {"type": "histogram"}, {"type": "scatter"}],
        [{"type": "pie"}, {"type": "bar"}, {"type": "histogram"}],
    ],
    vertical_spacing=0.08,
    horizontal_spacing=0.08,
)

fig.add_trace(go.Indicator(
    mode="number+delta",
    value=total_loss,
    number={"prefix": "Rs.", "font": {"size": 28}},
    delta={"reference": total_loss * 0.8, "increasing": {"color": "red"}},
    title={"text": "Monthly Revenue at Risk", "font": {"size": 13}},
), row=1, col=1)

fig.add_trace(go.Indicator(
    mode="gauge+number",
    value=avg_delivery,
    number={"suffix": " min", "font": {"size": 28}},
    gauge={
        "axis": {"range": [0, 60]},
        "bar": {"color": "#e74c3c" if avg_delivery > 35 else "#2ecc71"},
        "steps": [
            {"range": [0, 25], "color": "#d5f5e3"},
            {"range": [25, 35], "color": "#fdebd0"},
            {"range": [35, 60], "color": "#fadbd8"},
        ],
        "threshold": {"line": {"color": "red", "width": 3}, "thickness": 0.8, "value": 40},
    },
    title={"text": "Avg Delivery Time", "font": {"size": 13}},
), row=1, col=2)

fig.add_trace(go.Indicator(
    mode="number",
    value=bp_rating,
    number={"suffix": "/5.0", "font": {"size": 28, "color": "#2ecc71"}},
    title={"text": f"Top Partner: {bp_id}", "font": {"size": 13}},
), row=1, col=3)

fig.add_trace(go.Indicator(
    mode="number+delta",
    value=delay_rate,
    number={"suffix": "%", "font": {"size": 28}},
    delta={"reference": 20, "decreasing": {"color": "green"}, "increasing": {"color": "red"}},
    title={"text": "Delay Rate (>40min)", "font": {"size": 13}},
), row=2, col=1)

fig.add_trace(go.Indicator(
    mode="number",
    value=avg_satisfaction,
    number={"suffix": "/100", "font": {"size": 28, "color": "#3498db"}},
    title={"text": "Avg Satisfaction Index", "font": {"size": 13}},
), row=2, col=2)

fig.add_trace(go.Indicator(
    mode="number",
    value=total_orders,
    number={"font": {"size": 28, "color": "#8e44ad"}},
    title={"text": "Total Orders Analyzed", "font": {"size": 13}},
), row=2, col=3)

weather_avg = df.groupby("Weather")["ActualDeliveryTime"].mean().round(1)
w_order = ["Sunny", "Cloudy", "Rainy", "Stormy"]
w_colors = ["#2ecc71", "#95a5a6", "#3498db", "#e74c3c"]
fig.add_trace(go.Bar(
    x=[w for w in w_order if w in weather_avg.index],
    y=[weather_avg[w] for w in w_order if w in weather_avg.index],
    marker_color=w_colors[:len(weather_avg)],
    text=[f"{weather_avg[w]:.1f}" for w in w_order if w in weather_avg.index],
    textposition="auto",
    showlegend=False,
), row=3, col=1)

fig.add_trace(go.Histogram(
    x=df["PartnerRating"],
    nbinsx=20,
    marker_color="#3498db",
    showlegend=False,
), row=3, col=2)

hourly = df.groupby("OrderHour").agg(
    count=("OrderID", "count"),
    avg_time=("ActualDeliveryTime", "mean")
).round(1)
fig.add_trace(go.Scatter(
    x=hourly.index, y=hourly["count"],
    mode="lines+markers",
    marker=dict(size=8, color="#e67e22"),
    line=dict(width=2),
    showlegend=False,
), row=3, col=3)

food_rev = df.groupby("FoodType")["OrderValue"].sum().round(0)
fig.add_trace(go.Pie(
    labels=food_rev.index,
    values=food_rev.values,
    hole=0.4,
    marker=dict(colors=["#e74c3c", "#f39c12", "#2ecc71", "#3498db", "#9b59b6"]),
    textinfo="label+percent",
    showlegend=False,
), row=4, col=1)

area_data = df.groupby("CustomerArea")["ActualDeliveryTime"].mean().round(1)
fig.add_trace(go.Bar(
    x=area_data.index,
    y=area_data.values,
    marker_color=["#e74c3c", "#f39c12", "#2ecc71"],
    text=[f"{v:.1f}" for v in area_data.values],
    textposition="auto",
    showlegend=False,
), row=4, col=2)

fig.add_trace(go.Histogram(
    x=df["EfficiencyScore"],
    nbinsx=30,
    marker_color="#9b59b6",
    showlegend=False,
), row=4, col=3)

fig.update_layout(
    height=1400,
    width=1200,
    title_text="Smart Food Delivery Analytics - Executive Command Center",
    title_font_size=22,
    title_x=0.5,
    paper_bgcolor="#f8f9fa",
    plot_bgcolor="white",
    font=dict(family="Arial"),
)

fig.write_html("output/reports/executive_dashboard.html")
print("Executive Dashboard saved to output/reports/executive_dashboard.html")


# Alert Report
alerts = []

slow_routes = df[df["ActualDeliveryTime"] > 30]
alerts.append(f"ALERT: {len(slow_routes)} orders exceeded 30-minute delivery time")

low_partners = df.groupby("PartnerID")["PartnerRating"].mean()
bad_partners = low_partners[low_partners < 3.0]
alerts.append(f"ALERT: {len(bad_partners)} partners have average rating below 3.0")

stormy_orders = df[df["Weather"] == "Stormy"]
alerts.append(f"ALERT: {len(stormy_orders)} orders affected by stormy weather (avg time: {stormy_orders['ActualDeliveryTime'].mean():.1f} min)")

print("\n" + "=" * 50)
print("SYSTEM ALERTS")
print("=" * 50)
for a in alerts:
    print(f"  >> {a}")