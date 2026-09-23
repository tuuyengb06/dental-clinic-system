# Prompt: Sinh test cho hóa đơn điều trị và tồn kho vật tư nha khoa

## Kỹ thuật minh họa
Prompt sinh kiểm thử: Mã nguồn / Nghiệp vụ y tế + Loại test cụ thể + Framework / Tool test.

## Prompt sử dụng

[Instructions]
Viết bộ test cases tự động bằng `pytest` cho nghiệp vụ Lập hóa đơn điều trị và Trừ/Hoàn tồn kho vật tư y tế trong Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI.

[Business Rules]
- Khi tạo hóa đơn điều trị đã thanh toán, tồn kho vật tư tiêu hao (ví dụ: bộ mắc cài, trụ implant, lọ thuốc tê...) giảm tương ứng theo số lượng chỉ định.
- Không cho phép lập hóa đơn hoặc xuất sử dụng số lượng vật tư vượt quá tồn kho hiện có trong phòng khám.
- Khi chỉnh sửa hóa đơn điều trị đã thanh toán (tăng/giảm số lượng vật tư sử dụng), số lượng tồn kho chỉ điều chỉnh theo đúng phần chênh lệch (delta).
- Khi hủy hóa đơn điều trị đã thanh toán, số lượng vật tư y tế đã khấu trừ được cộng hoàn trả chính xác về kho.
- Bắt buộc kiểm tra: Số lượng vật tư (`quantity`) không được $\le 0$.

[Test Requirements]
- Bao phủ đầy đủ các trường hợp: Happy path (luồng chuẩn), Edge case (trường hợp biên) và Error case (xử lý ngoại lệ).
- Mỗi hàm test phải có tên rõ nghĩa, tuân thủ chuẩn đặt tên `test_<chức_năng>_<kịch_bản>_<kết_quả_kỳ_vọng>`.
- Dữ liệu mẫu sử dụng trong test:
  - Vật tư: **"Mắc cài Kim loại 3M"**, Mã: `VT-3M-01`, Đơn giá: `350,000 VNĐ`, Tồn kho ban đầu: `12 bộ`.
- Không phụ thuộc vào CSDL thật; sử dụng `pytest.fixture` hoặc mock objects đơn giản để giả lập dữ liệu trong bộ nhớ.

[Output Format]
Trả về mã nguồn Python hoàn chỉnh sử dụng `pytest` gồm:
1. `pytest.fixture` khởi tạo dữ liệu mẫu vật tư y tế và phòng khám.
2. Test case tạo hóa đơn điều trị và kiểm tra khấu trừ tồn kho.
3. Test case ném lỗi khi xuất vượt quá tồn kho.
4. Test case sửa hóa đơn điều trị (tăng/giảm số lượng vật tư) và kiểm tra cập nhật tồn kho theo chênh lệch.
5. Test case hủy hóa đơn điều trị và kiểm tra hoàn trả vật tư về kho.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `22-Sinh-test-hoa-don-ton-kho-nha-khoa.md` thì file kết quả phải là `22-Sinh-test-hoa-don-ton-kho-nha-khoa_ket_qua.md`.