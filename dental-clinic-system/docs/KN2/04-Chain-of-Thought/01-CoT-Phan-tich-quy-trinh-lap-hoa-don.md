# Prompt: Phân tích quy trình lập hóa đơn thanh toán bằng Chain-of-Thought

## Kỹ thuật minh họa
Chain-of-Thought: yêu cầu phân tích từng bước logic trước khi đưa ra kết quả chi tiết.

## Prompt sử dụng

Bạn là chuyên viên phân tích nghiệp vụ phần mềm y tế (BA). Hãy phân tích quy trình lập hóa đơn thanh toán và quản lý công nợ điều trị cho hệ thống quản lý phòng khám nha khoa có tích hợp AI.

Bối cảnh:
- Sau khi bác sĩ hoàn thành ca khám/thực hiện dịch vụ nha khoa (hoặc theo phác đồ điều trị từng đợt), Lễ tân/Thu ngân sẽ lập hóa đơn thanh toán cho bệnh nhân.
- Hóa đơn bao gồm chi phí dịch vụ nha khoa, thủ thuật, vật tư tiêu hao đính kèm (nếu có), chiết khấu/ưu đãi và trừ đi tiền tạm ứng trước đó.
- Hệ thống cần kiểm tra tồn kho vật tư/thuốc liên quan trước khi chốt hóa đơn.
- Bệnh nhân có thể thanh toán một lần hoặc thanh toán trả góp nhiều đợt (đối với các gói điều trị lớn như niềng răng, implant).
- AI hỗ trợ gợi ý áp dụng mã giảm giá phù hợp hoặc nhắc nhở công nợ đợt tiếp theo dựa trên lịch trình điều trị.
- Nếu hóa đơn bị hủy, chỉnh sửa hoặc hoàn tiền, hệ thống phải cập nhật trạng thái công nợ và hoàn trả vật tư tiêu hao vào kho một cách nhất quán.

Hãy suy nghĩ từng bước theo trình tự nghiệp vụ nha khoa:
1. Xác định actor và mục tiêu chính.
2. Xác định dữ liệu đầu vào (bệnh án, chỉ định bác sĩ, bảng giá, vật tư, tiền tạm ứng).
3. Xác định các bước xử lý chính (từ tiếp nhận chỉ định, tính toán chi phí, gợi ý AI, ghi nhận thanh toán đến trừ tồn kho).
4. Xác định điều kiện lỗi và các trường hợp đặc biệt (edge cases: trả góp, nợ xấu, hoàn dịch vụ).
5. Xác định dữ liệu đầu ra (hóa đơn, phiếu thu, nhật ký công nợ, cập nhật kho).
6. Đề xuất use case hoàn chỉnh.

Định dạng đầu ra:
- Phần A: Phân tích từng bước (Chain-of-Thought).
- Phần B: Use case "Lập hóa đơn thanh toán dịch vụ nha khoa" gồm: Actor, Tiền điều kiện, Luồng chính, Luồng thay thế/ngoại lệ, Hậu điều kiện.
- Phần C: Các điểm kiểm thử (Test scenarios & Edge cases) cần chú ý.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `05-Phan-tich-lap-hoa-don-nha-khoa.md` thì file kết quả phải là `05-Phan-tich-lap-hoa-don-nha-khoa_ket_qua.md`.