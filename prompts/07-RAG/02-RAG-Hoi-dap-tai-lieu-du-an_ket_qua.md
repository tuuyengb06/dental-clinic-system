# Hỏi đáp tài liệu dự án bằng RAG

> Đầu vào chưa kèm câu hỏi cụ thể hoặc các `retrieved_chunks`; vì vậy không thể kết luận nội dung dự án hay gắn trích dẫn giả. Phần dưới áp dụng chính xác hành vi “chưa đủ thông tin”.

## 1. Câu trả lời ngắn

Chưa đủ thông tin trong tài liệu được cung cấp.

## 2. Bằng chứng từ tài liệu

Không có đoạn tài liệu truy xuất hoặc `source_id` nào được cung cấp để trích dẫn.

## 3. Giả định hoặc điểm còn thiếu

- Cần có câu hỏi cụ thể của người dùng và các đoạn tài liệu truy xuất liên quan.
- Chỉ thông tin được hỗ trợ trực tiếp bởi đoạn có nguồn mới được trích dẫn.
- Nếu các đoạn mâu thuẫn, cần nêu từng quan điểm kèm nguồn thay vì tự chọn một bên.
- Với nội dung AI hoặc bệnh nhân, phải bám giới hạn được nêu trong tài liệu; giảm thiểu dữ liệu nhạy cảm và bảo vệ thông tin sức khỏe.
- Không đưa ra chẩn đoán, khuyến nghị điều trị hay suy luận thông tin định danh bệnh nhân.

## 4. Gợi ý câu hỏi tiếp theo

Vui lòng cung cấp câu hỏi cần trả lời cùng các đoạn tài liệu liên quan (kèm `source_id` nếu có). Ví dụ: “Theo tài liệu, chatbot được phép làm gì khi thiếu dữ liệu?”.
