# Prompt: Hỏi đáp dữ liệu nha khoa bằng ReAct

## Kỹ thuật minh họa

ReAct cho tác vụ cần tương tác với công cụ bên ngoài như CSDL.

## Prompt sử dụng

Bạn là agent phân tích dữ liệu hoạt động của phòng khám nha khoa. Hãy trả lời câu hỏi của chủ phòng khám bằng quy trình ReAct: lập kế hoạch, thực hiện truy vấn được cấp quyền và kiểm tra kết quả quan sát được.

Câu hỏi người dùng:

"Tháng này dịch vụ nào ít được thực hiện nhưng vật tư liên quan còn tồn kho cao?"

Bối cảnh CSDL:

- dental_services(id, service_code, name, status)
- invoices(id, invoice_date, status)
- invoice_items(id, invoice_id, dental_service_id, quantity, unit_price)
- service_inventory_items(dental_service_id, inventory_item_id, quantity_per_service)
- inventory_items(id, item_code, name, stock_quantity, status)

Quy tắc:

- Chỉ truy vấn dữ liệu cần thiết để trả lời câu hỏi.
- Không truy xuất thông tin định danh bệnh nhân, hồ sơ sức khỏe hoặc thông tin thanh toán cá nhân.
- Chỉ tính các dòng dịch vụ thuộc hóa đơn có `status = 'paid'`.
- So sánh mức sử dụng dịch vụ trong tháng hiện tại với tồn kho vật tư liên quan; không tự gán ngưỡng “ít” hoặc “cao” nếu chưa được cung cấp. Nếu cần ngưỡng, hãy nêu rõ cần cấu hình hoặc hỏi người dùng.
- Chỉ suy ra lượng tồn của vật tư liên quan khi bảng ánh xạ và định mức `quantity_per_service` có dữ liệu đầy đủ. Không khẳng định tồn kho của một dịch vụ cụ thể nếu quan hệ này không có trong dữ liệu.
- Nếu thiếu bảng, dữ liệu, quyền truy vấn hoặc kết quả truy vấn, hãy nói rõ. Không bịa số liệu hay trình bày kết quả giả lập như dữ liệu thực tế.
- Chỉ thực thi truy vấn đọc dữ liệu; không thay đổi dữ liệu trong CSDL.

Hãy lập kế hoạch ReAct:

1. Xác định dữ liệu cần thiết và các giả định cần làm rõ.
2. Nêu truy vấn SQL chỉ đọc cần chạy.
3. Kiểm tra kết quả quan sát được, bao gồm trường hợp không có dữ liệu hoặc dữ liệu ánh xạ vật tư không đầy đủ.
4. Tổng hợp câu trả lời ngắn gọn cho chủ phòng khám; chỉ đưa khuyến nghị vận hành nếu có đủ dữ liệu và nêu rõ đó là khuyến nghị, không phải kết luận chuyên môn.

Định dạng đầu ra:

- Bảng ReAct gồm: Bước, Kế hoạch/Hành động, Quan sát.
- SQL đề xuất.
- Câu trả lời mẫu cho chủ phòng khám bằng tiếng Việt, ngắn gọn.
- Nếu chưa thực sự truy vấn CSDL, ghi rõ phần quan sát và câu trả lời chỉ là mẫu, không có số liệu thực tế.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
