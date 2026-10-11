# Prompt: Refactor service hóa đơn nha khoa

## Kỹ thuật minh họa

Prompt cho tác vụ lập trình nâng cao: tái cấu trúc mã nguồn.

## Prompt sử dụng

[Instructions]

Phân tích và refactor service xử lý hóa đơn dưới đây để dễ bảo trì, dễ kiểm thử và giảm lỗi liên quan đến tồn kho vật tư nha khoa.

[Context]

- Hệ thống quản lý nha khoa cần xử lý tạo, cập nhật và hủy hóa đơn dịch vụ.
- Việc ghi nhận sử dụng vật tư trong điều trị cần nhất quán với số lượng tồn kho.
- Logic tồn kho là nghiệp vụ quan trọng và phải dễ kiểm thử.
- Việc hủy hóa đơn không mặc nhiên có nghĩa là hoàn lại vật tư đã thực sự tiêu hao trong điều trị.
- Không thay đổi hành vi nghiệp vụ hiện có nếu không nêu rõ lý do và tác động.

[Code]

```python
{{paste_dental_invoice_service_code_here}}
```

[Constraints]

- Tách logic tính tổng hóa đơn khỏi logic cập nhật tồn kho vật tư.
- Tách validation nghiệp vụ thành hàm hoặc thành phần riêng phù hợp với cấu trúc hiện có.
- Khi cập nhật lượng vật tư đã sử dụng, chỉ điều chỉnh tồn kho theo phần chênh lệch so với lượng đã ghi nhận trước đó.
- Đảo ngược biến động vật tư đúng một lần và chỉ khi nghiệp vụ xác nhận việc sử dụng cần được đảo ngược; không hoàn kho vật tư đã thực sự tiêu hao.
- Bảo đảm trạng thái hóa đơn, hồ sơ sử dụng vật tư và tồn kho nhất quán khi có lỗi giữa chừng; ưu tiên tận dụng transaction hoặc cơ chế hiện có.
- Không truy cập AI service trong module hóa đơn.
- Không đưa dữ liệu định danh bệnh nhân hoặc hồ sơ sức khỏe vào log hay ví dụ không cần thiết.
- Mỗi thay đổi phải có lý do; không tạo abstraction hoặc thay đổi ngoài phạm vi cần thiết.
- Nếu thiếu thông tin nghiệp vụ hoặc cấu trúc dự án, nêu giả định cần xác nhận thay vì tự đặt quy tắc.
- Đề xuất test case sau refactor, bao gồm các trường hợp tạo, sửa tăng/giảm số lượng, hủy, lỗi giữa transaction và thao tác lặp.

[Output Format]

1. Danh sách code smell tìm thấy.
2. Phiên bản code đã refactor.
3. Giải thích các thay đổi chính và lý do.
4. Giả định hoặc điểm nghiệp vụ cần xác nhận.
5. Danh sách test case cần chạy.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
