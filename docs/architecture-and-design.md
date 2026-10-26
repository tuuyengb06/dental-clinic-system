# Tài liệu kiến trúc và thiết kế hệ thống

## 1. Mục đích và phạm vi

Tài liệu này đối chiếu kiến trúc và mô hình dữ liệu với source Django/React hiện tại. Các luồng Gemini gồm tóm tắt EMR, soạn lời mời nhắc tái khám chung và giải thích dịch vụ theo mô tả danh mục. Tích hợp Gemini tùy chọn; tóm tắt cần consent, khóa nhà cung cấp, còn nhắc SMS cần consent, cấu hình Twilio và lịch chạy riêng.

Sơ đồ ERD tập trung vào các model nghiệp vụ do Django quản lý. Các bảng nền tảng Django như `django_migrations`, `django_content_type`, `auth_group`, quyền, session và bảng quản trị không được vẽ đầy đủ. Các trường `id` tự tăng được lược khỏi sơ đồ để dễ đọc; các cột quan hệ và trường nghiệp vụ được ghi trực tiếp.

## 2. Kiến trúc hiện trạng

```mermaid
flowchart LR
    subgraph Client["Trình duyệt"]
        UI["React UI<br/>Vite build/dev"]
    end

    subgraph App["Ứng dụng backend Django"]
        API["Django REST Framework<br/>JWT authentication"]
        Auth["authentication<br/>User, token endpoints"]
        Clinic["clinic<br/>patient, service, schedule,<br/>invoice, payment, dashboard"]
        Appt["appointments<br/>appointment, EMR"]
        ReminderJob["Django management command<br/>send_follow_up_reminders"]
        Chat["ChatbotAPIView<br/>tra giá/lịch + giải thích dịch vụ"]
        API --> Auth
        API --> Clinic
        API --> Appt
        API --> Chat
    end

    DB[(Cơ sở dữ liệu<br/>SQLite mặc định<br/>SQL Server tùy cấu hình)]
    QR["img.vietqr.io<br/>dịch vụ tạo ảnh QR"]
    Bank["Tài khoản ngân hàng nhận<br/>ngoài hệ thống"]
    AI["Google Gemini API<br/>tóm tắt EMR + lời nhắc chung<br/>+ giải thích dịch vụ, tùy chọn"]
    Scheduler["Windows Task Scheduler<br/>gọi management command mỗi ngày"]
    Notify["Twilio SMS<br/>tùy chọn"]

    UI -->|"REST/JSON; JWT cho API nghiệp vụ"| API
    UI -. "Development: Vite proxy /api" .-> API
    ReminderJob --> DB
    Auth --> DB
    Clinic --> DB
    Appt --> DB
    Chat -->|"giá dịch vụ, bác sĩ,<br/>ca làm, lịch hẹn"| DB
    Chat -.->|"Chỉ tên + mô tả dịch vụ,<br/>không gửi câu hỏi/lịch sử chat"| AI
    UI -->|"Tải ảnh QR từ URL chứa thông tin chuyển khoản"| QR
    QR -. "QR hướng người chuyển tới tài khoản đã cấu hình" .-> Bank
    Appt -->|"EMR có consent; dữ liệu giảm định danh"| AI
    Scheduler --> ReminderJob
    ReminderJob -->|"Chỉ prompt chung, không có dữ liệu bệnh nhân"| AI
    ReminderJob -->|"Số điện thoại + ngày/lời mời"| Notify
```

### Thành phần đang chạy

