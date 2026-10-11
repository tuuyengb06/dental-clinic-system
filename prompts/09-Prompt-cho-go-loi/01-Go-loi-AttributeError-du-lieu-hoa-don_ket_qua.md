# Gỡ lỗi `AttributeError` trong dữ liệu hóa đơn

## 1. Nguyên nhân gốc rễ

Vòng lặp giả định mọi phần tử trong `items` đều là một `DentalServiceItem`. Danh sách đầu vào có phần tử `None`, nên biểu thức `item.quantity` gây `AttributeError`. Bỏ qua `None` âm thầm không an toàn vì hóa đơn có thể bị tính thiếu; cần từ chối toàn bộ dữ liệu không hợp lệ bằng lỗi có chỉ số phần tử.

## 2. Code đã sửa

```python
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class DentalServiceItem:
    service_name: str
    quantity: int
    unit_price: int


def calculate_dental_invoice_total(
    items: Sequence[DentalServiceItem],
) -> int:
    """Tính tổng tiền các hạng mục dịch vụ nha khoa hợp lệ."""
    if items is None:
        raise TypeError("items must be a sequence of DentalServiceItem")

    total = 0
    for index, item in enumerate(items):
        if not isinstance(item, DentalServiceItem):
            raise ValueError(f"items[{index}] must be a DentalServiceItem")
        if item.quantity <= 0:
            raise ValueError(f"items[{index}].quantity must be greater than zero")
        if item.unit_price < 0:
            raise ValueError(f"items[{index}].unit_price must not be negative")
        total += item.quantity * item.unit_price
    return total
```

## 3. Vì sao phù hợp

- Báo lỗi sớm, xác định vị trí phần tử không hợp lệ thay vì bỏ qua và tạo sai tổng.
- Kiểm tra số lượng dương và đơn giá không âm trước khi tính.
- Danh sách rỗng cho tổng 0, là phép cộng không có hạng mục.
- Không phụ thuộc hoặc ghi dữ liệu bệnh nhân.

## 4. Pytest

```python
import pytest


def test_calculates_total_for_valid_items() -> None:
    items = [
        DentalServiceItem("Trám răng Composite", 2, 350_000),
        DentalServiceItem("X-quang Panorama", 1, 120_000),
    ]
    assert calculate_dental_invoice_total(items) == 820_000


def test_rejects_none_item_instead_of_ignoring_it() -> None:
    items = [DentalServiceItem("Trám răng Composite", 2, 350_000), None]
    with pytest.raises(ValueError, match=r"items\[1\]"):
        calculate_dental_invoice_total(items)  # type: ignore[list-item]


def test_empty_items_return_zero() -> None:
    assert calculate_dental_invoice_total([]) == 0
```
