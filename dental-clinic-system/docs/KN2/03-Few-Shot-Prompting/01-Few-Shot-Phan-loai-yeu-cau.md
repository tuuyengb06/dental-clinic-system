# Prompt: Phân loại yêu cầu bằng Few-Shot

## Kỹ thuật minh họa
Few-Shot Prompting: cung cấp ví dụ mẫu để mô hình học cách phân loại yêu cầu phần mềm y tế một cách chính xác.

## Prompt sử dụng

Bạn là chuyên viên phân tích yêu cầu phần mềm y tế (BA). Hãy phân loại các yêu cầu của Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI thành một trong bốn nhóm: 
- Quản lý dữ liệu & Hồ sơ
- Nghiệp vụ khám & Khai thác
- Báo cáo & Tài chính
- Chức năng AI hỗ trợ

Ví dụ minh họa:

Input: "Lễ tân có thể thêm mới, cập nhật thông tin cá nhân và tiền sử bệnh lý của bệnh nhân."
Output: Quản lý dữ liệu & Hồ sơ

Input: "Bác sĩ cập nhật trạng thái răng trên sơ đồ răng (Dental Chart) và kê đơn thuốc sau khám."
Output: Nghiệp vụ khám & Khai thác

Input: "Chủ phòng khám xem thống kê doanh thu theo từng bác sĩ và từng dịch vụ theo tháng."
Output: Báo cáo & Tài chính

Input: "Chatbot AI tự động phản hồi thắc mắc về giá dịch vụ và hỗ trợ bệnh nhân đặt lịch hẹn 24/7."
Output: Chức năng AI hỗ trợ

Hãy phân loại các yêu cầu sau:
1. Quản trị viên hệ thống tạo tài khoản cho bác sĩ, lễ tân và cấu hình phân quyền truy cập.
2. Lễ tân tiếp đón bệnh nhân, tạo lịch hẹn mới và ghi nhận tiền tạm ứng điều trị.
3. Mô hình AI phân tích ảnh X-quang răng và tự động khoanh vùng gợi ý các vị trí nghi ngờ sâu răng.
4. Quản lý phòng khám lọc danh sách công nợ trả góp của bệnh nhân theo khoảng thời gian.
5. Hệ thống tự động trừ số lượng vật tư y tế (mắc cài, thuốc tê) trong kho khi bác sĩ hoàn thành ca điều trị.
6. Chủ phòng khám hỏi AI bằng ngôn ngữ tự nhiên: "Tháng này dịch vụ nào có doanh thu cao nhất và bác sĩ nào khám nhiều ca nhất?"

Định dạng đầu ra:
Bảng Markdown gồm các cột: STT, Yêu cầu, Nhóm phân loại, Giải thích ngắn gọn.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `08-Phan-loai-yeu-cau-nha-khoa.md` thì file kết quả phải là `08-Phan-loai-yeu-cau-nha-khoa_ket_qua.md`.