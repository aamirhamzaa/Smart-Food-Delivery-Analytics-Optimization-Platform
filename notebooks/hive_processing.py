import pandas as pd

df = pd.read_csv("data/delivery_data.csv")


def rating_tier(r):
    if r >= 4.0:
        return "High"
    elif r >= 3.0:
        return "Medium"
    return "Low"


df["RatingTier"] = df["PartnerRating"].apply(rating_tier)

print("=" * 60)
print("QUERY 1: Avg Delivery Time by Weather and Rating Tier")
print("=" * 60)
q1 = df.groupby(["Weather", "RatingTier"]).agg(
    AvgDeliveryTime=("ActualDeliveryTime", "mean"),
    OrderCount=("OrderID", "count")
).round(2)
print(q1)
q1.to_csv("output/reports/q1_weather_rating.csv")


print("\n" + "=" * 60)
print("QUERY 2: Revenue at Risk from Delayed Orders")
print("=" * 60)
df["IsDelayed"] = df["ActualDeliveryTime"] > 40
q2 = df.groupby("CustomerArea").agg(
    DelayedOrders=("IsDelayed", "sum"),
    TotalOrders=("OrderID", "count"),
    RevenueAtRisk=("OrderValue", lambda x: x[df.loc[x.index, "IsDelayed"]].sum()),
).round(2)
q2["EstimatedChurnLoss"] = (q2["RevenueAtRisk"] * 0.15).round(2)
print(q2)
q2.to_csv("output/reports/q2_revenue_at_risk.csv")


print("\n" + "=" * 60)
print("QUERY 3: Partner Performance Tiers")
print("=" * 60)
q3 = df.groupby("PartnerID").agg(
    TotalDeliveries=("OrderID", "count"),
    AvgTime=("ActualDeliveryTime", "mean"),
    AvgRating=("PartnerRating", "mean"),
).round(2)


def perf_tier(row):
    if row["AvgRating"] >= 4.0 and row["AvgTime"] < 35:
        return "Premium"
    elif row["AvgRating"] >= 3.0 and row["AvgTime"] < 45:
        return "Standard"
    return "Training"


q3["PerformanceTier"] = q3.apply(perf_tier, axis=1)
q3 = q3.sort_values("AvgRating", ascending=False)
print(q3)
q3.to_csv("output/reports/q3_partner_tiers.csv")


print("\n" + "=" * 60)
print("QUERY 4: Peak vs Off-Peak Efficiency")
print("=" * 60)
q4 = df.groupby("PeakHour").agg(
    AvgDeliveryTime=("ActualDeliveryTime", "mean"),
    AvgOrderValue=("OrderValue", "mean"),
    OrderCount=("OrderID", "count"),
    TotalRevenue=("OrderValue", "sum"),
).round(2)
print(q4)
q4.to_csv("output/reports/q4_peak_analysis.csv")


print("\n" + "=" * 60)
print("QUERY 5: Food Type Analysis")
print("=" * 60)
q5 = df.groupby("FoodType").agg(
    AvgDeliveryTime=("ActualDeliveryTime", "mean"),
    MinTime=("ActualDeliveryTime", "min"),
    MaxTime=("ActualDeliveryTime", "max"),
    AvgOrderValue=("OrderValue", "mean"),
    OrderCount=("OrderID", "count"),
).round(2).sort_values("AvgDeliveryTime", ascending=False)
print(q5)
q5.to_csv("output/reports/q5_food_type.csv")


print("\n" + "=" * 60)
print("QUERY 6: Distance vs Delivery Time by Area")
print("=" * 60)


def dist_bucket(d):
    if d < 3:
        return "Short"
    elif d < 6:
        return "Medium"
    return "Long"


df["DistanceBucket"] = df["DistanceKM"].apply(dist_bucket)
q6 = df.groupby(["CustomerArea", "DistanceBucket"]).agg(
    AvgTime=("ActualDeliveryTime", "mean"),
    AvgDistance=("DistanceKM", "mean"),
    OrderCount=("OrderID", "count"),
).round(2)
print(q6)
q6.to_csv("output/reports/q6_distance_analysis.csv")

print("\nAll query results saved to output/reports/")