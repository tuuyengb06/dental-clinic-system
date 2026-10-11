from decimal import Decimal, InvalidOperation
from typing import Any


def calculate_dental_invoice_total(
    items: list[dict[str, Any]],
    discount_amount: int | float = 0,
) -> Decimal:
    """Calculate the net total for a dental service invoice.

    Args:
        items: Invoice lines containing a positive integer ``quantity`` and a
            non-negative numeric ``unit_price``.
        discount_amount: A non-negative discount amount.

    Returns:
        The net invoice total as ``Decimal``; it is never less than zero.

    Raises:
        TypeError: If an item or numeric value has an unsupported type.
        ValueError: If a required field is missing, a value is invalid, or
            a quantity/price/discount is outside the allowed range.
    """
    if isinstance(discount_amount, bool) or not isinstance(discount_amount, (int, float)):
        raise TypeError("discount_amount must be an int or float")
    if discount_amount < 0:
        raise ValueError("discount_amount must not be negative")

    try:
        discount = Decimal(str(discount_amount))
        if not discount.is_finite():
            raise ValueError("discount_amount must be finite")
        total = Decimal("0")

        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise TypeError(f"items[{index}] must be a dict")
            if "quantity" not in item or "unit_price" not in item:
                raise ValueError(f"items[{index}] must contain quantity and unit_price")

            quantity = item["quantity"]
            unit_price = item["unit_price"]
            if isinstance(quantity, bool) or not isinstance(quantity, int):
                raise TypeError(f"items[{index}].quantity must be an integer")
            if quantity <= 0:
                raise ValueError(f"items[{index}].quantity must be greater than zero")
            if isinstance(unit_price, bool) or not isinstance(unit_price, (int, float)):
                raise TypeError(f"items[{index}].unit_price must be an int or float")
            if unit_price < 0:
                raise ValueError(f"items[{index}].unit_price must not be negative")

            price = Decimal(str(unit_price))
            if not price.is_finite():
                raise ValueError(f"items[{index}].unit_price must be finite")
            total += quantity * price
    except InvalidOperation as exc:
        raise ValueError("monetary values must be finite numbers") from exc

    return max(total - discount, Decimal("0"))