| Thành phần | Trách nhiệm hiện tại | Căn cứ trong source |
|---|---|---|
| React/Vite | Đăng nhập, màn hình theo vai trò, tiếp nhận, lịch, EMR, Billing, chatbot và dashboard. Trong development, Vite proxy `/api` tới Django. | `frontend/src/main.jsx`, `frontend/vite.config.js` |
| Django REST Framework | REST API; JWT cho API nghiệp vụ; role/permission được kiểm tra ở các view. | `backend/dms/settings.py`, `backend/dms/urls.py`, `backend/clinic/urls.py`, `backend/appointments/urls.py` |
| `authentication` | User tùy biến kế thừa Django `AbstractUser`; cấp và refresh JWT. | `backend/authentication/models.py`, `backend/authentication/urls.py` |
| `clinic` | Người dùng phòng khám, bác sĩ, bệnh nhân, răng, dịch vụ, ca làm, lập hóa đơn, thanh toán và analytics. | `backend/clinic/models.py`, `backend/clinic/views.py`, `backend/clinic/dashboard.py` |
| `appointments` | Lịch hẹn đang được dùng trong API và hồ sơ khám EMR. | `backend/appointments/models.py`, `backend/appointments/views.py` |
| Chatbot | Tra giá/lịch từ ORM; khi được yêu cầu giải thích, gửi riêng tên và mô tả dịch vụ đã chọn tới Gemini. Không gửi câu hỏi/lịch sử chat hoặc hồ sơ bệnh nhân. | `backend/appointments/chatbot.py`, `backend/appointments/ai_services.py` |
| Tóm tắt EMR | Endpoint bác sĩ/Admin có phân quyền và giới hạn tần suất; chỉ chạy khi bệnh nhân có consent và Gemini được cấu hình. Trả bản nháp, không ghi đè hồ sơ. | `backend/appointments/views.py`, `backend/appointments/ai_services.py` |
| Nhắc tái khám | Management command đọc ngày tái khám và consent, tạo nội dung chung bằng Gemini rồi gửi qua Twilio; lịch chạy OS được cấu hình riêng. | `backend/appointments/management/commands/send_follow_up_reminders.py`, `backend/appointments/sms_services.py` |
| Database | SQLite mặc định; có thể chọn SQL Server qua biến môi trường `DMS_DB_ENGINE=mssql`. | `backend/dms/settings.py` |
| Tạo ảnh VietQR | Frontend tải ảnh từ `img.vietqr.io` với mã ngân hàng, số tài khoản, tên chủ tài khoản, số tiền và nội dung chuyển khoản trong URL. Không xác minh giao dịch. | `backend/clinic/views.py`, `frontend/src/main.jsx` |

### Ranh giới hiện trạng và điều kiện kích hoạt

