# Prompt: So sánh prompt cơ bản và prompt có cấu trúc

## Kỹ thuật minh họa

Phân tích khác biệt chất lượng giữa prompt thiếu cấu trúc và prompt có cấu trúc.

## Prompt sử dụng

[Instructions]

So sánh hai prompt dưới đây cho cùng tác vụ sinh SQL báo cáo doanh thu của phòng khám nha khoa. Hãy phân tích vì sao prompt có cấu trúc có khả năng tạo ra kết quả rõ ràng và đáng tin cậy hơn.

[Context]

- Dự án là hệ thống quản lý nha khoa có tích hợp AI.
- CSDL demo có các bảng dự kiến: patients, appointments, dental_services, treatment_records, invoices, invoice_items, inventory_items.
- Sinh viên cần học cách đánh giá chất lượng prompt, không chỉ dựa vào việc kết quả trông có vẻ đúng.
- Báo cáo doanh thu cần dùng dữ liệu tổng hợp, không hiển thị thông tin định danh hoặc hồ sơ sức khỏe của bệnh nhân.

[Input Data]

Prompt A:

```text
Viết SQL thống kê doanh thu phòng khám tháng này.
```

Prompt B:

```text
Bạn là lập trình viên backend. Viết một truy vấn SQL cho SQLite để thống kê doanh thu theo ngày trong tháng hiện tại của phòng khám nha khoa.

Dữ liệu nằm trong bảng invoices(
    id,
    patient_id,
    invoice_date,
    status,
    payment_method,
    discount_amount,
    total_amount
).

invoice_date được lưu theo định dạng ISO 8601. Chỉ tính hóa đơn có status = 'paid'. total_amount là tổng tiền trước khi giảm giá; net_revenue được tính bằng total_amount - discount_amount. Nếu discount_amount có thể NULL, hãy xử lý theo cách an toàn và nêu rõ giả định.

Trả về đúng các cột: sale_date, invoice_count, gross_revenue, discount_total, net_revenue. Không nối với bảng patients hoặc trả về dữ liệu có thể định danh bệnh nhân. Sắp xếp theo sale_date tăng dần.

Chỉ trả về SQL và giải thích ngắn các giả định.
```

[Constraints]

- Không cần chạy SQL.
- Tập trung vào các thành phần prompt: Instructions, Context, Input Data/Constraints, Examples, Output Format.
- Phân tích mức độ xác định của hệ quản trị CSDL, cấu trúc dữ liệu, điều kiện lọc, cách tính và định dạng kết quả.
- Chỉ ra rủi ro nếu dùng Prompt A trong dự án thật, bao gồm nguy cơ hiểu sai định nghĩa doanh thu hoặc vô tình truy vấn dữ liệu bệnh nhân không cần thiết.
- Không khẳng định Prompt B chắc chắn đúng nếu vẫn còn giả định hoặc chi tiết cần xác minh trong lược đồ thực tế.

[Output Format]

Trả lời bằng bảng Markdown gồm các cột:

- Tiêu chí
- Prompt A
- Prompt B
- Nhận xét

Sau bảng, viết phần kết luận từ 5 đến 7 câu cho sinh viên.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
