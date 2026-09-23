# Prompt: Sinh test case theo mẫu bằng Few-Shot

## Kỹ thuật minh họa
Few-Shot Prompting với ví dụ đại diện và edge case cho tác vụ kiểm thử phần mềm y tế.

## Prompt sử dụng

Bạn là QA Engineer chuyên nghiệp trong lĩnh vực y tế/nha khoa. Hãy sinh test case cho Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI theo đúng định dạng và mức độ chi tiết của ví dụ dưới đây.

Ví dụ:

Chức năng: Quản lý Sơ đồ răng (Dental Chart)
Test case ID: TC-EMR-01
Mục tiêu: Cập nhật trạng thái trám răng thành công cho bệnh nhân
Tiền điều kiện: Bệnh nhân Nguyen Van A có hồ sơ trên hệ thống, tài khoản Bác sĩ B đã đăng nhập thành công.
Bước thực hiện:
1. Mở hồ sơ bệnh án của bệnh nhân Nguyen Van A.
2. Chọn phân hệ Sơ đồ răng (Dental Chart).
3. Click chọn vị trí Răng số 36.
4. Chọn trạng thái "Sâu răng nhẹ", chọn phương án xử lý "Trám răng Composite", nhập chi phí 300,000 VNĐ.
5. Nhấn "Lưu cập nhật".
Kết quả mong đợi:
- Răng số 36 trên đồ họa chuyển sang màu tương ứng với trạng thái "Đã trám Composite".
- Nhật ký điều trị cập nhật thêm 1 dòng ghi nhận ca điều trị Răng 36 kèm tên Bác sĩ B và thời gian thực tế.
- Tổng chi phí điều trị của đợt khám tăng thêm 300,000 VNĐ.

Nhiệm vụ:
Sinh test case cho các chức năng và kịch bản sau:
1. Không cho phép kê đơn thuốc hoặc xếp lịch vượt quá số lượng tồn kho của vật tư/thuốc tê thực tế.
2. Hủy ca điều trị/hóa đơn dịch vụ và hoàn lại vật tư y tế tiêu hao vào kho.
3. Chatbot AI tư vấn dịch vụ niềng răng khi bệnh nhân yêu cầu tư vấn gói chi phí dưới 30,000,000 VNĐ và hỗ trợ trả góp.
4. AI phân tích ảnh X-quang xử lý trường hợp tệp ảnh tải lên bị mờ, lỗi định dạng hoặc không đúng chuẩn X-quang nha khoa.
5. Xuất báo cáo công nợ bệnh nhân ra file Excel/PDF.

Ràng buộc:
- Mỗi kịch bản chứa ít nhất 1 test case bao phủ cả Happy Path hoặc Edge Case/Negative Path phù hợp.
- Tuyệt đối không dùng thông tin cá nhân (PII) thực tế của bệnh nhân trong dữ liệu kiểm thử.
- Kết quả mong đợi phải cụ thể, đo lường và kiểm chứng được rõ ràng.

Định dạng đầu ra:
Markdown, mỗi test case bao gồm đầy đủ các mục:
- Chức năng
- Test case ID
- Mục tiêu
- Tiền điều kiện
- Bước thực hiện (dạng danh sách có đánh số 1, 2, 3...)
- Kết quả mong đợi (dạng danh sách bullet points)

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `10-Sinh-test-case-nha-khoa.md` thì file kết quả phải là `10-Sinh-test-case-nha-khoa_ket_qua.md`.