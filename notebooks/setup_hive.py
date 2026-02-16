from pyhive import hive

conn = hive.Connection(
    host="localhost",
    port=10000,
    username="hive",
    database="default"
)
cursor = conn.cursor()

# Create the table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS delivery_data (
        OrderID            STRING,
        RestaurantLat      DOUBLE,
        RestaurantLon      DOUBLE,
        RestaurantName     STRING,
        FoodType           STRING,
        DeliveryLat        DOUBLE,
        DeliveryLon        DOUBLE,
        CustomerArea       STRING,
        Weather            STRING,
        PartnerID          STRING,
        PartnerRating      DOUBLE,
        OrderHour          INT,
        DayType            STRING,
        OrderValue         DOUBLE,
        ActualDeliveryTime DOUBLE,
        DistanceKM         DOUBLE,
        PeakHour           INT
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
    TBLPROPERTIES ('skip.header.line.count'='1')
""")
print("Table created.")

# Load CSV into the table
cursor.execute("""
    LOAD DATA LOCAL INPATH '/tmp/delivery_data.csv'
    OVERWRITE INTO TABLE delivery_data
""")
print("Data loaded.")

# Verify
cursor.execute("SELECT COUNT(*) FROM delivery_data")
print(f"Row count: {cursor.fetchone()[0]}")

cursor.execute("SELECT * FROM delivery_data LIMIT 3")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()