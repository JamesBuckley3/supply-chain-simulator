"""
simulation.py

This module defines the Simulation class, which models a supply chain system over time.
It simulates order creation, fulfillment, inventory restocking, and order expiration,
and logs inventory and fulfillment activity for later export.

Typical usage:
    from simulation import Simulation

    sim = Simulation(conn, generator)
    sim.run(iterations=10000)
"""

from datetime import timedelta
import random
from models import *
import csv


class Simulation:
    """
    Runs a time-based simulation of a supply chain inventory and fulfillment system.

    The simulation advances in small random time increments and randomly triggers
    events such as order creation, fulfillment attempts, inventory restocking, and
    order expiration. The results are stored in memory and periodically exported
    to CSV logs.

    Attributes:
        conn (psycopg2.connection): Active database connection.
        cur (psycopg2.cursor): Cursor for executing queries.
        suppliers (dict): Dictionary of Supplier instances keyed by ID.
        items (dict): Dictionary of Item instances keyed by ID.
        customers (dict): Dictionary of Customer instances keyed by ID.
        supplier_items (dict): Maps supplier IDs to lists of item IDs they provide.
        sim_time (datetime): Current simulation timestamp.
        inventory_history (list): Log of inventory snapshots over time.
        order_fulfillment_log (list): Log of fulfillment attempts.
        recent_fulfillments (list): Temporary buffer for fulfillments until flush.
        cached_unfulfilled_orders (list): List of unexpired, unfulfilled order IDs.
    """

    def __init__(self, conn, generator):
        """
        Initialises the Simulation with a database connection and data generator.

        Args:
            conn (psycopg2.connection): An active database connection object.
            generator (object): An object containing initial simulation data
                                (suppliers, items, customers, etc.).
        """
        self.conn = conn
        self.cur = conn.cursor()

        self.suppliers = generator.suppliers
        self.items = generator.items
        self.customers = generator.customers
        self.supplier_items = generator.supplier_items
        self.sim_time = generator.sim_time

        self.inventory_history = []
        self.order_fulfillment_log = []
        self.recent_fulfillments = []
        self.cached_unfulfilled_orders = []

    def query_one(self, sql, params=()):
        """
        Executes a SQL query and returns the first row of the result.

        Args:
            sql (str): The SQL query string.
            params (tuple): Parameters to pass to the query.

        Returns:
            tuple: The first row of the query result, or None if no rows.
        """
        self.cur.execute(sql, params)
        return self.cur.fetchone()

    def query_all(self, sql, params=()):
        """
        Executes a SQL query and returns all rows of the result.

        Args:
            sql (str): The SQL query string.
            params (tuple): Parameters to pass to the query.

        Returns:
            list: A list of tuples, where each tuple is a row from the query result.
        """
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def execute(self, sql, params=()):
        """
        Executes a SQL query without returning any results.

        Args:
            sql (str): The SQL query string.
            params (tuple): Parameters to pass to the query.
        """
        self.cur.execute(sql, params)

    def increment_time(self):
        """
        Increments the simulation time by a random number of minutes.
        """
        self.sim_time += timedelta(minutes=random.randint(1, 15))

    def create_order(self):
        """
        Creates a new order with random items and a random customer.

        Inserts a new order into the 'ORDERS' table and then adds multiple
        order items to the 'ORDER_ITEMS' table, associating them with
        eligible suppliers.
        """
        customer = random.choice(list(self.customers.values()))
        self.cur.execute(
            "INSERT INTO ORDERS (CUSTOMER_ID, ORDER_DATE, ORDER_STATUS) VALUES (%s, %s, %s) RETURNING ORDER_ID",
            (customer.id, self.sim_time, "unfulfilled"),
        )
        order_id = self.cur.fetchone()[0]

        for item in random.sample(list(self.items.values()), k=random.randint(1, 5)):
            eligible_suppliers = [
                sid for sid, items in self.supplier_items.items() if item.id in items
            ]

            if not eligible_suppliers:
                continue

            supplier_id = random.choice(eligible_suppliers)

            self.cur.execute(
                "INSERT INTO ORDER_ITEMS (ORDER_ID, ITEM_ID, SUPPLIER_ID, QUANTITY, FULFILLED_QUANTITY, FULFILLED_DATE) "
                "VALUES (%s, %s, %s, %s, %s, NULL)",
                (order_id, item.id, supplier_id, random.randint(1, 5), 0),
            )

    def fulfill_order(self):
        """
        Attempts to fulfill a random unfulfilled order item.

        Selects an unfulfilled order and then a random unfulfilled item within
        that order. It then attempts to fulfill a portion or all of that item
        based on available inventory and logs the fulfillment attempt.
        """
        order_id = self._select_random_unfulfilled_order()
        if not order_id:
            return

        item_data = self._get_random_unfulfilled_item(order_id)
        if not item_data:
            return

        (order_item_id, item_id, supplier_id, quantity, fulfilled_quantity) = item_data

        result = self._attempt_fulfillment(
            order_id, order_item_id, item_id, supplier_id, quantity, fulfilled_quantity
        )

        self.recent_fulfillments.append(result)

    def restock_inventory(self):
        """
        Restocks inventory for items that are below their reorder point.

        Queries for items with low stock and randomly selects one based on
        item restock weights. It then calculates a restock amount and updates
        the inventory quantity.
        """
        self.cur.execute(
            """
            SELECT ITEM_ID, SUPPLIER_ID
            FROM INVENTORY
            WHERE QUANTITY_ON_HAND <= REORDER_POINT
            """
        )
        low_stock = self.cur.fetchall()

        if low_stock:
            item_ids = [item_id for item_id, _ in low_stock]
            weights = [self.items[item_id].restock_weight for item_id in item_ids]

            chosen_index = random.choices(range(len(low_stock)), weights=weights, k=1)[
                0
            ]
            item_id, supplier_id = low_stock[chosen_index]

            item = self.items[item_id]
            supplier = self.suppliers[supplier_id]
            max_qty = supplier.max_quantity

            self.cur.execute(
                """
                SELECT QUANTITY_ON_HAND
                FROM INVENTORY
                WHERE ITEM_ID = %s AND SUPPLIER_ID = %s
                """,
                (item_id, supplier_id),
            )
            current_qty = self.cur.fetchone()[0]

            base_restock = 10
            scaled = int(base_restock * item.restock_weight)
            restock_amount = min(scaled, max_qty - current_qty)

            self.cur.execute(
                """
                UPDATE INVENTORY
                SET QUANTITY_ON_HAND = QUANTITY_ON_HAND + %s,
                    LAST_UPDATED = %s
                WHERE ITEM_ID = %s AND SUPPLIER_ID = %s
                """,
                (restock_amount, self.sim_time.date(), item_id, supplier_id),
            )
        else:
            pass  # No items to restock

    def expire_old_orders(self):
        """
        Identifies and updates the status of old unfulfilled or partially fulfilled orders to 'expired'.

        Orders older than 14 days with 'unfulfilled' or 'partial' status are marked as expired.
        """
        self.cur.execute(
            """
            SELECT ORDER_ID, ORDER_DATE
            FROM ORDERS
            WHERE ORDER_STATUS IN ('unfulfilled', 'partial')
            AND ORDER_DATE <= %s
            """,
            (self.sim_time.date() - timedelta(days=14),),
        )

        rows = self.cur.fetchall()

        for order_id, order_date in rows:
            self.update_order_status(order_id, order_date)

    def update_order_status(self, order_id, order_date):
        """
        Updates the status of a specific order based on its fulfillment progress and age.

        Args:
            order_id (int): The ID of the order to update.
            order_date (datetime.date): The creation date of the order.
        """
        unfulfilled, fulfilled, total = self.query_one(
            """
            SELECT
                SUM(CASE WHEN FULFILLED_QUANTITY = 0 THEN 1 ELSE 0 END) AS unfulfilled,
                SUM(CASE WHEN FULFILLED_QUANTITY = QUANTITY THEN 1 ELSE 0 END) AS fulfilled,
                COUNT(*) AS total
            FROM ORDER_ITEMS
            WHERE ORDER_ID = %s
            """,
            (order_id,),
        )

        is_expired = (self.sim_time.date() - order_date).days >= 14

        if unfulfilled == total and is_expired:
            status = "expired"
        elif is_expired:
            status = "partial - expired"
        elif fulfilled == total:
            status = "fulfilled"
        elif fulfilled == 0:
            status = "unfulfilled"
        else:
            status = "partial"

        self.cur.execute(
            "UPDATE ORDERS SET ORDER_STATUS = %s WHERE ORDER_ID = %s",
            (status, order_id),
        )

    def update_cached_unfulfilled_orders(self):
        """
        Refreshes the internal cache of unfulfilled or partially fulfilled order IDs.

        This method queries the database for all orders that are currently
        'partial' or 'unfulfilled' and are not yet expired (within 14 days
        of their order date), storing their IDs in
        `self.cached_unfulfilled_orders` for quick access.
        """
        rows = self.query_all(
            """
            SELECT ORDER_ID
            FROM ORDERS
            WHERE ORDER_STATUS IN ('partial', 'unfulfilled')
            AND ORDER_DATE >= %s
        """,
            (self.sim_time - timedelta(days=14),),
        )
        self.cached_unfulfilled_orders = [row[0] for row in rows]

    def _select_random_unfulfilled_order(self):
        """
        Selects a random unfulfilled or partially fulfilled order ID from the cache.

        Returns:
            int or None: The ID of a random unfulfilled order, or None if no such orders exist.
        """
        if not self.cached_unfulfilled_orders:
            return None
        return random.choice(self.cached_unfulfilled_orders)

    def _get_random_unfulfilled_item(self, order_id):
        """
        Retrieves a random unfulfilled item within a given order.

        Args:
            order_id (int): The ID of the order to search within.

        Returns:
            tuple or None: A tuple containing (order_item_id, item_id, supplier_id, quantity, fulfilled_quantity)
                           for a randomly selected unfulfilled item, or None if no such items exist.
        """

        candidates = self.query_all(
            """
            SELECT ORDER_ITEM_ID, ITEM_ID, SUPPLIER_ID, QUANTITY, FULFILLED_QUANTITY
            FROM ORDER_ITEMS
            WHERE ORDER_ID = %s AND FULFILLED_QUANTITY < QUANTITY
        """,
            (order_id,),
        )

        if not candidates:
            return None
        return random.choice(candidates)

    def _attempt_fulfillment(
        self,
        order_id,
        order_item_id,
        item_id,
        supplier_id,
        quantity,
        fulfilled_quantity,
    ):
        """
        Attempts to fulfill a specific order item.

        Checks for supplier reliability and available inventory. If successful,
        it updates inventory and order item fulfillment quantities, then
        updates the overall order status. Logs the outcome of the attempt.

        Args:
            order_id (int): The ID of the parent order.
            order_item_id (int): The ID of the specific order item being fulfilled.
            item_id (int): The ID of the item.
            supplier_id (int): The ID of the supplier for this item.
            quantity (int): The total quantity requested for this order item.
            fulfilled_quantity (int): The quantity already fulfilled for this order item.

        Returns:
            dict: A dictionary containing details of the fulfillment attempt,
                  including success status, quantity fulfilled, and any failure reason.
        """
        item = self.items.get(item_id)
        supplier = self.suppliers.get(supplier_id)

        timestamp = self.sim_time.isoformat()
        remaining_qty = quantity - fulfilled_quantity

        result_data = {
            "order_id": order_id,
            "item_id": item_id,
            "supplier_id": supplier_id,
            "requested_qty": quantity,
            "previously_fulfilled": fulfilled_quantity,
            "newly_fulfilled": 0,
            "success": False,
            "failure_reason": None,
            "timestamp": timestamp,
        }

        if random.random() < supplier.failure_rate + item.failure_rate:
            result_data["failure_reason"] = "unreliable_supplier"
            return result_data

        result = self.query_one(
            """
            SELECT QUANTITY_ON_HAND
            FROM INVENTORY
            WHERE ITEM_ID = %s AND SUPPLIER_ID = %s
        """,
            (item_id, supplier_id),
        )

        if not result:
            result_data["failure_reason"] = "no_inventory_entry"
            return result_data

        available_qty = result[0]
        if available_qty == 0:
            result_data["failure_reason"] = "stockout"
            return result_data

        fulfill_qty = min(available_qty, remaining_qty)

        self.cur.execute(
            "UPDATE INVENTORY SET QUANTITY_ON_HAND = QUANTITY_ON_HAND - %s, LAST_UPDATED = %s "
            "WHERE ITEM_ID = %s AND SUPPLIER_ID = %s",
            (fulfill_qty, self.sim_time.date(), item_id, supplier_id),
        )

        self.cur.execute(
            "UPDATE ORDER_ITEMS SET FULFILLED_QUANTITY = FULFILLED_QUANTITY + %s, FULFILLED_DATE = %s "
            "WHERE ORDER_ITEM_ID = %s",
            (fulfill_qty, self.sim_time.date(), order_item_id),
        )

        self.update_order_status(order_id, self.sim_time.date())

        result_data.update(
            {
                "newly_fulfilled": fulfill_qty,
                "success": True,
            }
        )
        return result_data

    def log_inventory_snapshot(self):
        """
        Records the current state of inventory and relevant metrics.

        Takes a snapshot of all inventory items, including quantity on hand,
        restock weights, fulfillment weights, and unfulfilled backlog quantities,
        and appends it to the `inventory_history` log.
        """
        self.cur.execute(
            """
            SELECT ITEM_ID, SUPPLIER_ID, QUANTITY_ON_HAND
            FROM INVENTORY
            """
        )
        for item_id, supplier_id, qty in self.cur.fetchall():
            item = self.items[item_id]
            supplier = self.suppliers[supplier_id]

            self.cur.execute(
                """
                SELECT SUM(QUANTITY - FULFILLED_QUANTITY)
                FROM ORDER_ITEMS
                WHERE ITEM_ID = %s AND SUPPLIER_ID = %s AND FULFILLED_QUANTITY < QUANTITY
                """,
                (item_id, supplier_id),
            )
            unfulfilled_units = self.cur.fetchone()[0] or 0

            self.inventory_history.append(
                {
                    "timestamp": self.sim_time.isoformat(),
                    "item_id": item_id,
                    "supplier_id": supplier_id,
                    "quantity_on_hand": qty,
                    "restock_weight": item.restock_weight,
                    "fulfillment_weight": supplier.fulfillment_weight,
                    "backlog_unfulfilled_qty": unfulfilled_units,
                }
            )

    def export_logs(
        self,
        inventory_filename="inventory_history.csv",
        fulfillment_filename="fulfillment_log.csv",
    ):
        """
        Exports the collected inventory history and order fulfillment logs to CSV files.

        Args:
            inventory_filename (str): The filename for the inventory history CSV.
                                      Defaults to "inventory_history.csv".
            fulfillment_filename (str): The filename for the fulfillment log CSV.
                                        Defaults to "fulfillment_log.csv".
        """
        if self.inventory_history:
            with open(inventory_filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.inventory_history[0].keys())
                writer.writeheader()
                writer.writerows(self.inventory_history)
            print(f"📁 Inventory history exported to {inventory_filename}")
        else:
            print("⚠️ No inventory history to export.")

        if self.order_fulfillment_log:
            with open(fulfillment_filename, "w", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=self.order_fulfillment_log[0].keys()
                )
                writer.writeheader()
                writer.writerows(self.order_fulfillment_log)
            print(f"📁 Fulfillment log exported to {fulfillment_filename}")
        else:
            print("⚠️ No fulfillment log to export.")

    def run(self, iterations=100):
        """
        Runs the supply chain simulation loop for a specified number of steps.

        At each iteration, time is incremented, and one of several possible events
        is randomly selected and executed:
            - create_order
            - fulfill_order
            - restock
            - idle

        Every 100 iterations, inventory snapshots and fulfillment logs are flushed
        to memory, and expired orders are updated. Logs are exported at the end.

        Args:
            iterations (int): Number of simulation steps to run. Defaults to 100.
        """

        print(
            f"🚀 Starting simulation at {self.sim_time.date()} with {iterations} steps..."
        )

        for i in range(1, iterations):
            self.increment_time()

            if i % 100 == 0:
                self.update_cached_unfulfilled_orders()
                self.expire_old_orders()
                self.order_fulfillment_log.extend(self.recent_fulfillments)
                self.recent_fulfillments = []
                self.log_inventory_snapshot()
                self.conn.commit()

            event = random.choices(
                ["create_order", "fulfill_order", "restock", "idle"],
                weights=[0.2, 0.65, 0.05, 0.1],
            )[0]

            try:
                if event == "create_order":
                    self.create_order()
                elif event == "fulfill_order":
                    self.fulfill_order()
                elif event == "restock":
                    self.restock_inventory()
            except Exception as e:
                print(f"❌ Error during {event}: {e}")

        self.conn.commit()
        print(f"✅ Simulation completed at {self.sim_time.date()}.")

        self.order_fulfillment_log.extend(self.recent_fulfillments)
        self.recent_fulfillments.clear()

        self.export_logs()
