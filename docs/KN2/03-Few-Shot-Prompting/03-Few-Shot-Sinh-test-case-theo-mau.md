# Prompt: Sinh test case theo mẫu bằng Few-Shot

## Kỹ thuật minh họa

Few-Shot Prompting với ví dụ đại diện và edge case.

## Prompt sử dụng

Bạn là QA Engineer. Hãy sinh test case cho hệ thống quản lý nha khoa theo đúng định dạng của ví dụ.

Ví dụ:

Chức năng: Lập hóa đơn dịch vụ nha khoa

Test case ID: TC-HD-01

Mục tiêu: Tạo hóa đơn hợp lệ cho dịch vụ nha khoa

Tiền điều kiện: Có dịch vụ Trám răng Composite đang hoạt động, giá 350000 đồng; tài khoản nhân viên được cấp quyền lập hóa đơn.

Bước thực hiện:

1. Đăng nhập bằng tài khoản nhân viên được cấp quyền.
2. Tạo hóa đơn mới cho một bệnh nhân kiểm thử giả lập.
3. Chọn dịch vụ Trám răng Composite, số lượng 2.
4. Nhập giảm giá 0 đồng.
5. Chọn phương thức thanh toán tiền mặt.
6. Lưu hóa đơn.

Kết quả mong đợi:

- Hóa đơn được tạo thành công.
- Tổng tiền phải thanh toán là 700000 đồng.
- Hóa đơn được lưu với trạng thái thanh toán phù hợp.
- Không hiển thị dữ liệu bệnh nhân ngoài phạm vi quyền truy cập.

Nhiệm vụ:

Sinh test case cho các chức năng:

1. Không cho ghi nhận sử dụng vật tư vượt quá số lượng tồn kho.
2. Hủy hóa đơn chưa thanh toán và cập nhật lại số lượng vật tư nếu trước đó đã được ghi nhận sử dụng.
3. Chatbot tư vấn thông tin dịch vụ nha khoa theo nhu cầu của khách; chỉ sử dụng nội dung đã được phòng khám phê duyệt và không đưa ra chẩn đoán.
4. AI hỗ trợ tạo nhận xét báo cáo doanh thu khi dữ liệu trong khoảng thời gian được chọn rỗng.
5. Xuất báo cáo doanh thu ra CSV.

Ràng buộc:

- Mỗi chức năng có ít nhất 1 test case happy path hoặc edge case phù hợp.
- Không dùng dữ liệu định danh hoặc hồ sơ sức khỏe thật của bệnh nhân; chỉ sử dụng dữ liệu giả lập.
- Kết quả mong đợi phải kiểm chứng được, có giá trị cụ thể khi phù hợp.
- Với nội dung AI, kiểm tra AI không tự bịa thông tin khi thiếu dữ liệu, không chẩn đoán và không quyết định điều trị thay bác sĩ.
- Không giả định nghiệp vụ hủy hóa đơn hoặc cập nhật vật tư ngoài mô tả; nếu cần giả định để viết test, nêu rõ trong tiền điều kiện.

Định dạng đầu ra:

Markdown, mỗi test case gồm đúng các mục như ví dụ:

- Chức năng
- Test case ID
- Mục tiêu
- Tiền điều kiện
- Bước thực hiện
- Kết quả mong đợi

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
