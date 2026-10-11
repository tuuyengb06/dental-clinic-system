# Test `pytest` cho hóa đơn và tồn kho

> Ví dụ unit-test độc lập bằng object giả lập, không kết nối CSDL. Quy tắc minh họa: VND nguyên đồng; vật tư chỉ hoàn khi usage được đảo trước khi điều trị thực hiện; hủy hóa đơn không tự hoàn vật tư đã tiêu hao.

```python
from dataclasses import dataclass, field
import pytest


@dataclass
class InventoryItem:
    name: str
    stock_quantity: int


@dataclass
class MaterialUsage:
    item: InventoryItem
    quantity: int
    reversed: bool = False


@dataclass
class Invoice:
    lines: list[tuple[int, int]]
    status: str = "unpaid"
    treatment_performed: bool = False
    usages: list[MaterialUsage] = field(default_factory=list)


def invoice_total(lines: list[tuple[int, int]]) -> int:
    if any(quantity <= 0 or price < 0 for quantity, price in lines):
        raise ValueError("invalid invoice line")
    return sum(quantity * price for quantity, price in lines)


def record_usage(item: InventoryItem, quantity: int) -> MaterialUsage:
    if quantity <= 0:
        raise ValueError("quantity must be greater than zero")
    if quantity > item.stock_quantity:
        raise ValueError("insufficient stock")
    item.stock_quantity -= quantity
    return MaterialUsage(item, quantity)


def update_usage(usage: MaterialUsage, new_quantity: int) -> None:
    if usage.reversed:
        raise ValueError("usage has already been reversed")
    if new_quantity <= 0:
        raise ValueError("quantity must be greater than zero")
    delta = new_quantity - usage.quantity
    if delta > usage.item.stock_quantity:
        raise ValueError("insufficient stock")
    usage.item.stock_quantity -= delta
    usage.quantity = new_quantity


def cancel_invoice(invoice: Invoice) -> None:
    if invoice.status == "cancelled":
        return
    invoice.status = "cancelled"
    if not invoice.treatment_performed:
        for usage in invoice.usages:
            if not usage.reversed:
                usage.item.stock_quantity += usage.quantity
                usage.reversed = True


@pytest.fixture
def sample_data():
    composite = InventoryItem("Composite", 12)
    return {
        "composite": composite,
        "service_price": 350_000,
    }


def test_create_valid_dental_invoice(sample_data):
    invoice = Invoice(lines=[(2, sample_data["service_price"])])
    assert invoice_total(invoice.lines) == 700_000
    assert invoice.status == "unpaid"
    assert sample_data["composite"].stock_quantity == 12


def test_reject_material_usage_above_stock(sample_data):
    item = sample_data["composite"]
    with pytest.raises(ValueError, match="insufficient stock"):
        record_usage(item, 13)
    assert item.stock_quantity == 12


@pytest.mark.parametrize(
    ("new_quantity", "expected_stock"),
    [(3, 9), (1, 11)],
)
def test_update_usage_applies_only_quantity_delta(sample_data, new_quantity, expected_stock):
    item = sample_data["composite"]
    usage = record_usage(item, 2)  # tồn 10
    update_usage(usage, new_quantity)
    assert usage.quantity == new_quantity
    assert item.stock_quantity == expected_stock


def test_cancel_usage_before_treatment_restores_stock_once(sample_data):
    item = sample_data["composite"]
    usage = record_usage(item, 2)
    invoice = Invoice(lines=[(2, 350_000)], usages=[usage])

    cancel_invoice(invoice)
    assert item.stock_quantity == 12
    assert usage.reversed is True

    cancel_invoice(invoice)
    assert item.stock_quantity == 12


def test_cancel_invoice_does_not_restore_consumed_material(sample_data):
    item = sample_data["composite"]
    usage = record_usage(item, 2)
    invoice = Invoice(
        lines=[(2, 350_000)],
        status="paid",
        treatment_performed=True,
        usages=[usage],
    )

    cancel_invoice(invoice)
    assert invoice.status == "cancelled"
    assert item.stock_quantity == 10
    assert usage.reversed is False
```

Trong ứng dụng thật, tồn kho và usage phải cập nhật nguyên tử trong transaction; test trên chỉ minh họa logic domain. Không trừ kho chỉ vì hóa đơn thanh toán. Nếu DB dùng transaction/concurrency, bổ sung test tích hợp rollback và chống request lặp.
