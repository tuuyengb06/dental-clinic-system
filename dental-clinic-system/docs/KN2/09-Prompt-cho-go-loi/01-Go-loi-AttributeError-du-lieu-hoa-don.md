# Prompt: Gỡ lỗi AttributeError trong dữ liệu chi phí điều trị nha khoa

## Kỹ thuật minh họa
Prompt Debugging chuyên sâu: Kết hợp Code + Input dữ liệu lỗi thực tế + Stack Trace/Error Message + Ràng buộc nghiệp vụ y tế + Định dạng đầu ra chặt chẽ.

## Prompt sử dụng

[Instructions]
Phân tích và gỡ lỗi đoạn code Python dưới đây trong Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI. Xác định nguyên nhân gốc rễ, đề xuất phương án sửa lỗi nhỏ nhất (minimal patch) tuân thủ quy tắc toàn vẹn dữ liệu y tế, và viết các test cases kiểm thử tự động phòng ngừa tái diễn.

[Code]
```python
def calculate_dental_treatment_cost(treatment_items):
    total_cost = 0
    for item in treatment_items:
        total_cost += item.quantity * item.unit_price
    return total_cost