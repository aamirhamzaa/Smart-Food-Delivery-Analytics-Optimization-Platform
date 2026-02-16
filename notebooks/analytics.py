import pandas as pd
import numpy as np
from pyhive import hive

# --- Connect to HiveServer2 ---
conn = hive.Connection(
    host="localhost",      # or your hive-server container name if inside docker
    port=10000,
    username="hive",
    database="default"     # change to your actual database name
)

# --- Read from Hive table instead of CSV ---
query = "SELECT * FROM delivery_data"
df = pd.read_sql(query, conn)

# Normalize column names: strip table prefix and capitalize properly
df.columns = [col.split(".")[-1] for col in df.columns]  # remove "tablename." prefix if present
df.columns = [
    "OrderID", "RestaurantLat", "RestaurantLon", "RestaurantName",
    "FoodType", "DeliveryLat", "DeliveryLon", "CustomerArea",
    "Weather", "PartnerID", "PartnerRating", "OrderHour", "DayType",
    "OrderValue", "ActualDeliveryTime", "DistanceKM", "PeakHour"
]
print(df.columns.tolist())  # <-- add this temporarily to see exact names
conn.close()

# --- Analytics (same logic as before) ---
weather_factor_map = {"Sunny": 1.0, "Cloudy": 0.9, "Rainy": 0.7, "Stormy": 0.5}
df["WeatherFactor"] = df["Weather"].map(weather_factor_map)

df["EfficiencyScore"] = (
    (5 - df["ActualDeliveryTime"] / 10)
    * df["PartnerRating"]
    * df["WeatherFactor"]
)
df["EfficiencyScore"] = df["EfficiencyScore"].round(2)

CHURN_RATE = 0.15
DELAY_THRESHOLD = 40
df["IsDelayed"] = df["ActualDeliveryTime"] > DELAY_THRESHOLD
df["RevenueLossContribution"] = df["IsDelayed"].astype(int) * df["OrderValue"] * CHURN_RATE

total_revenue_loss = df["RevenueLossContribution"].sum()
monthly_projection = total_revenue_loss * 30

partner_hours = df.groupby("PartnerID").agg(
    total_orders=("OrderID", "count"),
    unique_hours=("OrderHour", "nunique"),
    avg_rating=("PartnerRating", "mean"),
    avg_time=("ActualDeliveryTime", "mean"),
).round(2)
partner_hours["utilization"] = (partner_hours["total_orders"] / partner_hours["unique_hours"]).round(2)

df["TimeEfficiency"] = 1 - (df["ActualDeliveryTime"] / df["ActualDeliveryTime"].max())
df["DistanceEfficiency"] = 1 - (df["DistanceKM"] / df["DistanceKM"].max())
df["RouteOptimizationScore"] = ((df["DistanceEfficiency"] + df["TimeEfficiency"]) / 2 * 100).round(2)

max_time = df["ActualDeliveryTime"].max()
df["CustomerSatisfactionIndex"] = (
    (1 - df["ActualDeliveryTime"] / max_time) * 0.6
    + (df["PartnerRating"] / 5.0) * 0.4
).round(3) * 100

# --- Print Reports ---
print("=" * 60)
print("BUSINESS INTELLIGENCE SUMMARY (from Hive)")
print("=" * 60)

print(f"\nTotal Orders Analyzed: {len(df)}")
print(f"Delayed Orders (>{DELAY_THRESHOLD} min): {df['IsDelayed'].sum()} ({df['IsDelayed'].mean()*100:.1f}%)")
print(f"Total Revenue in Dataset: Rs.{df['OrderValue'].sum():,.0f}")
print(f"Revenue at Risk (from delays): Rs.{total_revenue_loss:,.0f}")
print(f"Projected Monthly Loss: Rs.{monthly_projection:,.0f}")
print(f"Average Efficiency Score: {df['EfficiencyScore'].mean():.2f}")
print(f"Average Customer Satisfaction: {df['CustomerSatisfactionIndex'].mean():.1f}/100")
print(f"Average Route Optimization: {df['RouteOptimizationScore'].mean():.1f}/100")

print("\n" + "=" * 60)
print("TOP 10 PARTNERS BY UTILIZATION")
print("=" * 60)
print(partner_hours.sort_values("utilization", ascending=False).head(10))

print("\n" + "=" * 60)
print("WEATHER IMPACT ANALYSIS")
print("=" * 60)
weather_impact = df.groupby("Weather").agg(
    avg_delivery_time=("ActualDeliveryTime", "mean"),
    avg_efficiency=("EfficiencyScore", "mean"),
    delay_rate=("IsDelayed", "mean"),
    revenue_loss=("RevenueLossContribution", "sum"),
    order_count=("OrderID", "count"),
).round(2)
weather_impact["delay_rate"] = (weather_impact["delay_rate"] * 100).round(1)
print(weather_impact)

print("\n" + "=" * 60)
print("AREA-WISE PERFORMANCE")
print("=" * 60)
area_perf = df.groupby("CustomerArea").agg(
    avg_delivery_time=("ActualDeliveryTime", "mean"),
    avg_satisfaction=("CustomerSatisfactionIndex", "mean"),
    avg_order_value=("OrderValue", "mean"),
    delay_rate=("IsDelayed", "mean"),
    total_revenue=("OrderValue", "sum"),
).round(2)
area_perf["delay_rate"] = (area_perf["delay_rate"] * 100).round(1)
print(area_perf)

# --- Save outputs ---
df.to_csv("datas/delivery_data_enriched.csv", index=False)
partner_hours.to_csv("output/reports/partner_utilization.csv")
weather_impact.to_csv("output/reports/weather_impact.csv")
area_perf.to_csv("output/reports/area_performance.csv")

print("\nEnriched dataset saved to datas/delivery_data_enriched.csv")