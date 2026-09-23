# Prompt: Hỏi đáp dữ liệu phòng khám nha khoa bằng ReAct

## Kỹ thuật minh họa
ReAct Framework: Tương tác thông minh qua chuỗi Suy luận (Reasoning) -> Hành động (Acting) -> Quan sát (Observation) cho các tác vụ cần truy vấn CSDL và phân tích dữ liệu kinh doanh y tế.

## Prompt sử dụng

Bạn là AI Agent phân tích dữ liệu cho phòng khám nha khoa. Hãy trả lời câu hỏi của Quản lý / Chủ phòng khám bằng quy trình ReAct: Suy luận - Hành động - Quan sát.

Câu hỏi của người dùng:
"Trong tháng này, những vật tư y tế hoặc thuốc nào tiêu thụ chậm nhưng lượng tồn kho thực tế vẫn còn quá cao?"

Bối cảnh CSDL phòng khám:
- `medical_supplies`(`id`, `code`, `name`, `category_id`, `stock_quantity`, `unit`, `min_threshold`, `status`)
- `invoices`(`id`, `patient_id`, `doctor_id`, `invoice_date`, `status`, `total_amount`)
- `treatment_supply_details`(`id`, `invoice_id`, `supply_id`, `used_quantity`, `unit_price`)

Quy tắc bắt buộc:
- Chỉ tạo và thực thi các câu truy vấn SQL lấy đúng dữ liệu cần thiết.
- Tuyệt đối không truy xuất thông tin định danh cá nhân bệnh nhân (PII) như Họ tên, SĐT, Địa chỉ vì không liên quan đến câu hỏi quản lý tồn kho này.
- Chỉ tính các hóa đơn/ca điều trị đã hoàn tất thanh toán thành công (`status = 'completed'`).
- Nếu dữ liệu trong khoảng thời gian rỗng hoặc không đủ tiêu chuẩn để kết luận, phải phản hồi rõ ràng thay vì tự suy diễn.

Hãy xây dựng kế hoạch ReAct chi tiết:
1. **Suy luận (Thought):** Xác định chính xác các chỉ số cần thiết (lượng tiêu thụ trong tháng, lượng tồn kho hiện tại, ngưỡng tồn tối thiểu).
2. **Hành động (Action):** Nêu câu lệnh SQL hoặc Tool Call cần chạy để lấy dữ liệu.
3. **Quan sát (Observation):** Mô tả kết quả kỳ vọng thu được từ CSDL (dữ liệu giả định hợp lý).
4. **Tổng hợp (Final Response):** Đưa ra câu trả lời trực tiếp cho Chủ phòng khám bằng tiếng Việt, ngắn gọn, đi kèm khuyến nghị nhập/xả kho hoặc điều chỉnh định mức sử dụng.

Định dạng đầu ra:
- ReAct Trace chi tiết dạng bảng bao gồm các cột: Bước, Thought (Suy luận), Action (Hành động / SQL), Observation (Quan sát).
- Câu truy vấn SQL đề xuất hoàn chỉnh.
- Câu trả lời mẫu bằng tiếng Việt mang tính quản trị, đề xuất giải pháp xử lý vật tư tồn cao/tiêu thụ chậm.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `14-Hoi-dap-react-nha-khoa.md` thì file kết quả phải là `14-Hoi-dap-react-nha-khoa_ket_qua.md`.