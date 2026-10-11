# Prompt: Gỡ lỗi AttributeError trong dữ liệu hóa đơn nha khoa

## Kỹ thuật minh họa

Prompt debugging: Code + Input gây lỗi + Error Message + Output Format.

## Prompt sử dụng

[Instructions]

Phân tích lỗi trong đoạn code Python dưới đây. Xác định nguyên nhân gốc rễ, đề xuất cách sửa nhỏ nhất và viết test case phòng tránh lỗi bằng `pytest`.

[Code]

```python
def calculate_dental_invoice_total(items):
    total = 0
    for item in items:
        total += item.quantity * item.unit_price
    return total
```

[Input gây lỗi]

```python
from dataclasses import dataclass


@dataclass
class DentalServiceItem:
    service_name: str
    quantity: int
    unit_price: int


items = [
    DentalServiceItem(
        service_name="Trám răng Composite",
        quantity=2,
        unit_price=350000,
    ),
    None,
    DentalServiceItem(
        service_name="Chụp phim X-quang Panorama",
        quantity=1,
        unit_price=120000,
    ),
]

calculate_dental_invoice_total(items)
```

[Error Message]

```text
AttributeError: 'NoneType' object has no attribute 'quantity'
```

[Context]

- Hàm được dùng trong hệ thống quản lý nha khoa để tính tổng hóa đơn dịch vụ.
- Danh sách hạng mục có thể được tạo từ dữ liệu nhập vào hoặc dữ liệu do một thành phần khác của hệ thống cung cấp.
- Không được bỏ qua hạng mục `None` một cách im lặng vì điều đó có thể làm sai tổng tiền trên hóa đơn.
- Khi dữ liệu hóa đơn không hợp lệ, hệ thống cần báo lỗi rõ ràng để người gọi có thể xử lý.

[Output Format]

1. Nguyên nhân gốc rễ.
2. Code đã sửa.
3. Giải thích vì sao cách sửa phù hợp với hệ thống quản lý nha khoa.
4. 3 test case với `pytest`, bao gồm:
   - Tính đúng tổng tiền với các hạng mục hợp lệ.
   - Báo lỗi rõ ràng khi danh sách có hạng mục `None`, không bỏ qua hạng mục.
   - Xử lý danh sách rỗng theo hành vi phù hợp.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
