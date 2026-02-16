import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

df = pd.read_csv("datas/delivery_data_enriched.csv")

le_weather = LabelEncoder()
le_food = LabelEncoder()
le_area = LabelEncoder()
le_day = LabelEncoder()

df["Weather_enc"] = le_weather.fit_transform(df["Weather"])
df["FoodType_enc"] = le_food.fit_transform(df["FoodType"])
df["CustomerArea_enc"] = le_area.fit_transform(df["CustomerArea"])
df["DayType_enc"] = le_day.fit_transform(df["DayType"])

features = [
    "DistanceKM", "PartnerRating", "OrderHour", "PeakHour",
    "OrderValue", "Weather_enc", "FoodType_enc",
    "CustomerArea_enc", "DayType_enc"
]
target = "ActualDeliveryTime"

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
}

results = {}

print("=" * 60)
print("MODEL TRAINING AND EVALUATION")
print("=" * 60)

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    results[name] = {"MAE": mae, "RMSE": rmse, "R2": r2, "predictions": y_pred}

    print(f"\n{name}:")
    print(f"  MAE:  {mae:.2f} minutes")
    print(f"  RMSE: {rmse:.2f} minutes")
    print(f"  R2:   {r2:.4f}")

best_model_name = max(results, key=lambda k: results[k]["R2"])
best_model = models[best_model_name]
print(f"\nBest Model: {best_model_name} (R2 = {results[best_model_name]['R2']:.4f})")


# Feature Importance
if hasattr(best_model, "feature_importances_"):
    importance = pd.DataFrame({
        "Feature": features,
        "Importance": best_model.feature_importances_
    }).sort_values("Importance", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(importance["Feature"], importance["Importance"], color="#3498db", edgecolor="black", linewidth=0.5)
    ax.set_title(f"Feature Importance ({best_model_name})", fontsize=15, fontweight="bold")
    ax.set_xlabel("Importance", fontsize=13)
    plt.tight_layout()
    plt.savefig("output/charts/09_feature_importance.png", bbox_inches="tight")
    plt.close()
    print("\nFeature Importance chart saved")


# Actual vs Predicted scatter
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for i, (name, res) in enumerate(results.items()):
    axes[i].scatter(y_test, res["predictions"], alpha=0.3, s=15, color="#3498db")
    axes[i].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
                 "r--", linewidth=2, label="Perfect Prediction")
    axes[i].set_title(f"{name}\nR2={res['R2']:.3f}, MAE={res['MAE']:.1f}", fontsize=12, fontweight="bold")
    axes[i].set_xlabel("Actual Time (min)")
    axes[i].set_ylabel("Predicted Time (min)")
    axes[i].legend()

plt.suptitle("Model Comparison: Actual vs Predicted Delivery Time", fontsize=15, fontweight="bold")
plt.tight_layout()
plt.savefig("output/charts/10_model_comparison.png", bbox_inches="tight")
plt.close()
print("Model Comparison chart saved")


# Prediction examples
print("\n" + "=" * 60)
print("SAMPLE PREDICTIONS")
print("=" * 60)

scenarios = pd.DataFrame({
    "DistanceKM": [2.0, 5.0, 8.0, 3.0, 6.0],
    "PartnerRating": [4.5, 3.5, 2.5, 4.0, 3.0],
    "OrderHour": [12, 19, 20, 10, 15],
    "PeakHour": [1, 1, 1, 0, 0],
    "OrderValue": [350, 280, 200, 400, 150],
    "Weather_enc": [le_weather.transform(["Sunny"])[0],
                    le_weather.transform(["Rainy"])[0],
                    le_weather.transform(["Stormy"])[0],
                    le_weather.transform(["Cloudy"])[0],
                    le_weather.transform(["Sunny"])[0]],
    "FoodType_enc": [le_food.transform(["Pizza"])[0],
                     le_food.transform(["Indian"])[0],
                     le_food.transform(["Chinese"])[0],
                     le_food.transform(["Fast Food"])[0],
                     le_food.transform(["Desserts"])[0]],
    "CustomerArea_enc": [le_area.transform(["Downtown"])[0],
                         le_area.transform(["Suburbs"])[0],
                         le_area.transform(["Business District"])[0],
                         le_area.transform(["Downtown"])[0],
                         le_area.transform(["Suburbs"])[0]],
    "DayType_enc": [le_day.transform(["Weekday"])[0],
                    le_day.transform(["Weekend"])[0],
                    le_day.transform(["Weekday"])[0],
                    le_day.transform(["Weekend"])[0],
                    le_day.transform(["Weekday"])[0]],
})

scenario_labels = [
    "Short distance, good partner, sunny, peak",
    "Medium distance, avg partner, rainy, peak",
    "Long distance, low partner, stormy, peak",
    "Short distance, good partner, cloudy, off-peak",
    "Medium distance, avg partner, sunny, off-peak",
]

predictions = best_model.predict(scenarios)
for label, pred in zip(scenario_labels, predictions):
    print(f"  {label}")
    print(f"    -> Predicted delivery time: {pred:.1f} minutes\n")


# Peak hour staffing prediction
print("=" * 60)
print("STAFFING RECOMMENDATIONS")
print("=" * 60)
hourly_load = df.groupby("OrderHour").agg(
    orders=("OrderID", "count"),
    avg_time=("ActualDeliveryTime", "mean"),
).round(1)

hourly_load["partners_needed"] = np.ceil(hourly_load["orders"] / 3).astype(int)

for hour, row in hourly_load.iterrows():
    status = "PEAK" if hour in [11, 12, 13, 18, 19, 20, 21] else "    "
    print(f"  {status} Hour {hour:02d}:00 -> {int(row['orders']):3d} orders, "
          f"avg {row['avg_time']:.1f} min, need ~{row['partners_needed']} partners")