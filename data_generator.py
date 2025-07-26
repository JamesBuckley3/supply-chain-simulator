"""
data_generator.py

This module uses Faker to create randomised, but realistic, data for suppliers, items, and customers.
It also maps suppliers to items by matching product categories.
"""

import random
from faker import Faker
from datetime import datetime
from models import *


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

    def generate_suppliers(self):
        """
        Generates 10 suppliers, each assigned to one of 5 predefined categories.

        Returns:
            set[str]: A set of used categories.
        """
        categories = ["Electronics", "Clothing", "Food", "Medical", "Hardware"]
        used_categories = set()

        for i in range(10):
            category = categories[i % len(categories)]
            used_categories.add(category)
            self.suppliers[i] = Supplier(
                id=i,
                name=self.fake.company(),
                category=category,
                max_quantity=40,
                failure_rate=round(random.uniform(0.01, 0.05), 2),
                fulfillment_weight=round(random.uniform(0.1, 9.0), 2),
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
                failure_rate=round(random.uniform(0.01, 0.05), 2),
                restock_weight=round(random.uniform(0.1, 9.0), 2),
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
        return (
            self.suppliers,
            self.items,
            self.customers,
            self.supplier_items,
            self.sim_time,
        )
