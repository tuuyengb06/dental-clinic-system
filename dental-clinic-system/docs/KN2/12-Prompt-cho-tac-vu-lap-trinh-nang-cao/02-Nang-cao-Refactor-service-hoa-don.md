# Prompt: Refactor service Hồ sơ bệnh án & Đặt lịch khám nha khoa

## Kỹ thuật minh họa
Prompt cho tác vụ lập trình nâng cao: Phân tích code smell, tách biệt trách nhiệm (Separation of Concerns), đảm bảo tính toàn vẹn dữ liệu y tế và tối ưu mã nguồn cho dễUnit Test.

## Prompt sử dụng

[Instructions]
Phân tích và refactor service xử lý Hồ sơ Bệnh án & Đặt lịch khám nha khoa (`PatientTreatmentService`) dưới đây để tăng tính dễ bảo trì, đảm bảo tính nhất quán dữ liệu y tế và dễ viết Unit Test.

[Context]
- Hệ thống quản lý nha khoa cần xử lý các luồng: Đặt lịch hẹn khám, tạo/cập nhật hồ sơ bệnh án (sơ đồ răng, chỉ định thủ thuật), trừ tồn kho vật tư y tế (thuốc tê, mắc cài, trụ implant...) và tính tổng chi phí thanh toán/trả góp.
- Quản lý vật tư y tế và toàn vẹn sơ đồ răng (Dental Chart) là nghiệp vụ cốt lõi, không được phép xảy ra sai sót hoặc lệch dữ liệu (Race condition).
- Giữ nguyên các quy tắc nghiệp vụ nha khoa hiện tại, ngoại trừ các điểm được yêu cầu tối ưu để giảm lỗi.

[Code]
```python
{{paste_patient_treatment_service_code_here}}