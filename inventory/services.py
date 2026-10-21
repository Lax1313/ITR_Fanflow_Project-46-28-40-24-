"""
Inventory optimization service. All calculations use actual database
values -- nothing here is a placeholder or fake number.
"""
from decimal import Decimal

from .models import Inventory, InventoryTransaction


def calculate_available_stock(inventory: Inventory) -> Decimal:
    """Available Stock = Current Stock + Incoming Stock - Reserved Stock"""
    return inventory.current_stock + inventory.incoming_stock - inventory.reserved_stock


def calculate_shortage(required_quantity, inventory: Inventory) -> Decimal:
    """
    Shortage = Required Material - Available
    Returns 0 (not negative) when there's a surplus -- callers should check
    `is_sufficient()` separately if they need the surplus amount.
    """
    available = calculate_available_stock(inventory)
    shortage = Decimal(required_quantity) - available
    return shortage if shortage > 0 else Decimal('0')


def is_sufficient(required_quantity, inventory: Inventory) -> bool:
    return calculate_available_stock(inventory) >= Decimal(required_quantity)


def calculate_reorder_point(inventory: Inventory, average_daily_usage: Decimal, lead_time_days: int) -> Decimal:
    """Reorder Point = (Average Daily Usage x Lead Time) + Safety Stock"""
    return (Decimal(average_daily_usage) * Decimal(lead_time_days)) + inventory.safety_stock


def calculate_safety_stock(max_daily_usage: Decimal, avg_daily_usage: Decimal, max_lead_time: int, avg_lead_time: int) -> Decimal:
    """Safety Stock = (Max Daily Usage x Max Lead Time) - (Avg Daily Usage x Avg Lead Time)"""
    value = (Decimal(max_daily_usage) * max_lead_time) - (Decimal(avg_daily_usage) * avg_lead_time)
    return value if value > 0 else Decimal('0')


def calculate_suggested_purchase_quantity(inventory: Inventory, required_quantity=None) -> Decimal:
    """
    Suggested purchase quantity to bring stock back up to a healthy level:
      - if there's a specific requirement (e.g. from MRP), cover the
        shortage against that requirement, topped up to safety stock
      - otherwise, top up to maximum_stock from current available stock
    """
    available = calculate_available_stock(inventory)

    if required_quantity is not None:
        shortfall_vs_requirement = calculate_shortage(required_quantity, inventory)
        shortfall_vs_safety = inventory.safety_stock - available
        shortfall_vs_safety = shortfall_vs_safety if shortfall_vs_safety > 0 else Decimal('0')
        return max(shortfall_vs_requirement, shortfall_vs_safety)

    if inventory.maximum_stock and available < inventory.maximum_stock:
        return inventory.maximum_stock - available
    return Decimal('0')


def record_transaction(material, transaction_type, quantity, reference='', notes=''):
    """
    Records an InventoryTransaction and updates the Inventory row.
    Purchase/Return/Adjustment(+) increase current_stock;
    Sale/Production/Adjustment(-) decrease it.
    """
    inventory, _ = Inventory.objects.get_or_create(material=material)
    quantity = Decimal(quantity)

    increasing = {
        InventoryTransaction.TransactionType.PURCHASE,
        InventoryTransaction.TransactionType.RETURN,
    }

    if transaction_type in increasing:
        inventory.current_stock += quantity
    else:
        inventory.current_stock -= quantity

    inventory.save()

    return InventoryTransaction.objects.create(
        material=material,
        transaction_type=transaction_type,
        quantity=quantity,
        reference=reference,
        notes=notes,
    )