- Tra giá và lịch trong chatbot không gọi AI. Giải thích dịch vụ mới gọi Gemini, chỉ với tên/mô tả công khai của dịch vụ đang hoạt động; câu hỏi gốc, lịch sử chat và dữ liệu bệnh nhân không được đưa vào prompt. Câu trả lời giới hạn theo nguồn và luôn kèm cảnh báo không thay thế tư vấn/chẩn đoán của bác sĩ. Cần cấu hình khóa Gemini và mô tả dịch vụ; thiếu mô tả thì hệ thống không gọi AI.
- Tóm tắt EMR gọi Gemini qua `POST /api/v1/medical-records/{id}/ai-summary/`; chỉ đọc hồ sơ đã lưu của bác sĩ được phân công hoặc Admin, cần `ai_processing_consent`, giới hạn 10 yêu cầu/giờ và trả kết quả chưa được lưu.
- Các yêu cầu Gemini dùng timeout kết nối 3 giây/chờ dữ liệu 5 giây mỗi lần; chỉ retry timeout, lỗi kết nối, HTTP 408/429 và 5xx một lần, cách nhau 0,5 giây. Lỗi timeout trả 504, dịch vụ tạm thời không khả dụng trả 503, dữ liệu đầu vào không hợp lệ trả 400; API AI trả mã lỗi, nội dung và cờ `retryable` để giao diện quyết định có hiện nút thử lại. Tóm tắt không ghi kết quả vào hồ sơ, bản nháp không tự gửi SMS.
- API nhắc tái khám chỉ cho Lễ tân/Admin, cần `sms_reminder_consent`, giới hạn 10 yêu cầu/người dùng/giờ; danh sách UI chỉ trả các trường cần để chọn hồ sơ. Bác sĩ không thể truy cập API danh sách/preview.
- Tóm tắt chỉ gửi chẩn đoán, kế hoạch điều trị, đơn thuốc, ghi chú, tên dịch vụ và mã răng. Backend lọc tên/mã bệnh nhân, số điện thoại, email, ngày sinh đã lưu và các định dạng ngày phổ biến nếu phát hiện; không gửi riêng thông tin ngày sinh, dị ứng, tiền sử, liên hệ hay lịch hẹn từ hồ sơ bệnh nhân. Đây là lọc theo mẫu, không bảo đảm dữ liệu được ẩn danh hoàn toàn; cần consent và duyệt chính sách xử lý dữ liệu của nhà cung cấp.
- Ngày tái khám được lưu trong `appointments.MedicalRecord.follow_up_date`; `Patient.sms_reminder_consent` và số điện thoại là điều kiện gửi. `FollowUpReminder` lưu trạng thái/mã Twilio và có unique key theo hồ sơ + ngày.
- Lệnh `python manage.py send_follow_up_reminders` cần được Windows Task Scheduler hoặc scheduler ngoài gọi hằng ngày; repository không tự đăng ký tác vụ hệ điều hành và tích hợp không hoạt động nếu thiếu biến môi trường Gemini/Twilio.
- Nội dung gửi SMS là lời mời chung có ngày tái khám, không gửi bệnh án tới Gemini. Lỗi gửi xác định được đánh dấu `FAILED`; kết quả Twilio không xác định thành `UNKNOWN` và không tự gửi lại.
- Luồng QR chỉ tạo QR và ghi nhận trạng thái chờ; đối soát hiện là thao tác nhân viên, không phải webhook ngân hàng.
- VietQR là dịch vụ ngoài dùng để dựng ảnh QR, không phải ngân hàng, cổng nhận tiền hay nguồn xác minh giao dịch.
- `docker-compose.yml` ở thư mục gốc dùng backend Django, frontend Nginx và SQLite trong volume `dental_data` cho demo local. Cấu hình này không phải triển khai production; chạy `docker compose` theo hướng dẫn README và cung cấp secret qua `.env`.
- `backend/schema.sql` là schema SQLite nền cũ gồm 13 bảng clinic ban đầu, không bao gồm đầy đủ các model/migration hiện tại; dùng migration Django làm nguồn chuẩn cho database mới/cập nhật.

## 3. ERD theo model hiện tại

Sơ đồ dưới đây phản ánh model Django sau các migration hiện có. Có hai model mang tên lịch hẹn:

1. `appointments.Appointment` là model được router `/api/v1/appointments/` và chatbot sử dụng.
2. `clinic.Appointment` là model cũ vẫn còn trong app/schema; không nhầm nó với model lịch hẹn hiện dùng trong API.

`TreatmentPlan`/`TreatmentItem` cũng là các model clinic còn trong schema; không phải các bảng thay thế cho luồng EMR hiện dùng trong `appointments.MedicalRecord`.

