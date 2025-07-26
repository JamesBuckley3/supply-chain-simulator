"""
main.py

This script orchestrates the following workflow:
1. Connects to the PostgreSQL database.
2. Generates synthetic suppliers, items, customers, and inventory data.
3. Loads the data into the database.
4. Runs the simulation over a specified number of iterations.
5. Outputs logs and performance metrics.

Modules:
    - database: Provides database connection functionality.
    - data_generator: Generates synthetic simulation data.
    - db_loader: Loads generated data into the database.
    - simulation: Contains the simulation logic and run loop.
"""

import time
from database import get_connection
from data_generator import DataGenerator
from db_loader import SimulationDBLoader
from simulation import Simulation


def main():
    """
    Executes the full supply chain simulation pipeline.

    Workflow:
        - Establish database connection.
        - Generate data for suppliers, items, customers, and inventory mapping.
        - Load the data into relevant tables.
        - Run the simulation for a specified number of iterations.
        - Close the database connection and print runtime.
    """
    start = time.time()
    conn = get_connection()

    # Step 1: Generate data
    generator = DataGenerator()
    suppliers, items, customers, supplier_items, sim_time = generator.generate_all()

    # Step 2: Load into database
    loader = SimulationDBLoader(conn)
    loader.populate_tables(suppliers, items, customers, sim_time)

    # Step 3: Run simulation
    sim = Simulation(conn, generator)
    sim.run(iterations=100000)

    # Step 4: Clean up
    conn.close()
    print(f"Simulation took {time.time() - start:.2f} seconds")


if __name__ == "__main__":
    main()
