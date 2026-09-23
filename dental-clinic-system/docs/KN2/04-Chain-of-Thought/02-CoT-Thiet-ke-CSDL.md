# Prompt: Thiết kế CSDL bằng Chain-of-Thought

## Kỹ thuật minh họa
Chain-of-Thought cho bài toán cần suy luận nhiều bước và cân nhắc quan hệ dữ liệu phức tạp.

## Prompt sử dụng

Bạn là kiến trúc sư cơ sở dữ liệu y tế (Database Architect). Hãy thiết kế CSDL cho hệ thống quản lý phòng khám nha khoa có tích hợp AI.

Ngữ cảnh:
- Cần quản lý: Người dùng & Phân quyền (Quản trị, Bác sĩ, Lễ tân/Thu ngân), Hồ sơ Bệnh nhân (thông tin PII, tiền sử bệnh), Lịch hẹn khám, Bệnh án điện tử (EMR - sơ đồ răng Dental Chart, nhật ký điều trị, đơn thuốc), Danh mục Dịch vụ & Bảng giá, Hóa đơn & Công nợ trả góp, Vật tư y tế & Tồn kho.
- Cần cung cấp dữ liệu cho Chatbot AI: Danh mục dịch vụ, khung giờ trống của bác sĩ/ghế khám để tự động đặt lịch.
- Cần cung cấp dữ liệu cho AI Phân tích hình ảnh: Đường dẫn ảnh X-quang, nhãn tổn thương răng do AI gợi ý.
- Cần cung cấp dữ liệu cho AI Báo cáo (NL2SQL): Doanh thu theo bác sĩ, dịch vụ, công nợ bệnh nhân, tồn kho vật tư để sinh nhận xét kinh doanh bằng ngôn ngữ tự nhiên.

Hãy suy nghĩ từng bước:
1. Xác định các Entity chính trong hệ thống nha khoa.
2. Xác định thuộc tính quan trọng của từng Entity (đặc biệt lưu ý thuộc tính Sơ đồ răng Dental Chart dạng JSON/Text và thuộc tính ẩn danh/mã hóa PII).
3. Xác định khóa chính (PK), khóa ngoại (FK).
4. Xác định quan hệ 1-N, N-N giữa các thực thể (Bệnh nhân - Lịch hẹn, Bệnh nhân - Bệnh án, Bệnh án - Chi tiết răng, Hóa đơn - Đợt thanh toán...).
5. Xác định các ràng buộc dữ liệu (Constraints) để đảm bảo tính toàn vẹn dữ liệu y tế, công nợ và tồn kho vật tư.
6. Đề xuất lược đồ bảng chi tiết.

Ràng buộc:
- Ưu tiên hệ quản trị CSDL SQLite (cho bản Demo/MVP) hoặc PostgreSQL.
- Tuyệt đối không lưu API Key, mật khẩu dạng rõ (plain text) hoặc dữ liệu thẻ thanh toán nhạy cảm trong CSDL.
- Dữ liệu PII của bệnh nhân (SĐT, CCCD) phải có giải pháp mã hóa hoặc tách biệt khi cung cấp dữ liệu cho LLM.

Định dạng đầu ra:
1. Danh sách các Entity chính và lý do tồn tại.
2. Bảng thiết kế CSDL dạng Markdown (Tên bảng, Tên cột, Kiểu dữ liệu, Khóa, Mô tả).
3. Mô tả chi tiết các quan hệ giữa các bảng.
4. Gợi ý chỉ mục (Index) phục vụ tìm kiếm nhanh (Lịch hẹn, Bệnh nhân) và báo cáo doanh thu.
5. Sơ đồ Mermaid ERD biểu diễn mối quan hệ giữa các bảng.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `06-Thiet-ke-csdl-nha-khoa.md` thì file kết quả phải là `06-Thiet-ke-csdl-nha-khoa_ket_qua.md`.