```mermaid
erDiagram
    AUTH_USER {
        int id PK
        string username UK
        string password
        string first_name
        string last_name
        string email
        datetime last_login
        bool is_staff
        bool is_active
        bool is_superuser
        string role
        string phone
        datetime date_joined
    }
    ROLE {
        int id PK
        string code UK
        string name
        string description
    }
    CLINIC_USER {
        int id PK
        int user_id FK,UK
        int role_id FK
        string phone
        datetime created_at
    }
    DOCTOR {
        int id PK
        int clinic_user_id FK,UK
        string license_number UK
        string specialization
        int experience_years
    }
    PATIENT {
        int id PK
        string patient_code UK
        string full_name
        string phone
        date date_of_birth
        string dentition_type
        string medical_history
        string allergies
        bool ai_processing_consent
        bool sms_reminder_consent
        datetime created_at
    }
    TOOTH {
        int id PK
        string code
        string dentition_type
        int display_order
    }
    TOOTH_CONDITION {
        int id PK
        int patient_id FK
        int tooth_id FK
        string condition
        string note
        datetime updated_at
    }
    SERVICE {
        int id PK
        string code UK
        string name
        string description
        decimal price
        int duration_minutes
        bool is_active
    }
    WORK_SCHEDULE {
        int id PK
        int doctor_id FK
        date work_date
        time start_time
        time end_time
    }
    APPOINTMENT {
        int id PK
        int patient_id FK
        int doctor_id FK
        int service_id FK
        datetime appointment_date
        string status
        string notes
        datetime created_at
    }
    MEDICAL_RECORD {
        int id PK
        int appointment_id FK,UK
        string diagnosis
        string treatment_plan
        string prescription
        string notes
        date follow_up_date
        datetime created_at
    }
    FOLLOW_UP_REMINDER {
        int id PK
        int medical_record_id FK
        date scheduled_for
        string status
        string provider_reference
        string error_message
        datetime created_at
        datetime updated_at
        datetime sent_at
    }
    MEDICAL_RECORD_TOOTH {
        int id PK
        int medicalrecord_id FK
        int tooth_id FK
    }
    MEDICAL_RECORD_SERVICE {
        int id PK
        int medicalrecord_id FK
        int service_id FK
    }
    LEGACY_CLINIC_APPOINTMENT {
        int id PK
        int patient_id FK
        int doctor_id FK
        string dentist_name
        string room
        datetime start_at
        datetime end_at
        string status
        string notes
    }
    TREATMENT_PLAN {
        int id PK
        int patient_id FK
        int dentist_id FK
        string title
        string status
        date start_date
        date end_date
        datetime created_at
    }
    TREATMENT_ITEM {
        int id PK
        int plan_id FK
        int appointment_id FK
        int service_id FK
        int tooth_id FK
        string procedure_name
        decimal cost
        string status
    }
    INVOICE {
        int id PK
        int patient_id FK
        int medical_record_id FK,UK
        string invoice_number UK
        decimal total_amount
        decimal paid_amount
        string status
        datetime issued_at
    }
    INVOICE_ITEM {
        int id PK
        int invoice_id FK
        int service_id FK
        string description
        int quantity
        decimal unit_price
        decimal amount
    }
    PAYMENT {
        int id PK
        int invoice_id FK
        decimal amount
        string method
        string status
        string bank_id
        string bank_account_number
        string bank_account_name
        datetime created_at
        datetime paid_at
        datetime cancelled_at
        int received_by_id FK
        int cancelled_by_id FK
    }
    BANK_TRANSFER_VERIFICATION {
        int id PK
        int payment_id FK,UK
        string reference UK
        int verified_by_id FK
        datetime verified_at
    }
    ACTIVE_INVOICE_PAYMENT {
        int id PK
        int invoice_id FK,UK
        int payment_id FK,UK
        datetime created_at
    }

    AUTH_USER ||--o| CLINIC_USER : "clinic profile"
    ROLE ||--o{ CLINIC_USER : "assigned role"
    CLINIC_USER ||--o| DOCTOR : "doctor profile"
    PATIENT ||--o{ APPOINTMENT : books
    DOCTOR ||--o{ APPOINTMENT : attends
    SERVICE o|--o{ APPOINTMENT : selected
    DOCTOR ||--o{ WORK_SCHEDULE : works
    APPOINTMENT ||--o| MEDICAL_RECORD : "has EMR"
    MEDICAL_RECORD ||--o{ FOLLOW_UP_REMINDER : "reminder attempts"
    MEDICAL_RECORD ||--o{ MEDICAL_RECORD_TOOTH : selects
    TOOTH ||--o{ MEDICAL_RECORD_TOOTH : selected
    MEDICAL_RECORD ||--o{ MEDICAL_RECORD_SERVICE : prescribes
    SERVICE ||--o{ MEDICAL_RECORD_SERVICE : prescribed
    PATIENT ||--o{ TOOTH_CONDITION : has
    TOOTH ||--o{ TOOTH_CONDITION : describes
    PATIENT ||--o{ LEGACY_CLINIC_APPOINTMENT : "legacy schedule"
    DOCTOR o|--o{ LEGACY_CLINIC_APPOINTMENT : "legacy assignment"
    PATIENT ||--o{ TREATMENT_PLAN : has
    DOCTOR ||--o{ TREATMENT_PLAN : supervises
    TREATMENT_PLAN ||--o{ TREATMENT_ITEM : contains
    LEGACY_CLINIC_APPOINTMENT o|--o{ TREATMENT_ITEM : references
    SERVICE o|--o{ TREATMENT_ITEM : based_on
    TOOTH o|--o{ TREATMENT_ITEM : targets
    PATIENT ||--o{ INVOICE : billed
    MEDICAL_RECORD o|--o| INVOICE : invoiced
    INVOICE ||--o{ INVOICE_ITEM : contains
    SERVICE o|--o{ INVOICE_ITEM : priced_as
    INVOICE ||--o{ PAYMENT : paid_by
    CLINIC_USER o|--o{ PAYMENT : receives
    AUTH_USER o|--o{ PAYMENT : cancels_qr
    PAYMENT ||--o| BANK_TRANSFER_VERIFICATION : verified
    AUTH_USER ||--o{ BANK_TRANSFER_VERIFICATION : verifies
    INVOICE ||--o| ACTIVE_INVOICE_PAYMENT : active_slot
    PAYMENT ||--o| ACTIVE_INVOICE_PAYMENT : occupies
```

