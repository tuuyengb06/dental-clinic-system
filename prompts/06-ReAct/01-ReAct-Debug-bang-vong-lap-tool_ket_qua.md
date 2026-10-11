# Kế hoạch ReAct debug tồn kho

> Chỉ có mô tả lỗi, chưa có repository code, test fail hoặc lệnh chạy. Các bước “quan sát” dưới đây nêu rõ điều đã biết từ đầu vào và điều cần đo; không khẳng định đã đọc/sửa/chạy mã nguồn.

## 1. Kế hoạch ban đầu

1. Tìm hàm ghi/sửa/hủy usage và các nơi gọi.
2. Kiểm tra cách so sánh lượng cũ/mới, transaction và movement/audit.
3. Viết test hồi quy cho tăng, giảm, giữ nguyên, hủy và lỗi giữa transaction.
4. Sửa nhỏ nhất để áp dụng delta và tính idempotent.
5. Chạy test liên quan, sau đó xem diff.

## 2. Các vòng ReAct

| Vòng | Suy luận ngắn (giả thuyết) | Hành động | Quan sát |
|---|---|---|---|
| 1 | Có thể code trừ toàn bộ lượng mới khi update, thay vì chênh lệch | Đọc hàm update usage và callers; so sánh trường lượng cũ/mới | Chưa thực hiện được: mã nguồn không được cung cấp trong yêu cầu này. Cần xác nhận |
| 2 | Nếu tồn thay đổi trước khi usage lưu, lỗi giữa chừng có thể tạo lệch | Kiểm tra transaction và mọi điểm ghi inventory/movement | Chưa có code/DB để quan sát transaction |
| 3 | Hủy hoặc request lặp có thể đảo/trừ nhiều lần | Kiểm tra status/idempotency của usage và movement; thử gửi lặp trong test | Chưa có mã để xác minh tính lặp |
| 4 | Delta dương có thể vượt tồn hiện tại | Thêm test vượt tồn, tăng/giảm/giữ nguyên | Chưa chạy được vì không có test runner hoặc dự án cụ thể trong đầu vào |

## 3. Nguyên nhân gốc rễ và bằng chứng

**Chưa thể xác nhận nguyên nhân gốc rễ** khi chưa đọc mã thực tế. Giả thuyết cần kiểm chứng là phép cập nhật tồn kho đang áp dụng toàn bộ lượng mới thay vì `new_quantity - old_quantity`. Bằng chứng hiện có chỉ là mô tả lỗi; không phải bằng chứng từ code/runtime.

## 4. Bản sửa đề xuất

Sau khi xác nhận mã hiện tại, thay đổi nhỏ nhất thường là:

```text
delta = new_quantity - old_quantity
if delta > 0:
    validate stock >= delta
    stock -= delta
elif delta < 0:
    stock += abs(delta)
# delta == 0: không đổi tồn
```

Lưu lượng usage, số tồn và movement liên quan trong cùng transaction; movement có khóa idempotency. Khi hủy, chỉ đảo lại nếu nghiệp vụ xác nhận usage chưa thực hiện/được phép đảo, và chỉ một lần. Không tự hoàn vật tư đã thực sự tiêu hao.

## 5. Test cần chạy và kết quả thực tế

**Chưa chạy test** — không có cấu trúc backend, file test, lệnh chạy hoặc quyền truy cập cụ thể trong đầu vào.

Test cần bổ sung: (1) tăng 2→3 chỉ trừ 1; (2) giảm 3→2 cộng lại 1; (3) giữ nguyên không đổi tồn; (4) hủy usage được phép một lần và hủy lặp không đổi thêm; (5) tồn không đủ từ chối không cập nhật một phần; (6) lỗi giữa transaction rollback mọi thay đổi. Sau khi có dự án, chạy test liên quan bằng lệnh thực tế của repository và ghi đúng kết quả.
