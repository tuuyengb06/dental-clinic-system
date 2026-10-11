# Prompt: Chọn thiết kế CSDL tồn kho bằng Self-Consistency

## Kỹ thuật minh họa

Self-Consistency: tạo nhiều phương án thiết kế độc lập, so sánh theo tiêu chí và chọn phương án phù hợp nhất.

## Prompt sử dụng

Bạn là kiến trúc sư phần mềm. Hãy giải quyết bài toán thiết kế CSDL quản lý tồn kho vật tư nha khoa bằng cách tạo 3 phương án độc lập, sau đó so sánh và chọn phương án phù hợp nhất.

Bối cảnh:

- Hệ thống quản lý danh mục vật tư nha khoa, hồ sơ điều trị, ghi nhận sử dụng vật tư và các phiếu nhập kho.
- Cần xử lý chính xác khi nhập vật tư, ghi nhận sử dụng trong điều trị, chỉnh sửa lượng sử dụng và hủy ghi nhận.
- Cần dữ liệu phục vụ tra cứu tồn kho hiện tại, lịch sử biến động và báo cáo sử dụng vật tư.
- Dữ liệu hồ sơ bệnh nhân và điều trị cần được bảo vệ theo quyền truy cập; báo cáo tồn kho nên dùng dữ liệu tổng hợp khi không cần thông tin bệnh nhân.

Yêu cầu Self-Consistency:

1. Tạo Phương án A: lưu số lượng tồn kho hiện tại trực tiếp trong bảng `inventory_items`.
2. Tạo Phương án B: dùng bảng `inventory_movements` làm lịch sử nhập/xuất vật tư và tính tồn kho từ các biến động.
3. Tạo Phương án C: kết hợp số lượng tồn kho hiện tại để tra cứu nhanh với bảng lịch sử biến động để audit và đối soát.
4. Với mỗi phương án, mô tả cách xử lý nhập kho, ghi nhận sử dụng vật tư, chỉnh sửa lượng sử dụng, hủy ghi nhận và báo cáo tồn kho.
5. Đánh giá từng phương án theo các tiêu chí: đúng nghiệp vụ, dễ triển khai demo, dễ audit, hỗ trợ báo cáo, hiệu năng tra cứu và rủi ro sai lệch tồn kho.
6. Chọn phương án được nhiều tiêu chí ủng hộ nhất cho hệ thống quản lý nha khoa, giải thích các đánh đổi và nêu điều kiện cần thiết để phương án đó hoạt động nhất quán.

Ràng buộc:

- Không thiết kế lại toàn bộ hệ thống; tập trung vào các bảng và quan hệ cần cho tồn kho vật tư nha khoa.
- Nêu rõ cách bảo đảm thao tác lưu hồ sơ/ghi nhận sử dụng vật tư và cập nhật tồn kho nhất quán, chẳng hạn dùng transaction phù hợp.
- Khi sửa lượng đã sử dụng, phải tránh trừ toàn bộ lượng mới lần nữa; xử lý theo chênh lệch so với lượng đã ghi nhận.
- Không giả định chính sách nghiệp vụ chưa nêu, như cho phép tồn kho âm, quy trình kiểm kê hoặc hoàn trả vật tư đã mở/đã sử dụng. Ghi rõ các giả định cần xác minh.
- Không đưa thông tin định danh bệnh nhân hoặc chi tiết sức khỏe vào dữ liệu báo cáo tồn kho.

Định dạng đầu ra:

- Bảng so sánh 3 phương án.
- Kết luận chọn phương án.
- Lý do chọn và các đánh đổi.
- Các bảng/thuộc tính chính cần có trong phương án được chọn.
- Các test case bắt buộc cho phương án được chọn, tối thiểu gồm nhập kho, ghi nhận sử dụng, tăng/giảm lượng sử dụng khi chỉnh sửa, hủy ghi nhận và lỗi giữa transaction.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
