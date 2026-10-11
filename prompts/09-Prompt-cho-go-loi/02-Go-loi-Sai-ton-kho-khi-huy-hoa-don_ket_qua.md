# Gỡ lỗi tồn kho khi hủy hóa đơn

## 1. Nguyên nhân lỗi

Code hiện tại giảm tồn kho thêm một lần khi hủy hóa đơn:

```python
item.stock_quantity -= usage.quantity
```

Trong ví dụ, ghi nhận usage 2 đã làm tồn từ 12 xuống 10; khi hủy trong trường hợp phải đảo usage, code lại trừ 2 nên tồn thành 8 thay vì cộng lại về 12.

## 2. Code đã sửa

> Ví dụ giả định mỗi usage có cờ `reversed`, treatment có `performed`, và thao tác được gọi trong một transaction DB. Tên trường cần điều chỉnh theo schema thật.

```python
def cancel_invoice(invoice, session):
    if invoice.status == "cancelled":
        return invoice

    with session.begin():
        if invoice.status not in {"draft", "unpaid", "paid"}:
            raise ValueError("Invoice cannot be cancelled from its current status")

        invoice.status = "cancelled"
        for usage in invoice.material_usages:
            if usage.reversed:
                continue
            if invoice.treatment_performed:
                # Thanh toán/hóa đơn bị hủy không làm vật tư đã tiêu hao quay lại kho.
                continue

            usage.inventory_item.stock_quantity += usage.quantity
            usage.reversed = True

    return invoice
```

Trong hệ thống thật, dùng một bản ghi reversal có khóa duy nhất theo usage, thay vì chỉ dựa vào cờ nếu nhiều worker có thể xử lý đồng thời. Thay đổi trạng thái, bản ghi reversal và tồn kho phải cùng transaction. Hủy hóa đơn chưa đồng nghĩa tự động hoàn tiền; đó là nghiệp vụ riêng.

## 3. Test case tối thiểu

```python
from dataclasses import dataclass


@dataclass
class InventoryItem:
    stock_quantity: int


@dataclass
class Usage:
    quantity: int
    inventory_item: InventoryItem
    reversed: bool = False


@dataclass
class Invoice:
    status: str
    treatment_performed: bool
    material_usages: list[Usage]


from contextlib import nullcontext
import pytest


class FakeSession:
    def begin(self):
        return nullcontext()


@pytest.fixture
def fake_session():
    return FakeSession()


def test_cancel_before_treatment_reverses_usage_once(fake_session):
    item = InventoryItem(stock_quantity=10)
    invoice = Invoice("unpaid", False, [Usage(2, item)])

    cancel_invoice(invoice, fake_session)
    assert invoice.status == "cancelled"
    assert item.stock_quantity == 12
    assert invoice.material_usages[0].reversed is True

    cancel_invoice(invoice, fake_session)
    assert item.stock_quantity == 12


def test_cancel_after_treatment_does_not_return_consumed_material(fake_session):
    item = InventoryItem(stock_quantity=10)
    invoice = Invoice("paid", True, [Usage(2, item)])

    cancel_invoice(invoice, fake_session)
    assert invoice.status == "cancelled"
    assert item.stock_quantity == 10
```

`nullcontext` chỉ phục vụ unit test; test tích hợp cần transaction thật để xác nhận rollback. Đây là skeleton; chưa tuyên bố đã chạy.

## 4. Lưu ý nghiệp vụ

- Hủy hóa đơn chưa thanh toán: trạng thái hóa đơn và việc đảo usage phải dựa trên việc điều trị đã diễn ra chưa.
- Hủy hóa đơn đã thanh toán: cần quy trình hoàn/điều chỉnh thanh toán riêng; không mặc định hoàn vật tư.
- Chỉ đảo usage nếu xác nhận dịch vụ chưa thực hiện và vật tư chưa tiêu hao/được phép hoàn.
- Cần xác nhận trạng thái hợp lệ, quyền hủy, xử lý concurrency và audit với phòng khám.
