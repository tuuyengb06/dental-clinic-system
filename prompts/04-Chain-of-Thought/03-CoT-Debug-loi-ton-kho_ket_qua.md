# Debug lỗi cập nhật tồn kho vật tư

## Nguyên nhân gốc rễ

Khi sửa lượng sử dụng từ 2 lên 3, hệ thống trừ toàn bộ lượng mới (3) thay vì trừ phần tăng thêm (3 − 2 = 1). Do đó tồn sai thành 7 thay vì 9.

## Bảng mô phỏng tồn kho

| Thao tác | Tồn theo mã lỗi | Tồn đúng | Giải thích |
|---|---:|---:|---|
| Ban đầu | 12 | 12 | Tồn khởi điểm |
| Ghi nhận đã dùng 2 | 10 | 10 | Trừ 2 |
| Sửa lượng thành 3 | 7 | 9 | Mã lỗi trừ 3; đúng chỉ trừ thêm 1 |

## Pseudocode sửa lượng đã dùng

```text
function update_usage(usage_id, new_quantity):
    require new_quantity > 0
    begin transaction
    usage = load usage and inventory item
    old_quantity = usage.quantity
    delta = new_quantity - old_quantity

    if delta > 0:
        if current_stock < delta:
            rollback
            return insufficient_stock
        current_stock = current_stock - delta
    else if delta < 0:
        current_stock = current_stock + abs(delta)
    # delta == 0: không đổi tồn

    update usage.quantity = new_quantity
    record an idempotent inventory movement for -delta
    commit
    return success
```

## Bảo đảm nhất quán

- Cập nhật hồ sơ sử dụng, tồn kho và biến động kho trong cùng transaction.
- Chỉ commit khi tất cả bước thành công; lỗi ở bước nào rollback toàn bộ.
- Chống cập nhật đồng thời bằng khóa/transaction phù hợp với DB. Với SQLite có thể dùng transaction ghi thích hợp (ví dụ `BEGIN IMMEDIATE`) và vẫn cần xử lý retry/conflict.
- Ghi biến động có khóa duy nhất/idempotency để thao tác gửi lặp không nhân đôi.
- Khi hủy ghi nhận, hoàn đúng lượng đã trừ một lần và chỉ khi việc sử dụng cần được đảo ngược theo nghiệp vụ.
- Không mặc định chính sách tồn âm hoặc vật tư đã mở/tiêu hao có thể hoàn kho.

## Test case

| ID | Tình huống | Given/When | Kết quả mong đợi |
|---|---|---|---|
| VT-01 | Tăng lượng | Tồn 10, đã dùng 2; sửa thành 3 | Trừ thêm 1; tồn 9; lượng ghi nhận 3 |
| VT-02 | Giảm lượng | Tồn 9, đã dùng 3; sửa thành 2 | Cộng lại 1; tồn 10; lượng ghi nhận 2 |
| VT-03 | Giữ nguyên | Tồn 9, đã dùng 3; sửa thành 3 | Tồn vẫn 9; không thêm movement |
| VT-04 | Hủy ghi nhận | Tồn 10 sau khi đã trừ 2; hủy được nghiệp vụ cho phép | Tồn về 12 đúng một lần; lần hủy lặp không cộng thêm |
| VT-05 | Thiếu tồn khi tăng | Tồn 0, đã dùng 2; yêu cầu sửa thành 3 | Từ chối; hồ sơ, tồn và movements không đổi |
| VT-06 | Thất bại giữa transaction | Inject lỗi sau cập nhật tồn nhưng trước khi lưu usage | Rollback cả tồn, usage và movement |
| VT-07 | Input không hợp lệ | new_quantity bằng 0 hoặc âm | Báo lỗi validation; không thay đổi dữ liệu |

**Giả định cần xác nhận:** đơn vị vật tư là số nguyên hay có thể lẻ; tồn âm có cho phép không; chính sách hủy/hoàn kho và quyền ghi nhận.
