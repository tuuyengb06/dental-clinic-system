# Prompt: Gỡ lỗi sai tồn kho khi hủy hóa đơn nha khoa

## Kỹ thuật minh họa

Prompt debugging có đủ trạng thái trước/sau và yêu cầu sửa có giới hạn.

## Prompt sử dụng

[Instructions]

Debug lỗi cập nhật tồn kho vật tư khi hủy hóa đơn trong hệ thống quản lý nha khoa.

[Context]

- Vật tư nha khoa được ghi nhận sử dụng trong hồ sơ điều trị; khi việc sử dụng được ghi nhận, hệ thống trừ tồn kho.
- Nếu hóa đơn bị hủy và nghiệp vụ điều trị/ghi nhận sử dụng vật tư cũng được đảo ngược vì dịch vụ chưa được thực hiện, hệ thống phải hoàn lại đúng số lượng vật tư đã trừ.
- Nếu điều trị đã được thực hiện và vật tư đã tiêu hao, việc hủy hóa đơn thanh toán không mặc nhiên có nghĩa là vật tư được hoàn lại.
- Lỗi hiện tại: khi hủy hóa đơn trong trường hợp cần đảo ngược việc sử dụng vật tư, hệ thống không hoàn lại tồn kho hoặc hoàn sai số lượng.

[Code liên quan]

```python
def cancel_invoice(invoice):
    invoice.status = "cancelled"
    for usage in invoice.material_usages:
        item = usage.inventory_item
        item.stock_quantity -= usage.quantity
    return invoice
```

[Dữ liệu gây lỗi]

- Vật tư Composite trám răng có tồn kho ban đầu là 12 đơn vị.
- Hồ sơ điều trị ghi nhận sử dụng 2 đơn vị vật tư; sau khi ghi nhận, tồn kho đúng là 10.
- Hóa đơn liên quan bị hủy trong tình huống dịch vụ chưa được thực hiện và việc ghi nhận sử dụng vật tư cần được đảo ngược.
- Sau khi hủy, tồn kho mong đợi là 12 nhưng thực tế là 8.

[Ràng buộc]

- Không đề xuất viết lại toàn bộ hệ thống; tập trung vào logic hủy hóa đơn và đảo ngược biến động tồn kho liên quan.
- Chỉ hoàn lại vật tư khi nghiệp vụ xác nhận việc sử dụng vật tư cần được đảo ngược; không hoàn kho vật tư đã thực sự tiêu hao trong điều trị.
- Không đảo ngược cùng một biến động nhiều lần nếu thao tác hủy được gửi lại.
- Nêu rõ giả định nghiệp vụ và cách bảo đảm cập nhật trạng thái hóa đơn, hồ sơ sử dụng vật tư và tồn kho nhất quán nếu có lỗi giữa chừng.

[Output Format]

Trả lời theo thứ tự:

1. Nguyên nhân lỗi.
2. Dòng code sai.
3. Code đã sửa.
4. Test case tối thiểu để bắt lỗi này, bao gồm hủy cần hoàn vật tư và thao tác hủy lặp lại.
5. Lưu ý nghiệp vụ khi hủy hóa đơn chưa thanh toán hoặc khi điều trị đã được thực hiện.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
