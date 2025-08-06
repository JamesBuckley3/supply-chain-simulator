"""
data_generator.py

This module uses Faker to create randomised, but realistic, data for suppliers, items, and customers.
It also maps suppliers to items by matching product categories.
"""

import random
from faker import Faker
from datetime import datetime
from models import *
import json
import os


class DataGenerator:
    """
    Generates mock data for a supply chain simulation.

    Attributes:
        suppliers (dict[int, Supplier]): Mapping of supplier IDs to Supplier objects.
        items (dict[int, Item]): Mapping of item IDs to Item objects.
        customers (dict[int, Customer]): Mapping of customer IDs to Customer objects.
        supplier_items (dict[int, list[int]]): Maps supplier IDs to item IDs they can supply.
        sim_time (datetime): Starting timestamp for the simulation.
        fake (Faker): Faker instance for generating random names and words.
    """

    def __init__(self):
        """
        Initialises the data generator.

        Args:
            sim_days_ago (int, optional): Number of days before today to set as the simulation start. Defaults to 14.
        """
        self.suppliers = {}
        self.items = {}
        self.customers = {}
        self.supplier_items = {}
        self.sim_time = datetime.now()
        self.fake = Faker()
        self.seed = 42
        random.seed(self.seed)

    def generate_suppliers(self):
        """
        Generates 10 suppliers, each assigned to one of 5 predefined categories.

        Returns:
            set[str]: A set of used categories.
        """
        categories = ["Electronics", "Clothing", "Food", "Medical", "Hardware"]
        used_categories = set()

        for i in range(1, 11):
            category = categories[i % len(categories)]
            used_categories.add(category)
            self.suppliers[i] = Supplier(
                id=i,
                name=self.fake.company(),
                category=category,
                max_quantity=40,
                failure_rate=round(random.uniform(0.01, 0.5), 2),
                fulfillment_weight=round(random.uniform(0.1, 6.0), 2),
            )

        return used_categories

    def generate_items(self, used_categories):
        """
        Generates 50 items distributed across the given categories.

        Args:
            used_categories (set[str]): Categories to assign to items.
        """
        for i in range(1, 51):
            category = random.choice(list(used_categories))
            self.items[i] = Item(
                id=i,
                name=self.fake.unique.word().title(),
                category=category,
                unit_price=round(random.uniform(5.00, 50.00), 2),
                failure_rate=round(random.uniform(0.01, 0.5), 2),
                restock_weight=round(random.uniform(0.1, 6.0), 2),
            )

    def generate_customers(self):
        """
        Generates 200 customers, randomly assigning them to one of four regions.
        """
        regions = ["North", "South", "East", "West"]
        for i in range(1, 201):
            self.customers[i] = Customer(
                id=i, name=self.fake.name(), region=random.choice(regions)
            )

    def map_supplier_items(self):
        """
        Creates a mapping between suppliers and the item IDs they can supply,
        based on matching categories.
        """
        self.supplier_items = {sid: [] for sid in self.suppliers}
        for item in self.items.values():
            for sid, supplier in self.suppliers.items():
                if item.category == supplier.category:
                    self.supplier_items[sid].append(item.id)

    def export_config(self, output_dir="data", filename="simulation_config.json"):
        """
        Exports the current simulation configuration (suppliers, items, and seed) to a JSON file.

        This method creates the specified output directory if it doesn't exist and
        then writes the simulation's initial setup data, including details about
        suppliers, items, and the random seed (if available), into a formatted
        JSON file.

        Args:
            output_dir (str): The directory where the configuration file will be saved.
                            Defaults to "data".
            filename (str): The name of the JSON file.
                            Defaults to "simulation_config.json".
        """
        os.makedirs(output_dir, exist_ok=True)
        config_path = os.path.join(output_dir, filename)

        config_data = {
            "suppliers": {
                s.id: {
                    "name": s.name,
                    "category": s.category,
                    "failure_rate": s.failure_rate,
                    "fulfillment_weight": s.fulfillment_weight,
                }
                for s in self.suppliers.values()
            },
            "items": {
                i.id: {
                    "name": i.name,
                    "category": i.category,
                    "unit_price": i.unit_price,
                    "failure_rate": i.failure_rate,
                    "restock_weight": i.restock_weight,
                }
                for i in self.items.values()
            },
            "config": {
                "seed": self.seed if hasattr(self, "seed") else None,
            },
        }

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)

        print(f"Simulation config exported to {config_path}")

    def generate_all(self):
        """
        Runs the full data generation process.

        Returns:
            tuple:
                dict[int, Supplier]: All generated suppliers.
                dict[int, Item]: All generated items.
                dict[int, Customer]: All generated customers.
                dict[int, list[int]]: Supplier-to-item mapping.
                datetime: Simulation start timestamp.
        """
        used_categories = self.generate_suppliers()
        self.generate_items(used_categories)
        self.generate_customers()
        self.map_supplier_items()
        self.export_config()
        return (
            self.suppliers,
            self.items,
            self.customers,
            self.supplier_items,
            self.sim_time,
        )
