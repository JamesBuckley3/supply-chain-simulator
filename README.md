Supply Chain Simulator
======================

Project Overview
----------------

The Supply Chain Simulator is a Python-based project designed to simulate the dynamic behavior of a supply chain, including order generation, inventory management, and fulfillment processes. The simulation interacts with a PostgreSQL database to store and manage supply chain entities and their states. The primary goal of this project is to generate realistic supply chain data that can be analysed to understand fulfillment rates and identify factors contributing to unfulfilled or partially unfulfilled customer orders.

### Key Features:

Key Features:

- **Database Schema**: PostgreSQL setup with tables for core supply chain entities (items, customers, suppliers, inventory, orders).

- **Synthetic Data**: Realistic mock data generation for entities using Faker, including dynamic attributes like failure rates and weights.

- **Dynamic Simulation**: Simulates key supply chain events: order creation, fulfillment, inventory restocking, and order expiration.

- **Data Persistence**: Manages and updates all simulation activities and entity states within a PostgreSQL database.

- **Data Export**: Exports inventory history and order fulfillment logs to CSV for analysis.

Analytical Objective
--------------------

The core analytical question this simulator aims to help answer is:

**"How many customer orders go partially or fully unfulfilled - and what inventory or supplier-related factors are driving these failures?"**

By capturing granular data on order fulfillment attempts, inventory levels, supplier performance, and item characteristics, this simulation provides a rich dataset for investigating the root causes of supply chain disruptions and inefficiencies.

Project Structure
-----------------

<pre>
├── README.md
├── METHODOLOGY.md
├── config.py
├── database.py
├── data_generator.py
├── db_loader.py
├── main.py
├── models.py
├── simulation.py
├── LICENSE.txt
├── .gitignore
├── images/
│   └── erd.png
└── sql/
    ├── create_tables.sql
    ├── clear_data.sql
    ├── drop_tables.sql
    └── integrity_tests.sql
</pre>

Setup and Installation
----------------------

To get this project up and running, follow these steps:

### 1\. Prerequisites

-   **Python 3.x**

-   **PostgreSQL**: Ensure you have a PostgreSQL server installed and running.

-   `pip`: Python package installer.

### 2\. Clone the Repository

```bash 
git clone https://github.com/your-username/supply-chain-simulator.git\
cd supply-chain-simulator
```

### 3\. Set up Python Environment

It's recommended to use a virtual environment:

```bash
python -m venv venv\
source venv/bin/activate  # On Windows: `venv\Scripts\activate`\
pip install -r requirements.txt
```

`requirements.txt` content:

```bash
psycopg2-binary\
Faker\
python-dotenv\
pandas\
matplotlib
```

### 4\. Configure Database Connection

Create a `.env` file in the root directory of the project with your PostgreSQL credentials:

```.env
DB_NAME=supply_chain_sim\
DB_USER=your_postgres_user\
DB_PASS=your_postgres_password\
DB_HOST=localhost\
DB_PORT=5432
```

-   `DB_NAME`: (Optional) Defaults to `supply_chain_sim`.

-   `DB_HOST`: (Optional) Defaults to `localhost`.

-   `DB_PORT`: (Optional) Defaults to `5432`.

### 5\. Create Database and Tables

First, ensure your PostgreSQL server is running. Then, connect to your PostgreSQL instance (e.g., using `psql`) and create the database specified in your `.env` file (e.g., `supply_chain_sim`).

Once the database is created, run the `create_tables.sql` script to set up the necessary tables:

```bash
psql -U your_postgres_user -d supply_chain_sim -f create_tables.sql
```

Running the Simulation
----------------------

After setting up the database and installing dependencies, you can run the simulation:

```bash
python main.py
```

The `main.py` script will:

1.  Connect to the PostgreSQL database.

2.  Generate synthetic data for suppliers, items, customers, and initial inventory.

3.  Load this data into the database.

4.  Run the simulation for a specified number of iterations (default: 100,000 steps).

5.  Periodically update order statuses and log inventory snapshots and fulfillment attempts.

6.  Export `inventory_history.csv` and `fulfillment_log.csv` to the project root directory upon completion.

Analysing the Data
------------------

Once the simulation completes, two CSV files will be generated:

-   `inventory_history.csv`: Contains snapshots of inventory levels over time, along with associated item and supplier weights.

-   `fulfillment_log.csv`: Details each order fulfillment attempt, including success/failure status and reasons for failure.

You can use these CSVs for your data analysis. I will be performing my own data analysis which will be included in the next commit.


Contributing
------------

Feel free to fork this repository, open issues, or submit pull requests.

License
-------

This project is open-sourced under the MIT License.