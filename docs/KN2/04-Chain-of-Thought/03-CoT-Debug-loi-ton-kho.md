# Prompt: Debug lỗi tồn kho vật tư bằng Chain-of-Thought

## Kỹ thuật minh họa

Phân tích lỗi debugging bằng cách truy vết trạng thái và xác định nguyên nhân gốc rễ.

## Prompt sử dụng

Bạn là lập trình viên backend senior. Hãy phân tích lỗi tồn kho vật tư trong hệ thống quản lý nha khoa.

Mô tả lỗi:

- Vật tư Composite trám răng có tồn kho ban đầu là 12 đơn vị.
- Bác sĩ hoàn tất hồ sơ điều trị và ghi nhận đã sử dụng 2 đơn vị vật tư. Hệ thống trừ tồn kho còn 10.
- Sau đó, bác sĩ chỉnh sửa hồ sơ điều trị, cập nhật lượng vật tư đã sử dụng từ 2 lên 3 đơn vị.
- Hệ thống trừ tiếp 3 đơn vị và tồn kho còn 7.
- Kết quả đúng phải là 9 vì lượng sử dụng chỉ tăng thêm 1 đơn vị so với dữ liệu đã ghi nhận trước đó.

Yêu cầu:

Phân tích lần lượt các điểm sau và trình bày kết luận ngắn gọn:

1. Xác định trạng thái tồn kho trước và sau mỗi thao tác.
2. Xác định nguyên nhân gốc rễ.
3. Đề xuất thuật toán cập nhật tồn kho khi sửa lượng vật tư đã sử dụng.
4. Đề xuất test case để ngăn lỗi tái diễn.

Ràng buộc:

- Không đề xuất viết lại toàn bộ hệ thống.
- Tập trung vào logic cập nhật tồn kho khi ghi nhận, sửa hoặc hủy ghi nhận sử dụng vật tư.
- Khi sửa lượng sử dụng, chỉ điều chỉnh phần chênh lệch giữa số lượng mới và số lượng đã ghi nhận trước đó; xử lý riêng trường hợp số lượng giảm.
- Nêu cách bảo đảm việc cập nhật tồn kho và hồ sơ điều trị nhất quán nếu một thao tác thất bại.
- Không giả định thêm quy trình chuyên môn hoặc chính sách kho chưa được mô tả; nêu rõ giả định cần xác minh nếu cần.

Định dạng đầu ra:

- Nguyên nhân gốc rễ.
- Bảng mô phỏng tồn kho đúng/sai.
- Pseudocode thuật toán sửa lượng vật tư đã sử dụng.
- Danh sách test case, bao gồm tăng lượng sử dụng, giảm lượng sử dụng, giữ nguyên lượng và hủy ghi nhận.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