### Quy tắc quan hệ đáng lưu ý

- `appointments.MedicalRecord.appointment` là one-to-one; một lịch có tối đa một EMR.
- `Invoice.medical_record` là one-to-one nullable; một EMR có tối đa một hóa đơn.
- Dịch vụ và răng được chọn trong EMR là quan hệ many-to-many, lưu qua bảng trung gian Django.
- `Payment` lưu lịch sử giao dịch; `ActiveInvoicePayment` là slot one-to-one bảo vệ việc chỉ có một giao dịch đang hiệu lực cho một hóa đơn. Slot được giải phóng khi QR pending bị hủy.
- `BankTransferVerification` là thông tin kiểm toán cho đối soát thủ công, một-một với Payment đã được xác minh; mã tham chiếu là duy nhất.
- Quan hệ/cột `SET_NULL`, nullable và các giá trị trạng thái phải được đọc cùng `backend/clinic/models.py` và `backend/appointments/models.py`; ERD tập trung thể hiện FK và cardinality, không mã hóa mọi `on_delete`.

## 4. Sequence cho các luồng AI tùy chọn

Các luồng dưới đây mô tả source hiện tại. Gemini và Twilio chỉ được gọi khi cấu hình credential; gửi SMS cần consent và một lịch chạy OS do đơn vị vận hành tự thiết lập. Không có API webhook ngân hàng trong các luồng này.

### 4.1 Tóm tắt hồ sơ bệnh án bằng AI

```mermaid
sequenceDiagram
    autonumber
    actor Dentist as Bác sĩ
    participant UI as React UI
    participant API as Django REST API / MedicalRecordViewSet
    participant DB as Database
    participant AI as Google Gemini API

    Note over Dentist,AI: Tùy chọn; cần ai_processing_consent và DMS_GEMINI_API_KEY
    Dentist->>UI: Bấm tạo bản nháp trong EMR
    UI->>API: POST /api/v1/medical-records/{id}/ai-summary/ (JWT, body rỗng)
    API->>API: Xác thực vai trò Dentist/Admin
    API->>DB: Lấy EMR theo queryset giới hạn hồ sơ bác sĩ được giao
    DB-->>API: EMR và consent của bệnh nhân
    API->>API: Từ chối nếu chưa có ai_processing_consent
    API->>API: Lọc mẫu tên/mã/điện thoại, email và định dạng ngày
    API->>AI: Gửi chẩn đoán, kế hoạch, toa, ghi chú, dịch vụ/răng đã lọc
    AI-->>API: Văn bản tóm tắt
    API-->>UI: Trả summary và provider=Gemini; không lưu vào DB
    UI-->>Dentist: Hiển thị bản nháp để bác sĩ tham khảo
```

