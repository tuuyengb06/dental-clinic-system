# Prompt: Debug lỗi tồn kho vật tư y tế bằng Chain-of-Thought

## Kỹ thuật minh họa
Chain-of-Thought cho debugging cần truy vết nguyên nhân gốc rễ và xử lý sai lệch dữ liệu liên quan đến thủ thuật điều trị.

## Prompt sử dụng

Bạn là lập trình viên backend senior cho hệ thống y tế. Hãy phân tích và xử lý lỗi khấu trừ tồn kho vật tư nha khoa (mắc cài, thuốc tê, vật liệu trám...) trong hệ thống quản lý phòng khám nha khoa có tích hợp AI.

Mô tả lỗi nghiệp vụ:
- Vật tư "Mắc cài Kim loại 3M" có tồn kho thực tế ban đầu là 12 bộ.
- Bác sĩ lập hồ sơ điều trị chỉnh nha cho bệnh nhân A và chỉ định sử dụng 2 bộ mắc cài. Hệ thống khấu trừ tồn kho còn 10 bộ.
- Sau đó, bác sĩ cập nhật lại phác đồ điều trị của bệnh nhân A, thay đổi số lượng mắc cài sử dụng từ 2 bộ thành 3 bộ.
- Hệ thống tiếp tục trừ thẳng 3 bộ vào kho làm tồn kho hiện tại tụt xuống còn 7 bộ.
- Kết quả đúng phải là 9 bộ (vì số lượng thực tế tăng thêm chỉ là 1 bộ: 12 - 3 = 9).

Yêu cầu suy nghĩ từng bước:
1. Xác định trạng thái tồn kho vật tư trước và sau mỗi thao tác (Tạo bệnh án -> Cập nhật chỉ định/Hóa đơn).
2. Xác định nguyên nhân gốc rễ trong logic xử lý của Backend (chưa bù trừ chênh lệch `delta` hoặc chưa rollback lượng trừ cũ).
3. Đề xuất thuật toán/logic cập nhật tồn kho chính xác khi Tạo, Sửa, Hủy phiếu điều trị/hóa đơn dịch vụ y tế.
4. Đề xuất danh sách test cases chi tiết để ngăn chặn lỗi tái diễn (bao gồm các trường hợp cập nhật tăng/giảm số lượng, hủy ca điều trị, hoặc nhiều bác sĩ cùng thao tác kho).

Ràng buộc:
- Không đề xuất viết lại toàn bộ hệ thống hay thay đổi cấu trúc CSDL hiện tại.
- Tập trung vào logic xử lý Transaction, kiểm soát bất đồng bộ và bù trừ tồn kho trong ứng dụng.

Định dạng đầu ra:
- Nguyên nhân gốc rễ (Root Cause Analysis).
- Bảng mô phỏng biến động tồn kho thực tế (Trường hợp Sai vs Trường hợp Đúng).
- Pseudocode / Code logic khắc phục (đảm bảo tính nhất quán Transaction).
- Danh sách Test Cases kiểm thử tự động/thủ công.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `07-Debug-loi-ton-kho-nha-khoa.md` thì file kết quả phải là `07-Debug-loi-ton-kho-nha-khoa_ket_qua.md`.