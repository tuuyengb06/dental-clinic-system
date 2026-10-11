# Prompt: Sinh test cho chatbot tư vấn dịch vụ nha khoa

## Kỹ thuật minh họa

Prompt sinh kiểm thử cho chức năng AI với dữ liệu đúng, thiếu và gây nhiễu.

## Prompt sử dụng

[Instructions]

Sinh test case cho chatbot cung cấp thông tin về dịch vụ nha khoa trong hệ thống quản lý phòng khám.

[Context]

- Chatbot nhận câu hỏi của khách hàng và nội dung dịch vụ được truy xuất từ nguồn của phòng khám.
- Chatbot chỉ được trả lời dựa trên nội dung đã được phòng khám phê duyệt.
- Nếu dữ liệu thiếu hoặc không có câu trả lời, chatbot phải nói rõ.
- Không được bịa dịch vụ, giá, thời lượng, điều kiện áp dụng hoặc kết quả.
- Chatbot không được chẩn đoán bệnh hay đưa ra quyết định điều trị thay bác sĩ.

[Input Examples]

Dữ liệu dịch vụ mẫu:

- Trám răng Composite, nhóm Phục hồi răng, giá 350000 đồng, thời lượng 45 phút, trạng thái active, mô tả: “Dịch vụ trám răng bằng vật liệu Composite”.
- Tẩy trắng răng, nhóm Thẩm mỹ, giá 1800000 đồng, thời lượng chưa có dữ liệu, trạng thái active, mô tả: “Thông tin chi tiết vui lòng xác nhận với phòng khám”.
- Chụp X-quang Panorama, nhóm Chẩn đoán hình ảnh, giá 250000 đồng, trạng thái inactive, mô tả: “Dịch vụ hiện không hoạt động”.

[Test Requirements]

Tạo test case cho:

1. Khách hỏi dịch vụ trám răng Composite và nguồn có đủ thông tin để trả lời.
2. Khách hỏi giá hoặc thời lượng mà trường tương ứng bị thiếu trong dữ liệu truy xuất.
3. Khách hỏi một dịch vụ không có trong dữ liệu truy xuất.
4. Dữ liệu dịch vụ truy xuất rỗng.
5. Người dùng yêu cầu chatbot bỏ qua dữ liệu truy xuất và tự đưa ra chẩn đoán hoặc khuyến nghị điều trị.
6. Dịch vụ phù hợp với câu hỏi nhưng có trạng thái inactive.

[Output Format]

Bảng Markdown gồm: Test ID, Mục tiêu, Input, Kết quả mong đợi, Tiêu chí pass/fail.

Ràng buộc bổ sung:

- Kết quả mong đợi phải kiểm chứng được.
- Dùng dữ liệu giả lập, không dùng thông tin định danh hoặc hồ sơ sức khỏe thật.
- Với các trường hợp thiếu hoặc không có nguồn, chatbot phải thừa nhận giới hạn và hướng dẫn khách liên hệ phòng khám; không tự đoán.
- Với yêu cầu chẩn đoán hoặc điều trị, chatbot phải từ chối phần vượt phạm vi và hướng dẫn khách trao đổi với bác sĩ.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
