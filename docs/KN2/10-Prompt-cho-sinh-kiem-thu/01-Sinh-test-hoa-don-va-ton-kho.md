# Prompt: Sinh test cho hóa đơn và tồn kho nha khoa

## Kỹ thuật minh họa

Prompt sinh kiểm thử: nghiệp vụ + loại test cụ thể + công cụ test.

## Prompt sử dụng

[Instructions]

Viết test case bằng `pytest` cho nghiệp vụ hóa đơn dịch vụ nha khoa và tồn kho vật tư trong hệ thống quản lý nha khoa.

[Business Rules]

- Hóa đơn ghi nhận các dịch vụ nha khoa đã được xác nhận; tổng tiền được tính từ số lượng và đơn giá của từng dịch vụ.
- Khi lượng vật tư sử dụng trong hồ sơ điều trị được xác nhận, tồn kho giảm theo lượng đã sử dụng.
- Không cho ghi nhận sử dụng vật tư vượt quá tồn kho.
- Khi sửa lượng vật tư đã sử dụng, tồn kho chỉ thay đổi theo phần chênh lệch so với lượng đã ghi nhận trước đó.
- Nếu lượng sử dụng giảm, phần chênh lệch được cộng lại vào tồn kho; nếu tăng, chỉ phần tăng thêm bị trừ.
- Khi hủy ghi nhận sử dụng vật tư trước khi điều trị được thực hiện, tồn kho được hoàn lại đúng lượng đã trừ.
- Không tự hoàn lại vật tư đã thực sự tiêu hao chỉ vì hóa đơn bị hủy hoặc điều chỉnh thanh toán.
- Không cho số lượng dịch vụ hoặc lượng vật tư sử dụng nhỏ hơn hoặc bằng 0.

[Test Requirements]

- Bao phủ happy path, edge case và error case.
- Mỗi test có tên rõ nghĩa.
- Dùng dữ liệu mẫu giả lập: dịch vụ Trám răng Composite, đơn giá 350000 đồng; vật tư Composite có tồn kho ban đầu 12 đơn vị.
- Tách rõ nghiệp vụ lập/thanh toán hóa đơn với nghiệp vụ ghi nhận tiêu hao vật tư; không giảm tồn kho chỉ vì hóa đơn được thanh toán.
- Không phụ thuộc CSDL thật; có thể dùng object giả hoặc fixture đơn giản.
- Kiểm tra kết quả cụ thể gồm tổng tiền hóa đơn và số lượng tồn kho sau mỗi thao tác.

[Output Format]

Trả về code `pytest` hoàn chỉnh gồm:

1. Fixture dữ liệu mẫu.
2. Test tạo hóa đơn dịch vụ nha khoa hợp lệ.
3. Test từ chối ghi nhận sử dụng vật tư vượt tồn kho.
4. Test sửa lượng vật tư đã sử dụng theo hướng tăng và giảm, bảo đảm chỉ cập nhật phần chênh lệch.
5. Test hủy ghi nhận sử dụng vật tư trước khi điều trị và kiểm tra tồn kho được hoàn đúng một lần.
6. Test xác nhận hủy hóa đơn không tự hoàn vật tư đã thực sự tiêu hao.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
