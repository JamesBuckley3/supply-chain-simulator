-- create_tables.sql
-- Table: ITEMS
-- Description: Stores information about individual products available for sale.
CREATE TABLE ITEMS (
	ITEM_ID SERIAL PRIMARY KEY, -- Unique identifier for the item.
	NAME TEXT, -- Name of the item.
	CATEGORY TEXT, -- Classification or type of the item (e.g., 'Electronics', 'Books', 'Clothing').
	UNIT_PRICE NUMERIC(10, 2) -- The price of a single unit of the item. Must be non-negative.
	CHECK (UNIT_PRICE >= 0)
);

-- Table: CUSTOMERS
-- Description: Contains details about customers who place orders.
CREATE TABLE CUSTOMERS (
	CUSTOMER_ID SERIAL PRIMARY KEY, -- Unique identifier for the customer.
	NAME TEXT, -- Full name of the customer.
	REGION TEXT -- Geographic region of the customer (e.g., 'North', 'South').
);

-- Table: SUPPLIERS
-- Description: Stores information about companies that provide inventory items.
CREATE TABLE SUPPLIERS (
	SUPPLIER_ID SERIAL PRIMARY KEY, -- Unique identifier for the supplier.
	NAME TEXT, -- Name of the supplier company.
	CATEGORY TEXT -- Category of products the supplier specializes in (e.g., 'Electronics', 'Books').
);

-- Table: INVENTORY
-- Description: Tracks the current stock levels for each item, broken down by supplier.
-- This table helps manage reorder points and current quantities.
CREATE TABLE INVENTORY (
	ITEM_ID INT REFERENCES ITEMS (ITEM_ID), -- Foreign key linking to the ITEMS table.
	SUPPLIER_ID INT REFERENCES SUPPLIERS (SUPPLIER_ID), -- Foreign key linking to the SUPPLIERS table.
	QUANTITY_ON_HAND INT CHECK (QUANTITY_ON_HAND >= 0), -- Current number of units of the item available from this supplier. Must be non-negative.
	REORDER_POINT INT CHECK (REORDER_POINT >= 0), -- The quantity at which new stock should be ordered from the manufacturer. Must be non-negative.
	LAST_UPDATED DATE, -- The date when the inventory level was last updated.
	PRIMARY KEY (ITEM_ID, SUPPLIER_ID) -- Composite primary key ensuring uniqueness for each item-supplier pair.
);

-- Table: ORDERS
-- Description: Represents customer orders. An order can contain multiple items.
CREATE TABLE ORDERS (
	ORDER_ID SERIAL PRIMARY KEY, -- Unique identifier for the order.
	CUSTOMER_ID INT REFERENCES CUSTOMERS (CUSTOMER_ID), -- Foreign key linking to the CUSTOMERS table.
	ORDER_DATE DATE, -- The date the order was placed.
	ORDER_STATUS TEXT CHECK (
		ORDER_STATUS IN (
			'fulfilled',
			'partial',
			'partial - expired',
			'unfulfilled',
			'expired'
		)
	)
	-- Description of ORDER_STATUS values:
	-- 'unfulfilled': The order has been placed but no items have been fully shipped yet.
	-- 'partial': One or more - but not all items in the order have been fully shipped.
	-- 'fulfilled': All items in the order have been fully shipped to the customer.
	-- 'expired': Orders that were previously considered unfulfilled but became 14 days old.
	-- 'partial - expired': Orders that were previously considered partially fulfilled but became 14 days old.
	-- FOR CLARITY: FULLY SHIPPED MEANS AN ITEM'S FULFILLED QUANTITY = ORDERED QUANTITY
);

-- Table: ORDER_ITEMS
-- Description: Details the individual items within each customer order.
-- This table links an order to the specific items, their quantities, and the supplier from which they were sourced for that order.
CREATE TABLE ORDER_ITEMS (
	ORDER_ITEM_ID SERIAL PRIMARY KEY, -- Unique identifier for each line item within an order.
	ORDER_ID INT REFERENCES ORDERS (ORDER_ID), -- Foreign key linking to the ORDERS table.
	ITEM_ID INT REFERENCES ITEMS (ITEM_ID), -- Foreign key linking to the ITEMS table, indicating which item was ordered.
	SUPPLIER_ID INT REFERENCES SUPPLIERS (SUPPLIER_ID), -- Foreign key linking to the SUPPLIERS table, indicating the supplier for this specific item in the order.
	QUANTITY INT CHECK (QUANTITY >= 0), -- The total quantity of the item ordered. Must be non-negative.
	FULFILLED_QUANTITY INT CHECK ( -- The quantity of the item that has actually been shipped.
		FULFILLED_QUANTITY >= 0
		AND FULFILLED_QUANTITY <= QUANTITY -- Fulfilled quantity cannot exceed the ordered quantity.
	),
	FULFILLED_DATE DATE, -- The date when this specific order item was fulfilled (or last partly fulfilled).
	UNIQUE (ORDER_ID, ITEM_ID, SUPPLIER_ID) -- Ensures that each item from a specific supplier appears only once per order.
);