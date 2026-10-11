# Self-Consistency: Thiết kế CSDL tồn kho vật tư nha khoa

## So sánh 3 phương án

| Tiêu chí | A — tồn trực tiếp trên `inventory_items` | B — chỉ `inventory_movements` | C — tồn hiện tại + movement ledger |
|---|---|---|---|
| Cấu trúc | `inventory_items.stock_quantity`; usage liên kết hồ sơ điều trị | Mỗi nhập/xuất là một movement; tồn là tổng delta | Snapshot `stock_quantity` và movement bất biến |
| Nhập kho | Cộng vào số tồn | Thêm movement dương | Transaction thêm movement dương và cộng snapshot |
| Ghi nhận sử dụng | Trừ số lượng | Thêm movement âm | Transaction thêm movement âm và trừ snapshot |
| Sửa số lượng đã dùng | Điều chỉnh snapshot theo `new-old`, cần lưu giá trị trước | Thêm movement bù `old-new` hoặc `new-old` theo dấu quy ước | Ghi movement bù và cập nhật snapshot theo delta |
| Hủy ghi nhận | Cộng lại một lần nếu nghiệp vụ cho đảo | Ghi movement đảo dấu đúng một lần | Movement đảo dấu + snapshot cùng transaction, có idempotency |
| Báo cáo/đối soát | Tra nhanh; lịch sử hạn chế nếu không có bảng audit khác | Lịch sử đầy đủ; tổng ledger có thể tốn chi phí tính | Tra nhanh và có lịch sử đối soát |
| Đúng nghiệp vụ / sai lệch | Dễ hiểu, nhưng update lặp/đồng thời dễ lệch | Ledger minh bạch; phải bảo toàn tính toàn vẹn và tính lại chính xác | Có dư thừa nên cần transaction/đối soát, nhưng vừa nhanh vừa audit được |
| Demo/hiệu năng | Dễ triển khai, đọc nhanh | Dễ audit hơn, truy vấn tồn cần sum/index/cache | Phức tạp hơn một chút, đọc nhanh |

## Kết luận chọn phương án

Chọn **Phương án C** cho ứng dụng có yêu cầu xem tồn hiện tại đồng thời truy vết nhập/xuất và sửa/hủy. Đây là lựa chọn đề xuất, không phải quy tắc kho đã được xác nhận. Mỗi thay đổi tồn phải ghi movement bất biến và cập nhật snapshot trong cùng transaction; nếu một bước lỗi thì rollback cả hai. Khi sửa lượng sử dụng, delta bằng `new_quantity - old_quantity`: delta dương thì trừ phần tăng thêm; delta âm thì cộng lại phần giảm. Movement phải có tham chiếu bản ghi nghiệp vụ và idempotency để thao tác lặp không nhân đôi. Nên có tác vụ đối soát snapshot với tổng movements và phát hiện chênh lệch. Đánh đổi là dữ liệu tồn được lưu hai nơi, tăng độ phức tạp và cần kiểm thử đồng thời/rollback.

## Bảng/thuộc tính chính cho phương án C

| Bảng | Thuộc tính chính | Ràng buộc/gợi ý |
|---|---|---|
| `inventory_items` | `id`, `item_code`, `name`, `unit`, `stock_quantity`, `status` | Mã duy nhất; stock không âm nếu chính sách xác nhận; snapshot phục vụ tra cứu |
| `inventory_movements` | `id`, `inventory_item_id`, `quantity_delta`, `movement_type`, `source_type`, `source_id`, `idempotency_key`, `created_at`, `actor_user_id` | FK; movement không sửa/xóa tùy tiện; khóa idempotency duy nhất; chỉ ghi dữ liệu cần thiết |
| `treatment_material_usages` (nếu cần) | `id`, `treatment_record_id`, `inventory_item_id`, `quantity`, `status`, `movement_ref` | Liên kết hồ sơ điều trị; giữ lượng hiện hành để tính delta; quyền đọc hạn chế |
| `inventory_receipts` (nếu có nghiệp vụ) | `id`, `inventory_item_id`, `quantity`, `created_at`, `actor_user_id` | Chỉ thêm nếu nghiệp vụ nhập kho được xác nhận |

## Test case bắt buộc

| Trường hợp | Thiết lập/thao tác | Kết quả |
|---|---|---|
| Nhập kho | Tồn 10, ghi movement +5 trong transaction | Snapshot 15; ledger có đúng một movement |
| Ghi nhận sử dụng | Tồn 12, xác nhận dùng 2 | Tồn 10; ledger -2, usage liên kết |
| Tăng lượng | Usage 2, sửa 3 | Chỉ thêm movement -1; tồn giảm thêm 1 |
| Giảm lượng | Usage 3, sửa 2 | Movement +1; tồn tăng 1 |
| Hủy ghi nhận | Đảo việc sử dụng được xác nhận | Movement đảo đúng lượng một lần; lần lặp không đổi tồn lần nữa |
| Lỗi giữa transaction | Lỗi sau update snapshot hoặc trước movement | Rollback cả usage, snapshot và ledger |
| Không đủ tồn | Yêu cầu tăng vượt số sẵn có | Từ chối; không có dữ liệu cập nhật dở dang |

**Điểm cần xác minh:** chính sách tồn âm; đơn vị có phần lẻ; kiểm kê/nhập kho; vật tư đã mở hoặc tiêu hao có thể hoàn hay không; ai được phép ghi nhận. Không đưa định danh bệnh nhân hoặc ghi chú điều trị vào báo cáo kho.
