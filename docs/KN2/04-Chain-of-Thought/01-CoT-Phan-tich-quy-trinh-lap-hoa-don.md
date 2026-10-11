# Prompt: Phân tích quy trình lập hóa đơn bằng Chain-of-Thought

## Kỹ thuật minh họa

Phân tích quy trình theo từng khía cạnh nghiệp vụ trước khi trình bày kết quả.

## Prompt sử dụng

Bạn là chuyên viên phân tích nghiệp vụ. Hãy phân tích quy trình lập hóa đơn dịch vụ cho hệ thống quản lý nha khoa.

Bối cảnh:

- Nhân viên được phân quyền chọn bệnh nhân, thêm các dịch vụ nha khoa đã thực hiện hoặc được xác nhận vào hóa đơn, áp dụng giảm giá nếu có, ghi nhận phương thức thanh toán và lưu hóa đơn.
- Hệ thống cần kiểm tra thông tin dịch vụ và số tiền trước khi lưu hóa đơn.
- Vật tư nha khoa có thể được ghi nhận sử dụng trong quá trình điều trị; việc cập nhật tồn kho cần nhất quán với nghiệp vụ thực tế của phòng khám.
- Khi hóa đơn được thanh toán, hệ thống cập nhật trạng thái thanh toán và lưu thông tin giao dịch cần thiết.
- Nếu hóa đơn bị hủy hoặc điều chỉnh, hệ thống cần xử lý trạng thái hóa đơn, thanh toán và số lượng vật tư nhất quán, tránh cập nhật trùng hoặc sai lệch.
- Thông tin bệnh nhân và hồ sơ sức khỏe chỉ được hiển thị cho người dùng có quyền phù hợp.

Hãy phân tích lần lượt các khía cạnh sau và trình bày kết luận ngắn gọn, không cần tiết lộ suy luận nội bộ:

1. Xác định actor và mục tiêu.
2. Xác định dữ liệu đầu vào.
3. Mô tả các bước xử lý chính.
4. Xác định điều kiện lỗi và edge case.
5. Xác định dữ liệu đầu ra và hậu điều kiện.
6. Đề xuất use case hoàn chỉnh.

Định dạng đầu ra:

- Phần A: Tóm tắt phân tích theo các khía cạnh trên.
- Phần B: Use case "Lập hóa đơn dịch vụ nha khoa" gồm: Actor, Tiền điều kiện, Luồng chính, Luồng thay thế, Hậu điều kiện.
- Phần C: Các điểm cần kiểm thử.

Ràng buộc:

- Không tự đặt ra quy định về giảm giá, hoàn tiền, hủy hóa đơn hoặc thời điểm trừ vật tư nếu bối cảnh chưa xác định. Ghi rõ các giả định cần xác nhận với phòng khám.
- Không đưa ra chẩn đoán hoặc quyết định điều trị; hóa đơn chỉ ghi nhận dịch vụ đã được xác nhận bởi nhân viên có thẩm quyền.
- Không hiển thị dữ liệu định danh hoặc hồ sơ sức khỏe cho actor không có quyền.
- Nêu cách xử lý các trường hợp như dịch vụ không hợp lệ, số tiền không khớp, thanh toán thất bại, lưu trùng yêu cầu, hủy hóa đơn đã thanh toán và vật tư không đủ (nếu có liên quan).

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
