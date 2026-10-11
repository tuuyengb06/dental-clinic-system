# Prompt: Sinh code gọi API AI cho báo cáo doanh thu nha khoa

## Kỹ thuật minh họa

Prompt sinh mã cho chức năng AI có kiểm soát lỗi và dữ liệu nhạy cảm.

## Prompt sử dụng

[Instructions]

Viết module Python gọi AI để sinh nhận xét doanh thu và hoạt động cho hệ thống quản lý nha khoa.

[Context]

- Backend dùng Python.
- Dữ liệu đầu vào gồm doanh thu tổng hợp theo ngày, số lượt sử dụng dịch vụ nha khoa và số lượng tồn kho vật tư.
- AI chỉ tạo nhận xét và gợi ý vận hành dựa trên dữ liệu được cung cấp; không được thay đổi dữ liệu hệ thống.
- AI không được đưa ra chẩn đoán, khuyến nghị điều trị hoặc kết luận chuyên môn y tế.

[Constraints]

- API key phải được đọc từ biến môi trường, không hardcode trong mã nguồn.
- Cấu hình timeout cho yêu cầu gọi API.
- Xử lý và báo lỗi rõ ràng đối với rate limit, lỗi kết nối/timeout, response rỗng và response sai định dạng; không trả về nội dung giả như kết quả thành công.
- Không gửi thông tin định danh bệnh nhân, hồ sơ sức khỏe, nội dung ghi chú khám, dữ liệu thanh toán cá nhân hoặc dữ liệu nhạy cảm không cần thiết.
- Chỉ gửi dữ liệu tổng hợp cần cho báo cáo; không tự truy vấn hoặc sửa dữ liệu hệ thống.
- Prompt gửi cho AI phải yêu cầu output Markdown gồm: Tóm tắt, Điểm đáng chú ý, Cảnh báo tồn kho vật tư, Khuyến nghị vận hành.
- Nội dung khuyến nghị chỉ mang tính hỗ trợ vận hành, phải dựa trên dữ liệu đầu vào và nêu rõ khi dữ liệu không đủ; không khuyến nghị điều trị.
- Tách prompt template khỏi hàm gọi API.
- Dùng type hints và xử lý cấu hình thiếu theo cách rõ ràng.

[Output Format]

Trả về:

1. File `ai_prompts.py` chứa prompt template.
2. File `ai_report_service.py` chứa hàm `generate_dental_revenue_insight`.
3. Ví dụ cách gọi hàm với dữ liệu tổng hợp giả lập, không chứa thông tin bệnh nhân.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
