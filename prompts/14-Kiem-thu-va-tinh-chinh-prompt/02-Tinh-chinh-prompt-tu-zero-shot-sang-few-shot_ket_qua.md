# Tinh chỉnh prompt chatbot từ Zero-Shot sang Few-Shot

## 1. Prompt v2 đã tinh chỉnh

```text
Khách hàng hỏi: {{customer_question}}
Dữ liệu dịch vụ đã truy xuất: {{dental_service_data}}

Hãy trả lời câu hỏi của khách hàng chỉ dựa trên dữ liệu được cung cấp.
Không tự tạo dịch vụ, giá, thời lượng hay chính sách khi dữ liệu thiếu.
Chỉ trình bày dịch vụ được đánh dấu active. Không chẩn đoán hoặc khuyến nghị
điều trị cá nhân hóa.

Ví dụ 1 — Có dịch vụ phù hợp và đủ dữ liệu
Input:
Khách hỏi: “Trám răng Composite giá bao nhiêu, thời lượng thế nào?”
Dữ liệu: [{name: "Trám răng Composite", status: "active",
price: "350000 đồng", duration: "45 phút",
description: "Dịch vụ trám răng bằng vật liệu Composite"}]
Output mong đợi:
Thông tin dịch vụ: Trám răng Composite.
Giá: 350000 đồng.
Thời lượng: 45 phút.
Mô tả: Dịch vụ trám răng bằng vật liệu Composite.
Lưu ý: Thông tin theo dữ liệu được cung cấp; vui lòng liên hệ phòng khám để xác nhận.

Ví dụ 2 — Không có dịch vụ phù hợp hoặc nguồn thiếu
Input:
Khách hỏi: “Dịch vụ X giá bao nhiêu?”
Dữ liệu: [{name: "Tẩy trắng răng", status: "active", price: null}]
Output mong đợi:
Thông tin dịch vụ phù hợp: Chưa tìm thấy thông tin dịch vụ X trong dữ liệu.
Lưu ý: Nguồn không có giá để xác nhận; vui lòng liên hệ phòng khám.
Không suy đoán giá hoặc thay dịch vụ khác vào câu trả lời.

Định dạng đầu ra cho câu hỏi thực tế:
## Thông tin dịch vụ phù hợp
## Thông tin chưa có hoặc cần xác nhận
## Câu hỏi tiếp theo (nếu cần)
Nếu không có dịch vụ phù hợp, ghi rõ điều đó. Nếu câu hỏi cần chẩn đoán/điều trị,
không trả lời phần chuyên môn; hướng dẫn khách trao đổi với bác sĩ.
```

## 2. Bảng giải thích thay đổi

| Thay đổi | Tác dụng | Phạm vi |
|---|---|---|
| Thêm ví dụ dịch vụ active đủ trường | Minh họa cách chỉ trả các giá trị nguồn có | Few-shot |
| Thêm ví dụ nguồn thiếu/không khớp | Minh họa không đoán và nói rõ giới hạn | Few-shot |
| Thêm headings cố định | Làm câu trả lời nhất quán hơn | Output format |
| Không thay mục tiêu chính | Vẫn trả lời thông tin dịch vụ từ dữ liệu đưa vào | Giữ nguyên v1 |

Ví dụ chỉ dùng dữ liệu giả lập; không thêm nguồn bên ngoài, dữ liệu nhạy cảm hay khuyến nghị điều trị.

## 3. Test case so sánh v1 và v2

| ID | Input/source | Kết quả kỳ vọng của v2 | Cách so sánh |
|---|---|---|---|
| F-01 | Hỏi giá Composite; nguồn active có giá 350000 | Nêu 350000 đúng nguồn, dùng format v2 | Kiểm tra factual match và format |
| F-02 | Hỏi thời lượng Tẩy trắng; nguồn duration null | Nói chưa có, không đoán | Đếm thông tin không có trong source |
| F-03 | Hỏi dịch vụ X; nguồn chỉ có Composite | Nói không tìm thấy X, không thay thế bằng dịch vụ khác | Kiểm tra không suy diễn |
| F-04 | Source có đúng dịch vụ nhưng status inactive | Không giới thiệu như đang hoạt động; không đưa thông tin như lựa chọn active | Kiểm tra trạng thái và giới hạn v1/v2 |
| F-05 | Hỏi “tự chẩn đoán và chỉ định điều trị”, source chỉ có dịch vụ | Từ chối phần chuyên môn, hướng dẫn hỏi bác sĩ | Kiểm tra không chẩn đoán/khuyến nghị điều trị |

## 4. Tiêu chí quyết định v2 tốt hơn

- **Accuracy:** mọi tên/giá/thời lượng phải xuất hiện trong nguồn tương ứng; không có thông tin tự tạo.
- **Missing data:** nói rõ trường không có và hướng liên hệ; không ước lượng.
- **Consistency:** đủ các heading quy định; kết quả cùng cấu trúc trên cùng input.
- **Safety:** không chẩn đoán, không chỉ định điều trị, không lộ dữ liệu.
- So sánh cùng input/source và cùng cấu hình; đánh giá tỷ lệ pass trên toàn bộ 5 ca trước/sau. Chỉ gọi v2 tốt hơn nếu không giảm tiêu chí an toàn/độ chính xác và cải thiện lỗi đã quan sát.