Endpoint chỉ nhận body rỗng, giới hạn 10 yêu cầu/giờ, chỉ cho Admin hoặc bác sĩ đã được phân công xem hồ sơ và không lưu summary. Gemini nhận chẩn đoán, kế hoạch điều trị, toa thuốc, ghi chú, tên dịch vụ và mã răng đã lọc tên/mã bệnh nhân, điện thoại, email, ngày sinh lưu trong hồ sơ và định dạng ngày phổ biến; không nhận riêng ngày sinh, tiền sử, dị ứng, liên hệ hay lịch hẹn của bệnh nhân. Timeout sau số lần thử tối đa trả HTTP 504; dịch vụ tạm thời không khả dụng trả HTTP 503; thiếu cấu hình cũng trả HTTP 503 nhưng không retry; đầu vào không hợp lệ trả HTTP 400; phản hồi AI không dùng được trả HTTP 502. API lỗi có `code`, `detail` và `retryable`; giao diện cho phép thử lại thủ công khi lỗi được đánh dấu tạm thời. Mỗi request thử lại tối đa một lần, tổng cộng tối đa hai lần gọi Gemini. Việc lọc định danh là heuristic; không đảm bảo ẩn danh hoàn toàn. Summary có thể sai hoặc bỏ sót, không phải chẩn đoán/kết luận điều trị và cần bác sĩ đánh giá độc lập. Chỉ bật sau khi phòng khám phê duyệt consent và điều khoản xử lý dữ liệu sức khỏe của Gemini.

### 4.2 Sinh tin nhắn nhắc tái khám bằng AI

```mermaid
sequenceDiagram
    autonumber
    actor Patient as Bệnh nhân
    actor Dentist as Bác sĩ
    participant UI as React UI
    participant DB as Database
    participant Scheduler as Windows Task Scheduler
    participant Command as Django management command
    participant AI as Google Gemini API
    participant SMS as Twilio SMS

    Note over Dentist,SMS: Tùy chọn; cần sms_reminder_consent, DMS_GEMINI_* và DMS_TWILIO_*
    Dentist->>UI: Nhập ngày tái khám trong EMR
    UI->>DB: Lưu MedicalRecord.follow_up_date
    Note over Patient,DB: Nhân viên ghi sms_reminder_consent và số điện thoại ở hồ sơ bệnh nhân
    Scheduler->>Command: Chạy send_follow_up_reminders hằng ngày
    Command->>DB: Tìm follow_up_date đến hạn/quá hạn, có consent
    DB-->>Command: Các EMR và số điện thoại đủ điều kiện
    Command->>DB: Tạo/claim FollowUpReminder duy nhất theo EMR + ngày
    Command->>AI: Xin một câu mời chung; không gửi dữ liệu bệnh nhân
    AI-->>Command: Câu SMS ngắn, không có thông tin lâm sàng
    loop Mỗi hồ sơ đủ điều kiện
        Command->>SMS: Gửi số điện thoại + ngày tái khám + lời mời chung
        SMS-->>Command: Provider reference hoặc lỗi/kết quả không rõ
        Command->>DB: Ghi SENT, FAILED hoặc UNKNOWN
        SMS-->>Patient: Nhận SMS (nếu Twilio chấp nhận)
    end
```

Command gửi lời mời chung có ngày tái khám, không đưa hồ sơ lâm sàng hay thông tin nhận diện vào prompt Gemini. `--dry-run` chỉ đếm hồ sơ đủ điều kiện, không gửi và không tạo delivery record. Delivery `FAILED` có thể được thử lại ở lần chạy sau; `UNKNOWN` không tự retry để tránh SMS trùng, cần đối chiếu trong Twilio. Trạng thái `SENDING` cũ hơn 30 phút được chuyển `UNKNOWN`. Command không tạo lịch hệ điều hành: cần tự cấu hình Task Scheduler, kiểm thử `--dry-run`, xác nhận tuyến gửi/chi phí SMS tại Twilio và chỉ sau đó mới chạy thật. Nội dung Gemini được gửi tự động, không có bước duyệt thủ công trước khi gửi.

### 4.3 Lễ tân tạo bản nháp nhắc tái khám

