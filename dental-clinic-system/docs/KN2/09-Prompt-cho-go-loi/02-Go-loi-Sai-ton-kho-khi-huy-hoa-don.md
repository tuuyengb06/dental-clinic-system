# Prompt: Gỡ lỗi sai tồn kho vật tư y tế khi hủy hóa đơn điều trị

## Kỹ thuật minh họa
Prompt Debugging chuyên sâu: Cung cấp đoạn mã nguồn lỗi, trạng thái dữ liệu trước/sau (State Trace) và đưa ra các ràng buộc nghiệp vụ y tế nghiêm ngặt.

## Prompt sử dụng

[Instructions]
Debug lỗi hoàn trả/phục hồi số lượng vật tư y tế (thuốc tê, mắc cài, implant, vật liệu trám...) trong kho khi hủy hóa đơn hoặc hủy ca điều trị trong Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI.

[Context]
- Khi bác sĩ hoàn tất đợt khám và xuất hóa đơn điều trị, hệ thống tự động khấu trừ vật tư y tế tiêu hao tương ứng từ kho.
- Khi lễ tân hoặc quản lý hủy hóa đơn điều trị (do bệnh nhân hủy ca, nhập sai thông tin hoặc hoàn tiền), hệ thống phải cộng hoàn trả chính xác số lượng vật tư đã khấu trừ trước đó về kho.
- Lỗi hiện tại: Khi hủy hóa đơn điều trị, hệ thống không cộng hoàn trả vật tư hoặc tiếp tục trừ thêm số lượng vật tư, khiến tồn kho bị sai lệch nghiêm trọng.

[Code liên quan]
```python
def cancel_dental_treatment_invoice(invoice):
    """
    Hủy hóa đơn điều trị nha khoa và hoàn trả vật tư tiêu hao về kho.
    """
    invoice.status = "cancelled"
    for item in invoice.treatment_supply_items:
        medical_supply = item.medical_supply
        # Thực hiện cập nhật tồn kho vật tư y tế
        medical_supply.stock_quantity -= item.used_quantity
    return invoice