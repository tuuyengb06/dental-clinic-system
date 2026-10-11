# Chatbot RAG cung cấp thông tin dịch vụ nha khoa

## 1. Thông tin dịch vụ phù hợp

Chưa có câu hỏi khách hàng hoặc dữ liệu truy xuất cụ thể được cung cấp để đánh giá dịch vụ phù hợp. Không thể xác nhận tên dịch vụ, giá, thời lượng, tình trạng hoạt động hoặc quy trình đặt lịch.

## 2. Lý do phù hợp với câu hỏi

Chưa thể xác định mức độ phù hợp vì thiếu `customer_question` và `retrieved_dental_service_content`. Chatbot chỉ nên chọn dịch vụ đang hoạt động và chỉ nêu các trường có trong nguồn đã được phòng khám phê duyệt.

## 3. Lưu ý về thông tin chưa được xác nhận

- Không suy đoán dịch vụ, giá, thời lượng, điều kiện áp dụng hoặc kết quả.
- Nếu nội dung truy xuất thiếu, mâu thuẫn hoặc đánh dấu inactive, cần nói rõ và đề nghị khách xác nhận với phòng khám.
- Chatbot không chẩn đoán, đưa ra khuyến nghị điều trị cá nhân hóa hay cam kết kết quả; trường hợp cần đánh giá chuyên môn nên trao đổi với bác sĩ.
- Không yêu cầu khách gửi thông tin định danh hoặc hồ sơ sức khỏe nhạy cảm vào chatbot.

## 4. Câu hỏi tiếp theo nên hỏi khách

“Bạn muốn tìm hiểu thông tin chung về dịch vụ nào hoặc quy trình đặt lịch? Nếu cần tư vấn về tình trạng răng hay lựa chọn điều trị cá nhân, vui lòng trao đổi trực tiếp với bác sĩ.”

### Ví dụ minh họa (không phải dữ liệu đã truy xuất)

Nếu sau này nguồn đã duyệt ghi rõ: `service_name=Trám răng Composite`, `status=active`, `price=350000 đồng`, `duration=45 phút`, thì câu trả lời có thể nêu đúng ba thông tin đó và không thêm khẳng định khác. Ví dụ này chỉ minh họa định dạng, không xác nhận dữ liệu thực tế của phòng khám.
