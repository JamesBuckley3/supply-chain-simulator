-- integrity_tests.sql
-- 1. Test: Negative Unit Prices
-- Description: Checks for any items with a unit price less than zero, which violates the business rule that prices must be non-negative.
-- Violation: Indicates incorrect data entry or a logical error in price calculation.
SELECT
	*
FROM
	ITEMS
WHERE
	UNIT_PRICE < 0;

-- 2. Test: Suppliers Providing Items from Multiple Categories
-- Description: Identifies suppliers that are associated with items belonging to more than one category.
-- This might indicate a data modeling issue if suppliers are expected to be specialised, or just an informative query.
-- Violation: If a supplier is intended to provide only one category, this flags a discrepancy.
SELECT
	SUPPLIER_ID,
	COUNT(DISTINCT I.CATEGORY) AS NUM_CATEGORIES
FROM
	INVENTORY INV
	JOIN ITEMS I ON INV.ITEM_ID = I.ITEM_ID
GROUP BY
	SUPPLIER_ID
HAVING
	COUNT(DISTINCT I.CATEGORY) > 1;

-- 3. Test: FULFILLED_QUANTITY Exceeding QUANTITY
-- Description: Verifies that the fulfilled quantity for any order item does not exceed the initially ordered quantity.
-- This enforces the physical constraint that you cannot fulfill more than was ordered.
-- Violation: Critical data inconsistency; indicates an error in the fulfillment process or data update.
SELECT
	*
FROM
	ORDER_ITEMS
WHERE
	FULFILLED_QUANTITY > QUANTITY;

-- 4. Test: Fulfilled Items Without a FULFILLED_DATE
-- Description: Checks for order items that show a fulfilled quantity greater than zero but have a NULL fulfilled date.
-- This ensures that a fulfillment date is always recorded when fulfillment occurs.
-- Violation: Incomplete or inconsistent fulfillment records.
SELECT
	*
FROM
	ORDER_ITEMS
WHERE
	FULFILLED_QUANTITY > 0
	AND FULFILLED_DATE IS NULL;

-- 5. Test: Inventory Below Reorder Point
-- Description: Flags items in inventory where the quantity on hand has fallen below their defined reorder point.
-- This is a proactive check for inventory management, not strictly a data *integrity* violation but a critical business alert.
-- Violation: Indicates a need to reorder stock to prevent depletion.
SELECT
	*
FROM
	INVENTORY
WHERE
	QUANTITY_ON_HAND < REORDER_POINT;

-- 6. Test: Orders Without Any Items
-- Description: Finds orders that exist in the ORDERS table but have no corresponding entries in the ORDER_ITEMS table.
-- Ensures referential integrity and that all orders actually contain items.
-- Violation: Orphaned orders; indicates an incomplete or erroneous order creation process.
SELECT
	*
FROM
	ORDERS O
WHERE
	NOT EXISTS (
		SELECT
			1
		FROM
			ORDER_ITEMS OI
		WHERE
			OI.ORDER_ID = O.ORDER_ID
	);

-- 7. Test: Item Category Mismatch with Supplier Category in Inventory
-- Description: Checks if an item supplied by a supplier has a category different from the supplier's stated category.
-- This might indicate a data entry error or a loose adherence to supplier categorization.
-- Violation: Potential categorisation discrepancy; might need clarification on business rules for supplier/item categories.
SELECT
	S.SUPPLIER_ID,
	S.CATEGORY AS SUPPLIER_CATEGORY,
	I.CATEGORY AS ITEM_CATEGORY
FROM
	INVENTORY INV
	JOIN SUPPLIERS S ON INV.SUPPLIER_ID = S.SUPPLIER_ID
	JOIN ITEMS I ON INV.ITEM_ID = I.ITEM_ID
WHERE
	S.CATEGORY <> I.CATEGORY;

-- 8. Test: 'Fulfilled' Orders with Unfulfilled Items
-- Description: Identifies orders marked as 'fulfilled' where at least one of their associated order items is not fully fulfilled (i.e., FULFILLED_QUANTITY < QUANTITY).
-- This ensures consistency between the overall order status and the fulfillment status of its individual items.
-- Violation: Logical inconsistency; an order should only be 'fulfilled' if all its items are fully fulfilled.
SELECT
	O.ORDER_ID
FROM
	ORDERS O
	JOIN ORDER_ITEMS OI ON O.ORDER_ID = OI.ORDER_ID
WHERE
	O.ORDER_STATUS = 'fulfilled'
	AND OI.FULFILLED_QUANTITY < OI.QUANTITY;

-- 9. Test: Inconsistent 'Partial' Order Status
-- Description: Checks for orders marked as 'partial' that either have no items fulfilled at all, or all items are fully fulfilled.
-- A 'partial' order should have at least one item fully fulfilled and at least one item not fully fulfilled.
-- Violation: Misclassification of order status; these orders should likely be 'unfulfilled' or 'fulfilled'.
SELECT
	O.ORDER_ID
FROM
	ORDERS O
	JOIN ORDER_ITEMS OI ON O.ORDER_ID = OI.ORDER_ID
GROUP BY
	O.ORDER_ID,
	O.ORDER_STATUS
HAVING
	O.ORDER_STATUS = 'partial'
	AND (
		SUM(
			CASE
				WHEN OI.FULFILLED_QUANTITY > 0 THEN 1
				ELSE 0
			END
		) = 0 -- No items fulfilled at all
		OR SUM(
			CASE
				WHEN OI.FULFILLED_QUANTITY = OI.QUANTITY THEN 1
				ELSE 0
			END
		) = COUNT(*) -- All items fully fulfilled
	);

-- 10. Test: Recently Expired Orders
-- Description: Flags orders that are marked as 'expired' or 'partial - expired' but were placed within the last 14 days.
-- This query helps identify orders that expired unexpectedly quickly, potentially indicating a problem with stock or fulfillment processes rather than just old, unfulfilled orders.
-- Violation: Not strictly a data integrity violation, but a business process anomaly requiring investigation (e.g., immediate stock shortages, quick cancellations).
SELECT
	ORDER_ID,
	ORDER_DATE,
	ORDER_STATUS
FROM
	ORDERS
WHERE
	ORDER_STATUS IN ('expired', 'partial - expired')
	AND ORDER_DATE > CURRENT_DATE - INTERVAL '14 days'
ORDER BY
	ORDER_DATE DESC;