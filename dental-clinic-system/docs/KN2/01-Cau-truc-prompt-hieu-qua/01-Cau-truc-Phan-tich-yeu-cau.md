# Prompt: Phân tích yêu cầu bằng cấu trúc prompt đầy đủ cho Hệ thống Nha khoa

## Kỹ thuật minh họa
Cấu trúc prompt hiệu quả: Instructions (Chỉ dẫn), Context (Bối cảnh), Input Data/Constraints (Dữ liệu/Ràng buộc), Examples (Ví dụ minh họa), Output Format (Định dạng đầu ra).

## Prompt sử dụng

[Instructions]
Dựa vào mô tả bài toán trong tài liệu thông tin dự án: `Codes\Bai 01\dental_project.md`
Hãy thực hiện phân tích yêu cầu nghiệp vụ chuyên sâu cho Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI. Xác định rõ vấn đề nghiệp vụ, mục tiêu hệ thống, danh sách Actor, các chức năng quản lý vận hành, các chức năng AI hỗ trợ, mô hình dữ liệu cốt lõi, yêu cầu phi chức năng và rủi ro/giả định cần kiểm chứng.

[Context]
- Bạn là Chuyên viên Phân tích Nghiệp vụ Phần mềm (Business Analyst) giàu kinh nghiệm trong lĩnh vực Y tế & Nha khoa (HealthTech).
- Hệ thống được triển khai cho chuỗi phòng khám nha khoa quy mô vừa và lớn.
- Hệ thống cần giải quyết toàn diện việc quản lý hồ sơ bệnh án điện tử (EMR), sơ đồ răng (Dental Chart), lịch hẹn khám, vật tư nha khoa, hóa đơn điều trị, và tích hợp sâu các tiện ích AI nâng cao.
- Các chức năng AI bao gồm: Chatbot tư vấn dịch vụ & hỗ trợ đặt lịch hẹn, AI hỗ trợ phân tích hình ảnh X-quang/Sơ đồ răng, AI dự báo nhu cầu vật tư nha khoa & sinh báo cáo doanh thu điều trị.

[Input Data / Constraints]
- Chỉ dựa trên các nghiệp vụ thực tế ngành nha khoa, không tự thêm các chức năng mâu thuẫn:
  - Người dùng gồm: Quản trị hệ thống (Admin), Lễ tân/Thu ngân, Bác sĩ nha khoa, Phụ tá/Y sĩ, và Bệnh nhân.
  - Bệnh nhân có thông tin cá nhân (PII), tiền sử bệnh lý, hồ sơ khám (EMR), sơ đồ răng, lịch sử điều trị và lịch hẹn.
  - Bác sĩ có thông tin chuyên khoa, lịch làm việc, danh sách ca điều trị và hiệu suất làm việc.
  - Hóa đơn điều trị cần hỗ trợ tính chi phí theo thủ thuật, chính sách bảo hiểm/giảm giá, thanh toán nhiều đợt (trả góp niềng răng/implant).
  - Quản lý vật tư nha khoa (trụ Implant, mắc cài, thuốc tê...) cần theo dõi hạn sử dụng, lô sản xuất và cảnh báo tồn kho tối thiểu.
  - Cần xuất báo cáo PDF/Excel cho kế hoạch điều trị, hóa đơn GTGT và báo cáo doanh thu.
  - Bắt buộc tuân thủ quy định bảo mật dữ liệu y tế cá nhân (PHI/PII), không gửi dữ liệu định danh bệnh nhân cho các mô hình AI bên thứ ba.

[Examples]
Ví dụ cách diễn đạt Actor trong nha khoa:
- Actor: Bác sĩ Nha khoa
- Mục tiêu: Chẩn đoán nhanh, cập nhật sơ đồ răng, lập kế hoạch điều trị và theo dõi tiến trình của bệnh nhân.
- Chức năng liên quan: Xem hồ sơ bệnh án EMR, cập nhật Dental Chart, tạo đơn thuốc, ghi chú ca điều trị, xem gợi ý phân tích phim X-quang từ AI.

[Output Format]
Trả lời bằng Markdown với cấu trúc tiêu chuẩn:
1. Bối cảnh và vấn đề nghiệp vụ phòng khám
2. Mục tiêu hệ thống
3. Phân tích Actor và nhu cầu (Bảng Markdown)
4. Danh sách chức năng quản lý vận hành
5. Danh sách chức năng AI tích hợp
6. Cấu trúc dữ liệu cốt lõi
7. Yêu cầu phi chức năng (An toàn y tế, Bảo mật PHI/PII, Hiệu năng)
8. Rủi ro nghiệp vụ và Giả định cần kiểm chứng

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Phan-tich-yeu-cau-nha-khoa.md` thì file kết quả phải là `01-Phan-tich-yeu-cau-nha-khoa_ket_qua.md`.