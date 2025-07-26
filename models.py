"""
models.py

This module defines structured representations of core entities used in the simulation:
- Supplier: Provides inventory and has limits, reliability, and priority.
- Item: Product that can be ordered and restocked.
- Customer: Entity that places orders within a specific region.
"""

from dataclasses import dataclass


@dataclass
class Supplier:
    """Represents a supplier who provides inventory for one item category.

    Attributes:
        id (int): Unique supplier ID.
        name (str): Name of the supplier.
        category (str): Product category this supplier serves (e.g., "Electronics").
        max_quantity (int): Max inventory this supplier can restock.
        failure_rate (float): Likelihood that the supplier fails to fulfill an item.
        fulfillment_weight (float): Probability weight used when selecting this supplier for fulfillment.
    """

    id: int
    name: str
    category: str
    max_quantity: int
    failure_rate: float
    fulfillment_weight: float


@dataclass
class Item:
    """Represents an item that can be ordered by customers.

    Attributes:
        id (int): Unique item ID.
        name (str): Name of the item.
        category (str): Product category (e.g., "Electronics").
        unit_price (float): Price per unit.
        failure_rate (float): Likelihood that an item-related issue causes fulfillment failure.
        restock_weight (float): Probability weight used when deciding which items to restock.
    """

    id: int
    name: str
    category: str
    unit_price: float
    failure_rate: float
    restock_weight: float


@dataclass
class Customer:
    """Represents a customer who places orders.

    Attributes:
        id (int): Unique customer ID.
        name (str): Name of the customer.
        region (str): Geographic region of the customer (e.g., "North").
    """

    id: int
    name: str
    region: str


__all__ = ["Supplier", "Item", "Customer"]
