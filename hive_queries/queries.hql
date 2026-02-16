CREATE EXTERNAL TABLE IF NOT EXISTS delivery_orders (
    OrderID STRING,
    RestaurantLat DOUBLE,
    RestaurantLon DOUBLE,
    RestaurantName STRING,
    FoodType STRING,
    DeliveryLat DOUBLE,
    DeliveryLon DOUBLE,
    CustomerArea STRING,
    Weather STRING,
    PartnerID STRING,
    PartnerRating DOUBLE,
    OrderHour INT,
    DayType STRING,
    OrderValue DOUBLE,
    ActualDeliveryTime DOUBLE,
    DistanceKM DOUBLE,
    PeakHour INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/delivery_data'
TBLPROPERTIES ('skip.header.line.count'='1');


-- Query 1: Average delivery time by weather and partner rating tier
SELECT
    Weather,
    CASE
        WHEN PartnerRating >= 4.0 THEN 'High'
        WHEN PartnerRating >= 3.0 THEN 'Medium'
        ELSE 'Low'
    END AS RatingTier,
    ROUND(AVG(ActualDeliveryTime), 2) AS AvgDeliveryTime,
    COUNT(*) AS OrderCount
FROM delivery_orders
GROUP BY
    Weather,
    CASE
        WHEN PartnerRating >= 4.0 THEN 'High'
        WHEN PartnerRating >= 3.0 THEN 'Medium'
        ELSE 'Low'
    END
ORDER BY Weather, RatingTier;


-- Query 2: Revenue at risk from delayed orders (over 40 min)
SELECT
    CustomerArea,
    COUNT(CASE WHEN ActualDeliveryTime > 40 THEN 1 END) AS DelayedOrders,
    COUNT(*) AS TotalOrders,
    ROUND(SUM(CASE WHEN ActualDeliveryTime > 40 THEN OrderValue ELSE 0 END), 2) AS RevenueAtRisk,
    ROUND(SUM(CASE WHEN ActualDeliveryTime > 40 THEN OrderValue ELSE 0 END) * 0.15, 2) AS EstimatedChurnLoss
FROM delivery_orders
GROUP BY CustomerArea
ORDER BY RevenueAtRisk DESC;


-- Query 3: Partner performance tiers
SELECT
    PartnerID,
    COUNT(*) AS TotalDeliveries,
    ROUND(AVG(ActualDeliveryTime), 2) AS AvgTime,
    ROUND(AVG(PartnerRating), 2) AS AvgRating,
    CASE
        WHEN AVG(PartnerRating) >= 4.0 AND AVG(ActualDeliveryTime) < 35 THEN 'Premium'
        WHEN AVG(PartnerRating) >= 3.0 AND AVG(ActualDeliveryTime) < 45 THEN 'Standard'
        ELSE 'Training'
    END AS PerformanceTier
FROM delivery_orders
GROUP BY PartnerID
ORDER BY AvgRating DESC;


-- Query 4: Peak vs off-peak efficiency
SELECT
    PeakHour,
    ROUND(AVG(ActualDeliveryTime), 2) AS AvgDeliveryTime,
    ROUND(AVG(OrderValue), 2) AS AvgOrderValue,
    COUNT(*) AS OrderCount,
    ROUND(SUM(OrderValue), 2) AS TotalRevenue
FROM delivery_orders
GROUP BY PeakHour;


-- Query 5: Food type preparation and delivery analysis
SELECT
    FoodType,
    ROUND(AVG(ActualDeliveryTime), 2) AS AvgDeliveryTime,
    ROUND(MIN(ActualDeliveryTime), 2) AS MinTime,
    ROUND(MAX(ActualDeliveryTime), 2) AS MaxTime,
    ROUND(AVG(OrderValue), 2) AS AvgOrderValue,
    COUNT(*) AS OrderCount
FROM delivery_orders
GROUP BY FoodType
ORDER BY AvgDeliveryTime DESC;


-- Query 6: Distance vs delivery time by area
SELECT
    CustomerArea,
    CASE
        WHEN DistanceKM < 3 THEN 'Short'
        WHEN DistanceKM < 6 THEN 'Medium'
        ELSE 'Long'
    END AS DistanceBucket,
    ROUND(AVG(ActualDeliveryTime), 2) AS AvgTime,
    ROUND(AVG(DistanceKM), 2) AS AvgDistance,
    COUNT(*) AS OrderCount
FROM delivery_orders
GROUP BY
    CustomerArea,
    CASE
        WHEN DistanceKM < 3 THEN 'Short'
        WHEN DistanceKM < 6 THEN 'Medium'
        ELSE 'Long'
    END
ORDER BY CustomerArea, DistanceBucket;