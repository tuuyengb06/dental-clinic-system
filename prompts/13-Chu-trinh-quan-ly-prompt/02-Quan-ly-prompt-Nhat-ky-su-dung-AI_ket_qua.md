# Mẫu nhật ký sử dụng AI

> Ba dòng dưới đây là ví dụ minh họa hư cấu, dùng dữ liệu giả lập. Không phải nhật ký cho tác vụ đã thực sự chạy hoặc kiểm chứng trong repository này.

## 1. Bảng nhật ký Markdown

| Ngày | Giai đoạn SDLC | Mục tiêu | Prompt đã dùng | Công cụ AI | Tóm tắt phản hồi | Cách kiểm chứng | Chỉnh sửa của sinh viên | Kết quả | Ghi chú bảo mật |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-11 (ví dụ) | Phân tích | Phác thảo use case đặt lịch khám | “Đề xuất actor, luồng chính/ngoại lệ cho đặt lịch; đánh dấu điểm thiếu, không dùng dữ liệu thật.” | Trợ lý AI (ví dụ) | Đưa luồng lễ tân tạo lịch, chọn thời gian và phản hồi lỗi | Đối chiếu đặc tả dự án; kiểm tra actor/quy tắc trùng lịch với nhóm | Ghi trùng lịch là điểm cần xác nhận, không coi giả định là yêu cầu | Bản nháp use case, chưa phê duyệt | Chỉ dùng actor giả; không có tên/điện thoại bệnh nhân |
| 2026-10-11 (ví dụ) | Lập trình | Sinh API CRUD dịch vụ nha khoa | “Tạo model/schema/router theo FastAPI; giá không âm, mã duy nhất; nêu giả định và test.” | Trợ lý AI (ví dụ) | Đề xuất CRUD, validation và lỗi trùng mã | Review schema/endpoint; chạy test unit/API trước tích hợp | Đổi biểu diễn giá sang integer VND; thêm authz cần cấu hình | Code draft; cần chạy test thực tế trước merge | Không đưa API key hoặc dữ liệu bệnh nhân |
| 2026-10-11 (ví dụ) | Debug | Tìm lỗi khi sửa lượng vật tư sử dụng | “Phân tích tồn 12 → dùng 2 còn 10 → sửa 3; chỉ dùng delta; đưa test tăng/giảm/hủy.” | Trợ lý AI (ví dụ) | Phát hiện giả thuyết trừ lượng mới thay vì chênh lệch | Kiểm tra code, thêm regression test và chạy suite liên quan | Giữ giả thuyết cho đến khi có bằng chứng từ source; nêu transaction/idempotency | Mẫu cách debug; không tuyên bố mã đã sửa/chạy | Chỉ dùng số lượng giả lập, không có bệnh nhân thật |

## 2. Hướng dẫn sử dụng khi nộp bài

- Ghi ngày, mục tiêu, prompt/phiên bản và đầu ra có liên quan; có thể link file thay vì chép nội dung lớn.
- Nêu cách kiểm chứng độc lập: review đặc tả/code, chạy test và ghi chính xác kết quả. Không ghi “đã chạy/pass” nếu chưa chạy.
- Ghi rõ chỉnh sửa và quyết định của sinh viên; đầu ra AI không mặc nhiên là đáp án cuối.
- Chỉ dùng dữ liệu giả lập hoặc khử định danh. Không ghi thông tin bệnh nhân thật, sức khỏe, thanh toán cá nhân, mật khẩu hay API key.
- Ẩn hoặc loại bỏ nội dung nhạy cảm khỏi log/ảnh chụp/đính kèm.
