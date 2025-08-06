-- basic_eda.sql
-- This script contains a set of basic Exploratory Data Analysis (EDA) queries
-- designed to provide initial insights into the current state and performance
-- of the order and inventory management system. These queries help identify
-- trends, potential issues, and key metrics at a high level.
-- 1. Order Status Distribution
-- Description: This query calculates the count and percentage distribution of
--              all orders based on their current status.
-- Purpose:     To quickly understand the overall health of orders (e.g., how many
--              are fulfilled vs. unfulfilled, partial, or expired). This helps
--              identify bottlenecks or common end-states for orders.
-- Output:      ORDER_STATUS (e.g., 'fulfilled', 'unfulfilled'), ORDER_COUNT (number of orders in that status),
--              PERCENTAGE_OF_ORDERS (percentage of total orders for that status).
SELECT
	ORDER_STATUS,
	COUNT(*) AS ORDER_COUNT,
	ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS PERCENTAGE_OF_ORDERS
FROM
	ORDERS
GROUP BY
	ORDER_STATUS
ORDER BY
	PERCENTAGE_OF_ORDERS DESC;

-- 2. Top Suppliers by Order Failure Count
-- Description: Identifies suppliers whose items are most frequently associated with
--              orders that have reached an 'expired' or 'partial - expired' status.
-- Purpose:     To pinpoint potential problem suppliers contributing to unfulfilled
--              or problematic orders. This can guide investigations into supplier
--              performance, stock issues, or delivery reliability.
-- Output:      SUPPLIER_NAME, FAILURE_COUNT (number of associated order items in failed orders).
SELECT
	S.NAME AS SUPPLIER_NAME,
	COUNT(*) AS FAILURE_COUNT
FROM
	ORDER_ITEMS OI
	JOIN SUPPLIERS S ON OI.SUPPLIER_ID = S.SUPPLIER_ID
	JOIN ORDERS O ON OI.ORDER_ID = O.ORDER_ID
WHERE
	O.ORDER_STATUS IN ('partial - expired', 'expired')
GROUP BY
	S.NAME
ORDER BY
	FAILURE_COUNT DESC;

-- 3. Supplier Order Status Breakdown
-- Description: Provides a detailed breakdown of order statuses for each supplier,
--              showing how many orders (or order items) from a given supplier
--              fall into each status category.
-- Purpose:     Offers a more granular view of supplier performance compared to the
--              "Top Suppliers by Order Failure Count" query. It helps understand
--              if a supplier primarily fulfills orders or contributes significantly
--              to specific problematic statuses.
-- Output:      SUPPLIER_NAME, ORDER_STATUS, ORDER_COUNT (number of associated order items for that supplier and status).
SELECT
	S.NAME AS SUPPLIER_NAME,
	O.ORDER_STATUS,
	COUNT(*) AS ORDER_COUNT
FROM
	ORDERS O
	JOIN ORDER_ITEMS OI ON O.ORDER_ID = OI.ORDER_ID
	JOIN SUPPLIERS S ON OI.SUPPLIER_ID = S.SUPPLIER_ID
GROUP BY
	S.NAME,
	O.ORDER_STATUS
ORDER BY
	S.NAME,
	ORDER_COUNT DESC;

-- 4. Item Fulfillment Rate
-- Description: Calculates the average fulfillment rate for each item, based on
--              the ratio of FULFILLED_QUANTITY to the original QUANTITY ordered.
-- Purpose:     To identify items that frequently experience low fulfillment rates.
--              This can highlight issues with popular items going out of stock,
--              problems with specific item logistics, or inaccurate inventory.
-- Output:      NAME (Item Name), AVG_FULFILLMENT_RATE (average rate between 0.00 and 1.00).
SELECT
	I.NAME,
	ROUND(
		AVG(
			1.0 * OI.FULFILLED_QUANTITY / NULLIF(OI.QUANTITY, 0)
		),
		2
	) AS AVG_FULFILLMENT_RATE
FROM
	ORDER_ITEMS OI
	JOIN ITEMS I ON OI.ITEM_ID = I.ITEM_ID
GROUP BY
	I.NAME
ORDER BY
	AVG_FULFILLMENT_RATE ASC;