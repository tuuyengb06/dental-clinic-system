# Dental Management System (DMS)

MVP runnable cho phòng khám nha khoa, gồm Django REST Framework backend và React/Vite frontend.

## 1. Cài đặt yêu cầu

- Python 3.11 hoặc mới hơn
- Node.js 20 hoặc mới hơn
- npm 10 hoặc mới hơn

## 2. Khởi chạy backend

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_dental_data
python manage.py runserver 8000
```

Backend chạy tại `http://127.0.0.1:8000`.

Kiểm tra nhanh: mở `http://127.0.0.1:8000/api/v1/health/` và xác nhận response có `status: ok`.

## 3. Khởi chạy frontend

Mở một PowerShell mới:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Mở URL Vite hiển thị trong terminal, thường là `http://127.0.0.1:5173`.

Frontend tự gọi API backend. Nếu backend chưa chạy, giao diện vẫn hiển thị demo data để chụp ảnh bố cục; trạng thái góc trên sẽ ghi `Demo data` thay vì `Live API`.

## 4. Dữ liệu demo

Lệnh `seed_dental_data` tạo:

- 32 mã răng người lớn `A01` đến `A32`.
- 20 mã răng trẻ em `C01` đến `C20`.
- Bệnh nhân demo `DMS-0001` và `DMS-0002`.
- Lịch hẹn và hóa đơn mẫu.

## 5. API chính

- `GET/POST /api/v1/patients/`
- `GET /api/v1/patients/{id}/tooth_chart/`
- `PUT /api/v1/patients/{id}/tooth_chart/`
- `GET/POST /api/v1/appointments/`
- `POST /api/v1/appointments/{id}/confirm/`
- `POST /api/v1/appointments/{id}/cancel/`
- `GET/POST /api/v1/invoices/`
- `POST /api/v1/invoices/{id}/pay/`
- `GET /api/v1/health/`

## 6. Build kiểm tra

```powershell
cd frontend
npm run build
```

Backend có thể kiểm tra bằng:

```powershell
cd backend
python manage.py check
```

## 7. Chụp ảnh minh chứng

1. Chạy backend ở một terminal và frontend ở terminal thứ hai.
2. Mở `http://127.0.0.1:5173`.
3. Chụp Dashboard.
4. Chọn `Patients` để chụp danh sách hồ sơ.
5. Chọn `Tooth chart`, thử `Adult · 32` và `Child · 20`, chụp cả hai trạng thái.
6. Chọn `Appointments` và `Billing` để chụp lịch cùng công nợ.

## Phạm vi MVP

Đã có giao diện và API nền cho patient, appointment, tooth chart, invoice/payment và health check. Prescription allergy check, radiograph upload thật, treatment plan chi tiết và RBAC đầy đủ vẫn là các bước tiếp theo trong `docs/KN2/03_implementation_plan.md`.