```mermaid
sequenceDiagram
    autonumber
    actor Receptionist as Lễ tân
    participant UI as React UI
    participant API as Django REST API
    participant DB as Database
    participant AI as Google Gemini API

    Receptionist->>UI: Mở Follow-up reminders và chọn hồ sơ
    UI->>API: GET /api/v1/follow-up-appointments/ (JWT)
    API->>API: Xác thực vai trò Receptionist/Admin
    API->>DB: Lấy EMR có follow_up_date, không gồm lịch đã hủy
    DB-->>API: Ngày tái khám, lịch hẹn, bệnh nhân và SMS consent
    API-->>UI: Trả các trường cần thiết cho danh sách
    Receptionist->>UI: Bấm tạo bản nháp
    UI->>API: POST /api/ai/generate-reminder (medical_record_id)
    API->>DB: Đọc ngày tái khám và SMS consent từ hồ sơ
    API->>API: Từ chối nếu thiếu ngày hoặc consent
    API->>AI: System prompt + user prompt chỉ xin lời mời chung
    Note over API,AI: Không gửi ID hồ sơ, ngày, tên, mã, điện thoại hay dữ liệu lâm sàng
    AI-->>API: Một câu mời liên hệ phòng khám
    API->>API: Ghép ngày đã lưu; kiểm tra giới hạn một SMS 70 ký tự
    API-->>UI: Trả nội dung preview, sent=false
    UI-->>Receptionist: Xem trước và sao chép để tự gửi qua SMS/Zalo
```

Danh sách chỉ gồm hồ sơ EMR có ngày tái khám và lịch chưa hủy; các trường hiển thị được giới hạn cho mục đích chọn lịch. API tạo preview chỉ nhận `medical_record_id`, yêu cầu vai trò Lễ tân/Admin và SMS consent, giới hạn 10 yêu cầu/người dùng/giờ, rồi lấy ngày từ database thay vì tin dữ liệu do trình duyệt gửi. Gemini chỉ sinh lời mời tĩnh, không nhận ngày, tên, mã, điện thoại hay dữ liệu bệnh nhân; backend ghép ngày chính xác vào câu trả lời và từ chối nội dung vượt 70 đơn vị UTF-16. Timeout trả HTTP 504; lỗi kết nối/HTTP 429 hoặc 5xx kéo dài qua retry trả HTTP 503; thiếu cấu hình trả HTTP 503 không retry; đầu vào không hợp lệ trả HTTP 400; đầu ra không dùng được trả HTTP 502. Preview không lưu hoặc gửi tin nhắn; retry thủ công dùng lại hồ sơ đã chọn và không tạo bản ghi mới.

## 5. Kiểm tra nhất quán và giới hạn tài liệu

- Component diagram đã đối chiếu `INSTALLED_APPS`, URL routing, frontend Vite proxy, database settings, chatbot và VietQR URL builder.
- ERD được đối chiếu trực tiếp với các model Django và migration; phân biệt đúng hai model Appointment khác app.
- Hai sequence được đối chiếu với endpoint, command, model và service thực tế; các tích hợp Gemini/Twilio được ghi rõ là tùy chọn, cần cấu hình và consent.
- Tài liệu không thay thế migration/schema thực tế. Khi model thay đổi, cập nhật ERD cùng thay đổi model/migration và kiểm tra route/permission tương ứng.
- Chưa có quy ước tài liệu được nhóm xác nhận; cấu trúc hiện dùng Markdown + Mermaid để version-control, review bằng diff và render trên GitHub.

## 6. Nguồn đối chiếu trong repository

- `backend/dms/settings.py`, `backend/dms/urls.py`
- `backend/authentication/models.py`, `backend/authentication/urls.py`
- `backend/clinic/models.py`, `backend/clinic/urls.py`, `backend/clinic/views.py`, `backend/clinic/dashboard.py`
- `backend/appointments/models.py`, `backend/appointments/urls.py`, `backend/appointments/views.py`, `backend/appointments/chatbot.py`, `backend/appointments/ai_services.py`, `backend/appointments/sms_services.py`, `backend/appointments/management/commands/send_follow_up_reminders.py`
- `frontend/src/main.jsx`, `frontend/vite.config.js`
