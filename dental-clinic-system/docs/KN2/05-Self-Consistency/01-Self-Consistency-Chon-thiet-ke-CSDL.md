# Prompt: Chọn thiết kế CSDL bằng Self-Consistency

## Kỹ thuật minh họa
Self-Consistency: tạo nhiều phương án suy luận độc lập, phân tích ưu/nhược điểm từng phương án rồi chọn phương án có sự đồng thuận nhất quán nhất.

## Prompt sử dụng

Bạn là kiến trúc sư phần mềm (Software Architect). Hãy giải quyết bài toán thiết kế cơ sở dữ liệu cho phân hệ Quản lý Tồn kho Vật tư Y tế (thuốc, mắc cài, implant, vật liệu trám...) trong Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI bằng cách tạo 3 phương án thiết kế độc lập, sau đó so sánh và chọn phương án tối ưu nhất.

Bối cảnh:
- Hệ thống quản lý thông tin vật tư y tế, hóa đơn/phát sinh điều trị, phiếu nhập kho, điều chuyển vật tư và lượng tồn kho thực tế.
- Cần xử lý chính xác tuyệt đối biến động tồn kho khi: Bác sĩ ghi nhận thủ thuật điều trị (tự động xuất vật tư), điều chỉnh số lượng vật tư sử dụng, hủy ca điều trị/hóa đơn, và nhập kho vật tư mới.
- Dữ liệu tồn kho cần phục vụ trực tiếp cho báo cáo kiểm kê, cảnh báo vật tư sắp hết/cận hạn sử dụng, và làm dữ liệu đầu vào cho AI dự báo nhu cầu nhập hàng.

Yêu cầu Self-Consistency:
1. Tạo **Phương án A**: Lưu số lượng tồn kho trực tiếp trong bảng `medical_supplies` (Cập nhật trực tiếp số lượng tồn kho `stock_quantity`).
2. Tạo **Phương án B**: Không lưu cột tồn kho cố định, tính toán tồn kho động hoàn toàn thông qua lịch sử xuất/nhập ở bảng `inventory_movements` (Event Sourcing).
3. Tạo **Phương án C**: Mô hình lai (Hybrid) - Lưu số lượng tồn kho hiện tại trong `medical_supplies` để truy vấn nhanh, đồng thời bắt buộc ghi vết chi tiết mọi biến động vào `inventory_movements` trong cùng một Database Transaction.
4. Đánh giá từng phương án theo các tiêu chí: Đúng nghiệp vụ y tế, Dễ triển khai/demo, Khả năng truy vết (Audit Log), Hỗ trợ báo cáo/AI, Rủi ro sai lệch dữ liệu (Race condition/Inconsistency).
5. So sánh đối chiếu và chọn phương án được nhiều tiêu chí ủng hộ nhất.

Định dạng đầu ra:
- Bảng so sánh 3 phương án theo các tiêu chí đã nêu.
- Kết luận phương án được chọn.
- Lý do kỹ thuật chọn phương án đó.
- Các test cases bắt buộc (Happy path & Edge cases) dành cho phương án được chọn.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `11-Chon-thiet-ke-csdl-nha-khoa.md` thì file kết quả phải là `11-Chon-thiet-ke-csdl-nha-khoa_ket_qua.md`.