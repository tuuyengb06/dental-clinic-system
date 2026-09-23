# Prompt: Xác định actor và chức năng bằng Zero-Shot

## Kỹ thuật minh họa
Zero-Shot Prompting: yêu cầu trực tiếp, không cung cấp ví dụ mẫu.

## Prompt sử dụng

Bạn là chuyên viên phân tích hệ thống y tế. Dựa trên mô tả sau, hãy xác định actor và chức năng chính cho hệ thống quản lý phòng khám nha khoa có tích hợp AI.

Bối cảnh:
- Phòng khám nha khoa cần quản lý hồ sơ bệnh nhân, lịch hẹn khám, phác đồ điều trị, đơn thuốc, vật tư y tế, hóa đơn thanh toán và báo cáo doanh thu.
- Người dùng gồm: Quản trị viên hệ thống, Lễ tân/Thu ngân, Bác sĩ nha khoa, Bệnh nhân và Chủ phòng khám (Quản lý).
- Hệ thống có các chức năng quản lý vận hành: đăng nhập, phân quyền tài khoản, quản lý hồ sơ bệnh nhân, tiếp đón & check-in, quản lý lịch hẹn (đặt/sửa/hủy), tương tác sơ đồ răng (Dental Chart), kê đơn thuốc, quản lý vật tư kho, lập hóa đơn & theo dõi công nợ, thống kê doanh thu, xuất báo cáo PDF/Excel.
- Hệ thống có các chức năng AI: Chatbot/Voicebot tư vấn dịch vụ & đặt lịch hẹn 24/7, AI gợi ý phân tích chẩn đoán sơ bộ từ ảnh X-quang răng, hỏi đáp dữ liệu doanh thu và hiệu suất phòng khám bằng ngôn ngữ tự nhiên.

Yêu cầu:
1. Liệt kê các actor có trong hệ thống.
2. Với mỗi actor, liệt kê chi tiết các mục tiêu và chức năng tương ứng dựa đúng theo bối cảnh trên.
3. Chỉ ra danh sách chức năng cần phân quyền và kiểm soát truy cập chặt chẽ (đặc biệt liên quan đến dữ liệu y tế nhạy cảm PII và tài chính).
4. Không tự thêm actor hoặc chức năng ngoài bối cảnh đã cung cấp.

Định dạng đầu ra:
- Bảng tổng hợp: Actor | Mục tiêu | Chức năng liên quan
- Danh sách các chức năng cần bảo vệ quyền truy cập và lưu ý an toàn dữ liệu.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `02-Xac-dinh-actor-nha-khoa.md` thì file kết quả phải là `02-Xac-dinh-actor-nha-khoa_ket_qua.md`.