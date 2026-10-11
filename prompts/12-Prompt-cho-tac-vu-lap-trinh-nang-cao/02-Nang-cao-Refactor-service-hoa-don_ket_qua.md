# Refactor service hóa đơn nha khoa

> Đầu vào code trong prompt là placeholder `{{paste_dental_invoice_service_code_here}}`, không có source thật để review hoặc tạo bản refactor tương thích. Vì vậy phần code dưới đây là skeleton tham khảo minh họa việc tách trách nhiệm, không phải bản sửa drop-in.

## 1. Code smell có thể đánh giá khi có source

Chưa thể xác nhận code smell cụ thể khi không có code. Các rủi ro cần rà soát:

- Tính tổng hóa đơn, validate, cập nhật tồn và hủy hóa đơn nằm chung một hàm.
- Khi sửa usage trừ toàn bộ quantity mới thay vì delta `new-old`.
- Tồn kho và usage cập nhật không cùng transaction.
- Hủy lặp làm đảo movement nhiều lần.
- Hủy hóa đơn luôn hoàn vật tư dù điều trị đã thực hiện/tiêu hao.
- Log hoặc AI call trong module hóa đơn đưa dữ liệu bệnh nhân không cần thiết ra ngoài.

## 2. Code refactor tham khảo

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class InvoiceLine:
    quantity: int
    unit_price: int


@dataclass
class MaterialUsage:
    inventory_item_id: int
    quantity: int
    reversed: bool = False


class InvoiceRepository(Protocol):
    def transaction(self): ...
    def get_stock(self, item_id: int) -> int: ...
    def adjust_stock(self, item_id: int, delta: int) -> None: ...
    def save_usage(self, usage: MaterialUsage) -> None: ...
    def add_movement(self, item_id: int, delta: int, operation_key: str) -> None: ...
    def has_movement(self, operation_key: str) -> bool: ...


class InvoiceValidationError(ValueError):
    pass


def calculate_total(lines: list[InvoiceLine], discount: int = 0) -> int:
    if discount < 0:
        raise InvoiceValidationError("discount must not be negative")
    total = 0
    for line in lines:
        if line.quantity <= 0 or line.unit_price < 0:
            raise InvoiceValidationError("invalid invoice line")
        total += line.quantity * line.unit_price
    return max(total - discount, 0)


def validate_usage_quantity(quantity: int) -> None:
    if quantity <= 0:
        raise InvoiceValidationError("usage quantity must be greater than zero")


def update_material_usage(
    repo: InvoiceRepository,
    usage: MaterialUsage,
    new_quantity: int,
    operation_key: str,
) -> None:
    validate_usage_quantity(new_quantity)
    if usage.reversed:
        raise InvoiceValidationError("cannot edit a reversed usage")
    delta = new_quantity - usage.quantity
    with repo.transaction():
        if repo.has_movement(operation_key):
            return
        if delta > 0:
            if repo.get_stock(usage.inventory_item_id) < delta:
                raise InvoiceValidationError("insufficient inventory")
            repo.adjust_stock(usage.inventory_item_id, -delta)
            repo.add_movement(usage.inventory_item_id, -delta, operation_key)
        elif delta < 0:
            repo.adjust_stock(usage.inventory_item_id, -delta)
            repo.add_movement(usage.inventory_item_id, -delta, operation_key)
        usage.quantity = new_quantity
        repo.save_usage(usage)


def reverse_material_usage(
    repo: InvoiceRepository,
    usage: MaterialUsage,
    *,
    treatment_performed: bool,
    reversal_allowed: bool,
    operation_key: str,
) -> bool:
    """Reverse a not-yet-performed usage once, when business rules allow."""
    if treatment_performed or not reversal_allowed or usage.reversed:
        return False
    with repo.transaction():
        if repo.has_movement(operation_key):
            return False
        repo.adjust_stock(usage.inventory_item_id, usage.quantity)
        repo.add_movement(usage.inventory_item_id, usage.quantity, operation_key)
        usage.reversed = True
        repo.save_usage(usage)
    return True
```

Repository thực tế phải cung cấp transaction, khóa/idempotency và cách lưu cùng rollback. `operation_key` phải là duy nhất theo thao tác nghiệp vụ.

## 3. Thay đổi và lý do

- Tách `calculate_total` khỏi xử lý vật tư để dễ unit-test và tránh thay đổi tồn khi chỉ tính hóa đơn.
- Tách validation số lượng; lỗi được báo rõ.
- Update tồn theo delta: chỉ trừ phần tăng, cộng lại phần giảm, không đổi khi giữ nguyên.
- Transaction gom cập nhật tồn, ledger và usage; implementation phải đảm bảo rollback.
- Module không gọi AI; nội dung AI nằm ngoài invoice service.
- Không log patient data; chỉ dùng ID nội bộ cần thiết theo quyền.

## 4. Giả định/điểm cần xác nhận

- Repository interface, schema, quantity type và transaction manager chưa được cung cấp.
- `reverse_material_usage` là mẫu: caller phải xác định `treatment_performed` và `reversal_allowed` từ nguồn nghiệp vụ có thẩm quyền.
- Tồn âm, nhập kho, hủy/hoàn tiền, vật tư đã mở và đơn vị lẻ cần được xác nhận.
- Khi đồng thời sửa cùng usage, cần locking/version check ở tầng DB.

## 5. Test case cần chạy

1. Tính hóa đơn hợp lệ; từ chối quantity ≤ 0, unit_price < 0, discount < 0.
2. Tồn 12; ghi nhận dùng 2; sửa lên 3 chỉ trừ thêm 1.
3. Sửa từ 3 xuống 2 cộng lại 1; giữ nguyên không phát movement.
4. Tăng vượt tồn bị từ chối và không cập nhật usage/tồn.
5. Hủy usage được phép chỉ đảo một lần; request lặp không đổi tồn thêm.
6. Hủy hóa đơn sau điều trị đã thực hiện không hoàn vật tư đã tiêu hao.
7. Inject lỗi giữa transaction: tồn, usage, ledger cùng rollback.
8. Hai cập nhật đồng thời không vượt tồn hoặc tạo movement trùng.

Chỉ có thể xác nhận test pass sau khi thay skeleton theo repository và thực sự chạy test.
