import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)

n_orders = 1200

restaurant_profiles = {
    "Pizza Palace": {"lat": 12.9716, "lon": 77.5946, "food": "Pizza"},
    "Dragon Wok": {"lat": 12.9352, "lon": 77.6245, "food": "Chinese"},
    "Spice Garden": {"lat": 12.9611, "lon": 77.6387, "food": "Indian"},
    "Burger Barn": {"lat": 12.9250, "lon": 77.5800, "food": "Fast Food"},
    "Sweet Tooth": {"lat": 12.9450, "lon": 77.5700, "food": "Desserts"},
    "Curry House": {"lat": 12.9800, "lon": 77.6100, "food": "Indian"},
    "Noodle Box": {"lat": 12.9550, "lon": 77.6050, "food": "Chinese"},
    "Flame Grill": {"lat": 12.9680, "lon": 77.5850, "food": "Fast Food"},
    "Roma Kitchen": {"lat": 12.9400, "lon": 77.6200, "food": "Pizza"},
    "Ice Cream Hub": {"lat": 12.9300, "lon": 77.5950, "food": "Desserts"},
    "Tandoori Nights": {"lat": 12.9750, "lon": 77.6300, "food": "Indian"},
    "Wonton Express": {"lat": 12.9500, "lon": 77.5750, "food": "Chinese"},
    "Cheese Burst": {"lat": 12.9650, "lon": 77.6150, "food": "Pizza"},
    "Quick Bites": {"lat": 12.9350, "lon": 77.6000, "food": "Fast Food"},
    "Cake Walk": {"lat": 12.9850, "lon": 77.5900, "food": "Desserts"},
}

area_coords = {
    "Downtown": {"lat_range": (12.960, 12.985), "lon_range": (77.580, 77.610)},
    "Suburbs": {"lat_range": (12.920, 12.945), "lon_range": (77.560, 77.590)},
    "Business District": {"lat_range": (12.945, 12.970), "lon_range": (77.610, 77.645)},
}

weather_options = ["Sunny", "Rainy", "Cloudy", "Stormy"]
weather_weights = [0.40, 0.25, 0.25, 0.10]

day_types = ["Weekday", "Weekend"]
day_weights = [0.71, 0.29]

partner_ids = [f"P{str(i).zfill(3)}" for i in range(1, 51)]
partner_base_ratings = {pid: round(np.random.uniform(2.5, 5.0), 1) for pid in partner_ids}

orders = []

for i in range(1, n_orders + 1):
    rest_name = random.choice(list(restaurant_profiles.keys()))
    rest_info = restaurant_profiles[rest_name]

    rest_lat = rest_info["lat"] + np.random.normal(0, 0.002)
    rest_lon = rest_info["lon"] + np.random.normal(0, 0.002)
    food_type = rest_info["food"]

    area = random.choices(list(area_coords.keys()), weights=[0.4, 0.35, 0.25])[0]
    area_info = area_coords[area]
    del_lat = np.random.uniform(*area_info["lat_range"])
    del_lon = np.random.uniform(*area_info["lon_range"])

    weather = random.choices(weather_options, weights=weather_weights)[0]
    day_type = random.choices(day_types, weights=day_weights)[0]

    hour = random.choices(
        list(range(8, 23)),
        weights=[2, 3, 5, 8, 10, 5, 3, 3, 6, 9, 10, 8, 5, 3, 2]
    )[0]

    is_peak = 1 if hour in [11, 12, 13, 18, 19, 20, 21] else 0

    pid = random.choice(partner_ids)
    p_rating = partner_base_ratings[pid] + np.random.normal(0, 0.2)
    p_rating = round(max(1.0, min(5.0, p_rating)), 1)

    distance = np.sqrt((rest_lat - del_lat)**2 + (rest_lon - del_lon)**2) * 111
    distance = round(max(0.5, distance + np.random.normal(0, 0.5)), 2)

    base_time = 10 + distance * 4
    weather_penalty = {"Sunny": 0, "Cloudy": 3, "Rainy": 8, "Stormy": 15}[weather]
    peak_penalty = 7 if is_peak else 0
    rating_bonus = (p_rating - 3.0) * (-2)
    food_prep = {"Pizza": 5, "Chinese": 3, "Indian": 6, "Fast Food": 2, "Desserts": 1}[food_type]
    noise = np.random.normal(0, 5)

    actual_time = base_time + weather_penalty + peak_penalty + rating_bonus + food_prep + noise
    actual_time = round(max(10, min(90, actual_time)), 1)

    base_value = {"Pizza": 350, "Chinese": 300, "Indian": 280, "Fast Food": 200, "Desserts": 180}[food_type]
    order_value = round(base_value + np.random.normal(0, 80), 0)
    order_value = max(80, order_value)

    orders.append({
        "OrderID": f"ORD{str(i).zfill(5)}",
        "RestaurantLat": round(rest_lat, 6),
        "RestaurantLon": round(rest_lon, 6),
        "RestaurantName": rest_name,
        "FoodType": food_type,
        "DeliveryLat": round(del_lat, 6),
        "DeliveryLon": round(del_lon, 6),
        "CustomerArea": area,
        "Weather": weather,
        "PartnerID": pid,
        "PartnerRating": p_rating,
        "OrderHour": hour,
        "DayType": day_type,
        "OrderValue": order_value,
        "ActualDeliveryTime": actual_time,
        "DistanceKM": distance,
        "PeakHour": is_peak,
    })

df = pd.DataFrame(orders)
df.to_csv("datas/delivery_data.csv", index=False)

print(f"Generated {len(df)} orders")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 5 rows:")
print(df.head())
print(f"\nBasic stats:")
print(df.describe())
