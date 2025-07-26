Methodology
===========

The simulation operates on a discrete-event, time-based model, progressing through a series of random events over a specified number of iterations.

1.  **Initialisation**:

    -   A PostgreSQL database connection is established.

    -   Synthetic data for `Suppliers`, `Items`, and `Customers` is generated using the `Faker` library, ensuring realistic names, categories, and regions.

    -   Initial `Inventory` levels are populated in the database, linking items to eligible suppliers based on categories and setting random reorder points.

    - An ERD (Entity Relationship Diagram) of the database:

    ![ERD](images/erd.png "ERD")


2.  **Simulation Loop**:

    -   The simulation time advances by a random small increment in each iteration.

    -   One of four events is randomly chosen to occur:

        -   **Order Creation**: A new customer order is generated with a random selection of items and quantities. This order is recorded in the `ORDERS` and `ORDER_ITEMS` tables with an initial 'unfulfilled' status.

        -   **Order Fulfillment**: The system attempts to fulfill a randomly selected unfulfilled item from an existing order. Fulfillment success depends on supplier reliability (failure rate) and available `Inventory`. If successful, `QUANTITY_ON_HAND` in `INVENTORY` is reduced, `FULFILLED_QUANTITY` in `ORDER_ITEMS` is updated, and the overall `ORDER_STATUS` is adjusted (e.g., to 'partial' or 'fulfilled').

        -   **Inventory Restocking**: For items whose `QUANTITY_ON_HAND` falls below their `REORDER_POINT`, a restock event is triggered. The restock amount is influenced by item-specific restock weights and supplier maximum quantities, updating the `INVENTORY` table.

        -   **Idle**: No specific action occurs, representing periods of inactivity.

    -   Error handling is in place to catch and report issues during event execution.

3.  **Periodic Updates & Logging**:

    -   Every 100 iterations, the simulation performs maintenance tasks:

        -   The cache of unfulfilled orders is refreshed.

        -   Old orders (older than 14 simulated days) that are still 'unfulfilled' or 'partial' are marked as 'expired' or 'partial - expired'.

        -   Recent fulfillment attempts are flushed from a temporary buffer to the main `order_fulfillment_log`.

        -   A snapshot of the current `Inventory` state, including `QUANTITY_ON_HAND`, `restock_weight`, `fulfillment_weight`, and `backlog_unfulfilled_qty`, is recorded in `inventory_history`.

        -   Database changes are committed.

4.  **Data Export**:

    -   Upon completion of all iterations, the accumulated `inventory_history` and `order_fulfillment_log` are exported to `inventory_history.csv` and `fulfillment_log.csv` files, respectively. These CSVs provide a comprehensive dataset for subsequent analysis.