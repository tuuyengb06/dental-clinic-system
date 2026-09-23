# Prompt: So sánh prompt cơ bản và prompt có cấu trúc cho Hệ thống Nha khoa

## Kỹ thuật minh họa
Phân tích so sánh (Comparative Evaluation): Đánh giá sự khác biệt về chất lượng, độ chính xác y tế và tính an toàn dữ liệu giữa prompt thiếu cấu trúc (Ad-hoc Prompt) và prompt có cấu trúc chặt chẽ (Structured Prompt).

## Prompt sử dụng

[Instructions]
So sánh hai prompt dưới đây cho cùng một tác vụ sinh truy vấn SQL báo cáo doanh thu điều trị và hiệu suất dịch vụ nha khoa. Hãy phân tích chuyên sâu lý do tại sao prompt có cấu trúc tạo ra kết quả chính xác, đáng tin cậy và đảm bảo quy chuẩn dữ liệu y tế tốt hơn.

[Context]
- Dự án là Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI.
- Cơ sở dữ liệu PostgreSQL của phòng khám bao gồm các bảng cốt lõi: `patients`, `dentists`, `appointments`, `invoices`, `treatment_services`, `invoice_details`, `medical_supplies`.
- Đội ngũ phát triển (BA/Developer/QA) cần nắm vững tư duy thiết kế prompt chuẩn hóa, không chỉ đánh giá phản hồi dựa trên cảm quan "có vẻ đúng" mà phải kiểm soát tính toàn vẹn của logic tài chính y tế (trả góp niềng răng/implant, bảo hiểm, giảm giá) và bảo mật PHI/PII.

[Input Data]
Prompt A (Cơ bản / Thiếu cấu trúc):
"Viết SQL thống kê doanh thu nha khoa tháng này."

Prompt B (Có cấu trúc chuẩn hóa):
"Bạn là Kỹ sư Cơ sở dữ liệu Senior ngành HealthTech. Hãy viết truy vấn SQL cho PostgreSQL để thống kê doanh thu điều trị nha khoa theo từng ngày trong tháng hiện tại. 
Dữ liệu sử dụng gồm các bảng: 
- `invoices(id, patient_id, appointment_id, invoice_date, status, discount_amount, insurance_covered_amount, net_total)`
- `invoice_details(id, invoice_id, service_id, doctor_id, quantity, unit_price)`
- `treatment_services(id, service_name, category)`.
Ràng buộc nghiệp vụ: 
- Chỉ tính các hóa đơn đã thanh toán thành công (status = 'COMPLETED').
- Bỏ qua các hóa đơn hủy hoặc hoàn tiền (status IN ('CANCELLED', 'REFUNDED')).
- Doanh thu thực tế (net_revenue) = sum(unit_price * quantity) - discount_amount - insurance_covered_amount.
Yêu cầu Output: Trả về các cột `treatment_date`, `total_invoices`, `gross_revenue`, `total_discounts`, `insurance_claims`, `net_revenue`. Sắp xếp theo `treatment_date` tăng dần. 
Chỉ trả về câu lệnh SQL tối ưu và giải thích ngắn gọn các giả định về múi giờ (timezone)."

[Constraints]
- Không yêu cầu thực thi trực tiếp truy vấn SQL.
- Tập trung phân tích theo 5 thành phần cấu trúc prompt tiêu chuẩn: Instructions, Context, Input Data/Constraints, Examples, Output Format.
- Chỉ ra các rủi ro tài chính & nghiệp vụ nha khoa nghiêm trọng (như tính sai doanh thu thực nhận, lộ thông tin bệnh nhân, sót doanh thu thủ thuật) nếu sử dụng Prompt A trong môi trường sản xuất (Production).

[Output Format]
Trình bày tài liệu Markdown gồm:
1. **Bảng so sánh đối chiếu** với các cột: Tiêu chí phân tích, Prompt A (Cơ bản), Prompt B (Cấu trúc), Nhận xét & Đánh giá tác động.
2. **Phần kết luận bài học kinh nghiệm (5–7 câu)** đúc kết nguyên tắc thiết kế prompt cho kỹ sư phần mềm hệ thống nha khoa.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `36-So-sanh-prompt-co-ban-va-co-cau-truc-nha-khoa.md` thì file kết quả phải là `36-So-sanh-prompt-co-ban-va-co-cau-truc-nha-khoa_ket_qua.md`.