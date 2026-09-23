# Prompt: Sinh hàm tính tổng hóa đơn điều trị nha khoa

## Kỹ thuật minh họa
Prompt sinh mã có ràng buộc input/output chặt chẽ, kiểm tra hợp lệ (validation) và bao phủ các trường hợp đặc biệt (edge cases) trong nghiệp vụ thanh toán y tế.

## Prompt sử dụng

[Instructions]
Viết hàm Python tính tổng tiền hóa đơn điều trị cho Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI.

[Context]
- Hệ thống cần tính toán chính xác tổng chi phí các thủ thuật/dịch vụ nha khoa, vật tư đính kèm và số tiền bệnh nhân cần thanh toán thực tế trước khi lưu hóa đơn hoặc tạo lịch trình trả góp.
- Mỗi dòng dịch vụ trong hóa đơn bao gồm: `service_id`, `quantity` (số lượng thực hiện/răng điều trị), `unit_price` (đơn giá dịch vụ).
- Hóa đơn có thể áp dụng số tiền giảm giá trực tiếp (`discount_amount`) hoặc khấu trừ số tiền bệnh nhân đã tạm ứng trước đó (`prepaid_amount`).

[Constraints]
- Tên hàm: `calculate_dental_invoice_total`.
- Tham số đầu vào:
  - `items`: `list[dict]`, mỗi `dict` đại diện cho một chỉ định dịch vụ/thủ thuật chứa ít nhất hai khóa: `quantity` (kiểu `int` hoặc `float`) và `unit_price` (kiểu `int` hoặc `float`).
  - `discount_amount`: `int` hoặc `float`, mặc định là `0`.
  - `prepaid_amount`: `int` hoặc `float`, mặc định là `0`.
- Kiểm tra tính hợp lệ (Validation & Raising `ValueError`):
  - Bắt buộc kiểm tra `quantity > 0` (số lượng lượt khám/răng phải lớn hơn 0).
  - Bắt buộc kiểm tra `unit_price >= 0` (đơn giá dịch vụ không được âm).
  - Bắt buộc kiểm tra `discount_amount >= 0` và `prepaid_amount >= 0` (tiền giảm giá và tiền tạm ứng không được âm).
- Logic xử lý chi phí:
  - Tính tổng chi phí dịch vụ ban đầu: $\text{gross\_total} = \sum (\text{quantity} \times \text{unit\_price})$.
  - Tính tổng chi phí sau khi giảm giá: $\text{after\_discount} = \max(0, \text{gross\_total} - \text{discount\_amount})$.
  - Tính số tiền thực tế bệnh nhân còn phải thanh toán đợt này: $\text{net\_payable} = \max(0, \text{after\_discount} - \text{prepaid\_amount})$.
- Hàm trả về một `dict` gồm 3 thông số: `gross_total`, `discount_amount`, `net_payable`.
- Sử dụng đầy đủ Type Hints (`typing`).
- Có Docstring chuẩn theo Google Python Style Guide.

[Output Format]
Chỉ trả về đoạn mã Python hoàn chỉnh, không giải thích thêm.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `18-Sinh-ham-tinh-tong-hoa-don-nha-khoa.md` thì file kết quả phải là `18-Sinh-ham-tinh-tong-hoa-don-nha-khoa_ket_qua.md`.