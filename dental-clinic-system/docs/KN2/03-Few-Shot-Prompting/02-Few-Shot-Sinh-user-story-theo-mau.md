# Prompt: Sinh User Story theo mẫu bằng Few-Shot

## Kỹ thuật minh họa
Few-Shot Prompting để kiểm soát phong cách, chuẩn hóa cấu trúc và đảm bảo độ chi tiết cho yêu cầu phần mềm nha khoa.

## Prompt sử dụng

Bạn là Business Analyst chuyên nghiệp trong lĩnh vực phần mềm y tế. Hãy viết các User Story cho Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI theo đúng phong cách và mức độ chi tiết của các ví dụ bên dưới.

Ví dụ 1:
Chức năng: Quản lý Sơ đồ răng (Dental Chart)
User story:
Là một Bác sĩ Nha khoa, tôi muốn cập nhật trạng thái chi tiết trên sơ đồ răng của bệnh nhân để theo dõi phác đồ điều trị chính xác qua từng giai đoạn.
Tiêu chí chấp nhận:
- Có thể chọn từng răng (11-48) và đánh dấu trạng thái (sâu, đã trám, nhổ, implant, niềng răng...).
- Hệ thống tự động lưu lịch sử thay đổi kèm mốc thời gian và tên bác sĩ thực hiện.
- Không cho phép chỉnh sửa dữ liệu sơ đồ răng của các đợt khám đã hoàn tất và chốt sổ.

Ví dụ 2:
Chức năng: AI Phân tích Ảnh X-quang Răng
User story:
Là một Bác sĩ Nha khoa, tôi muốn AI phân tích và tự động khoanh vùng tổn thương trên ảnh X-quang để hỗ trợ chẩn đoán nhanh và tránh bỏ sót bệnh lý.
Tiêu chí chấp nhận:
- Hệ thống tự động highlight các vùng nghi ngờ (sâu răng, tiêu xương, răng khôn mọc lệch) trong vòng dưới 5 giây sau khi tải ảnh lên.
- Hiển thị mức độ tin cậy (%) của dự đoán do AI đưa ra.
- Cho phép bác sĩ xác nhận, chỉnh sửa hoặc hủy bỏ gợi ý của AI trước khi lưu vào bệnh án chính thức.

Nhiệm vụ:
Hãy viết các User Story cho các chức năng sau của hệ thống nha khoa:
1. Đặt lịch hẹn và Tự động nhắc lịch qua Zalo/SMS.
2. Lập hóa đơn và Quản lý thanh toán trả góp.
3. Quản lý Tồn kho vật tư y tế và Cảnh báo hạn sử dụng.
4. Hỏi đáp dữ liệu báo cáo phòng khám bằng ngôn ngữ tự nhiên (NL2SQL).

Định dạng đầu ra:
Với mỗi chức năng, trình bày rõ ràng:
- Chức năng
- User story (Mẫu: "Là một [Actor], tôi muốn [mục tiêu] để [lợi ích].")
- Tiêu chí chấp nhận (Danh sách dạng bullet points)

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `09-Sinh-user-story-few-shot-nha-khoa.md` thì file kết quả phải là `09-Sinh-user-story-few-shot-nha-khoa_ket_qua.md`.