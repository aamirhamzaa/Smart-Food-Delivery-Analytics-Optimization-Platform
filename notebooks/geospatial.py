import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, MarkerCluster

df = pd.read_csv("datas/delivery_data_enriched.csv")

center_lat = df["RestaurantLat"].mean()
center_lon = df["RestaurantLon"].mean()


# Map 1: Delivery Performance Heatmap
m1 = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="cartodbpositron")

delayed = df[df["IsDelayed"] == True]
on_time = df[df["IsDelayed"] == False]

heat_data_delayed = delayed[["DeliveryLat", "DeliveryLon"]].values.tolist()
heat_data_ontime = on_time[["DeliveryLat", "DeliveryLon"]].values.tolist()

HeatMap(
    heat_data_delayed,
    name="Delayed Deliveries (Red)",
    gradient={0.4: "yellow", 0.65: "orange", 1: "red"},
    radius=20, blur=15, max_zoom=15
).add_to(m1)

folium.LayerControl().add_to(m1)

legend_html = """
<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
     background-color: white; padding: 15px; border-radius: 5px;
     border: 2px solid grey; font-size: 13px;">
     <b>Delivery Performance Heatmap</b><br>
     <span style="color: red;">Red zones</span> = High delay concentration<br>
     <span style="color: yellow;">Yellow zones</span> = Moderate delays<br>
</div>
"""
m1.get_root().html.add_child(folium.Element(legend_html))

m1.save("output/maps/01_delivery_heatmap.html")
print("Map 1 saved: Delivery Heatmap")


# Map 2: Partner Performance Map
m2 = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="cartodbpositron")

restaurants = df.groupby("RestaurantName").agg(
    lat=("RestaurantLat", "mean"),
    lon=("RestaurantLon", "mean"),
    avg_time=("ActualDeliveryTime", "mean"),
    avg_rating=("PartnerRating", "mean"),
    total_orders=("OrderID", "count"),
    avg_value=("OrderValue", "mean"),
    food_type=("FoodType", "first"),
).round(2)

for name, row in restaurants.iterrows():
    if row["avg_time"] < 30:
        color = "green"
        status = "Fast"
    elif row["avg_time"] < 40:
        color = "orange"
        status = "Normal"
    else:
        color = "red"
        status = "Slow"

    popup_html = f"""
    <div style="font-family: Arial; width: 200px;">
        <h4 style="margin: 0; color: {color};">{name}</h4>
        <hr style="margin: 3px 0;">
        <b>Food Type:</b> {row['food_type']}<br>
        <b>Avg Delivery:</b> {row['avg_time']:.1f} min ({status})<br>
        <b>Avg Rating:</b> {row['avg_rating']:.1f}/5.0<br>
        <b>Total Orders:</b> {row['total_orders']}<br>
        <b>Avg Order Value:</b> Rs.{row['avg_value']:.0f}<br>
    </div>
    """

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=row["total_orders"] / 8,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{name} | {row['avg_time']:.0f}min | {row['avg_rating']:.1f}*"
    ).add_to(m2)

m2.save("output/maps/02_partner_performance_map.html")
print("Map 2 saved: Partner Performance Map")


# Map 3: Route Analysis - Longest Routes
m3 = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="cartodbpositron")

longest_routes = df.nlargest(50, "ActualDeliveryTime")

for _, row in longest_routes.iterrows():
    time_norm = (row["ActualDeliveryTime"] - 40) / (df["ActualDeliveryTime"].max() - 40)
    time_norm = max(0, min(1, time_norm))

    r = int(255 * time_norm)
    g = int(255 * (1 - time_norm))
    color = f"#{r:02x}{g:02x}00"

    folium.PolyLine(
        locations=[
            [row["RestaurantLat"], row["RestaurantLon"]],
            [row["DeliveryLat"], row["DeliveryLon"]]
        ],
        weight=3,
        color=color,
        opacity=0.7,
        tooltip=f"Order: {row['OrderID']} | Time: {row['ActualDeliveryTime']}min | Dist: {row['DistanceKM']}km"
    ).add_to(m3)

    folium.CircleMarker(
        location=[row["RestaurantLat"], row["RestaurantLon"]],
        radius=4, color="blue", fill=True, fill_opacity=0.8
    ).add_to(m3)

    folium.CircleMarker(
        location=[row["DeliveryLat"], row["DeliveryLon"]],
        radius=4, color=color, fill=True, fill_opacity=0.8
    ).add_to(m3)

route_legend = """
<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
     background-color: white; padding: 15px; border-radius: 5px;
     border: 2px solid grey; font-size: 13px;">
     <b>Top 50 Longest Delivery Routes</b><br>
     <span style="color: blue;">Blue dots</span> = Restaurants<br>
     <span style="color: red;">Red lines</span> = Slowest deliveries<br>
     <span style="color: green;">Green lines</span> = Relatively faster<br>
</div>
"""
m3.get_root().html.add_child(folium.Element(route_legend))
m3.save("output/maps/03_route_analysis.html")
print("Map 3 saved: Route Analysis")


# Map 4: Restaurant Clustering with Density
m4 = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="cartodbpositron")

marker_cluster = MarkerCluster(name="Restaurant Clusters").add_to(m4)

for name, row in restaurants.iterrows():
    food_icons = {
        "Pizza": "cutlery", "Chinese": "cutlery", "Indian": "cutlery",
        "Fast Food": "cutlery", "Desserts": "cutlery"
    }
    food_colors_map = {
        "Pizza": "red", "Chinese": "orange", "Indian": "green",
        "Fast Food": "blue", "Desserts": "pink"
    }

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=f"{name}<br>{row['food_type']}<br>Orders: {row['total_orders']}",
        icon=folium.Icon(
            color=food_colors_map.get(row["food_type"], "gray"),
            icon=food_icons.get(row["food_type"], "cutlery"),
            prefix="fa"
        )
    ).add_to(marker_cluster)

delivery_heat = df[["DeliveryLat", "DeliveryLon"]].values.tolist()
HeatMap(delivery_heat, name="Delivery Density", radius=15, blur=10).add_to(m4)

folium.LayerControl().add_to(m4)
m4.save("output/maps/04_restaurant_clusters.html")
print("Map 4 saved: Restaurant Clustering")

print("\nAll maps saved to output/maps/")