# UML hệ thống quản lý nha khoa tích hợp AI

## 1. Use Case Diagram (Mermaid)

```mermaid
flowchart LR
    Admin["Quản trị viên"]
    Receptionist["Lễ tân"]
    Dentist["Bác sĩ nha khoa"]
    Assistant["Phụ tá nha khoa"]
    Owner["Chủ phòng khám"]
    Patient["Bệnh nhân/khách chatbot"]

    subgraph System["Hệ thống quản lý nha khoa"]
        Login([Đăng nhập])
        ManageUsers([Quản lý người dùng và vai trò])
        ManagePatient([Quản lý hồ sơ bệnh nhân])
        ManageAppointment([Quản lý lịch hẹn])
        ManageTreatment([Ghi nhận hồ sơ khám])
        ManagePlan([Lập kế hoạch điều trị])
        ManageService([Quản lý dịch vụ nha khoa])
        ManageInvoice([Lập hóa đơn và thanh toán])
        ManageInventory([Theo dõi vật tư])
        ViewReport([Xem hoặc xuất báo cáo tổng hợp])
        FAQ([Chatbot trả lời thông tin dịch vụ đã duyệt])
        AISummary([AI hỗ trợ tóm tắt thông tin khám])
        ReviewAI([Bác sĩ xem xét/xác nhận nội dung AI])
        AskData([Hỏi đáp dữ liệu hoạt động theo quyền])
    end

    Admin --> Login
    Admin --> ManageUsers
    Admin --> ManageService
    Receptionist --> Login
    Receptionist --> ManagePatient
    Receptionist --> ManageAppointment
    Receptionist --> ManageInvoice
    Dentist --> Login
    Dentist --> ManagePatient
    Dentist --> ManageTreatment
    Dentist --> ManagePlan
    Dentist --> AISummary
    Dentist --> ReviewAI
    Assistant --> Login
    Assistant --> ManageTreatment
    Owner --> Login
    Owner --> ViewReport
    Owner --> AskData
    Patient --> FAQ
    AISummary -. "cần bác sĩ rà soát" .-> ReviewAI
```

## 2. Class Diagram (Mermaid)

```mermaid
classDiagram
    class User {
      +int id
      +string username
      +string status
    }
    class Role {
      +int id
      +string name
    }
    class Patient {
      +int id
      +string patientCode
      +string contactData
    }
    class Appointment {
      +int id
      +datetime scheduledAt
      +string status
    }
    class DentalService {
      +int id
      +string serviceCode
      +string name
      +int price
      +string status
    }
    class TreatmentRecord {
      +int id
      +datetime occurredAt
      +string clinicalNotes
    }
    class TreatmentPlan {
      +int id
      +string content
      +string status
    }
    class Invoice {
      +int id
      +datetime invoiceDate
      +string status
      +int totalAmount
    }
    class InvoiceItem {
      +int id
      +int quantity
      +int unitPrice
    }
    class Payment {
      +int id
      +int amount
      +string method
      +string status
    }
    class InventoryItem {
      +int id
      +string itemCode
      +string unit
      +float stockQuantity
    }
    class InventoryMovement {
      +int id
      +float quantityDelta
      +string reason
      +string idempotencyKey
    }
    class AIRequest {
      +int id
      +string requestType
      +string status
      +datetime createdAt
    }
    class AIReportRequest {
      +int id
      +string period
      +string status
    }

    User "0..*" -- "0..*" Role : assigned
    Patient "1" -- "0..*" Appointment : books
    User "1" -- "0..*" Appointment : assigned staff
    Patient "1" -- "0..*" TreatmentRecord : has
    User "1" -- "0..*" TreatmentRecord : author
    Appointment "0..1" -- "0..*" TreatmentRecord : may link
    TreatmentRecord "0..*" -- "0..*" DentalService : records
    TreatmentRecord "1" -- "0..*" TreatmentPlan : has
    Patient "1" -- "0..*" Invoice : billed
    Invoice "1" -- "1..*" InvoiceItem : contains
    DentalService "1" -- "0..*" InvoiceItem : referenced
    Invoice "1" -- "0..*" Payment : paid by
    InventoryItem "1" -- "0..*" InventoryMovement : movement history
    TreatmentRecord "0..1" -- "0..*" InventoryMovement : may cause
    User "1" -- "0..*" AIRequest : requests
    User "0..1" -- "0..*" AIRequest : reviews
    User "1" -- "0..*" AIReportRequest : requests
```

## 3. Giải thích quan hệ và giả định

- Người dùng có thể có nhiều vai trò; hồ sơ bệnh nhân, lịch hẹn và ghi chú khám chỉ truy cập theo quyền. Sơ đồ không thể hiện chính sách chi tiết — cần ma trận authz.
- Lịch hẹn có thể liên kết hồ sơ khám; một hồ sơ có thể có nhiều dịch vụ/kế hoạch, tùy quy tắc lưu lịch sử.
- Hóa đơn chứa dòng dịch vụ và có thể có nhiều lần ghi nhận thanh toán; quy tắc thanh toán nhiều đợt, hủy/hoàn cần xác nhận.
- Biến động vật tư lưu lịch sử; cập nhật snapshot cùng movement phải transaction và idempotent. Việc hủy hóa đơn không tự động hoàn vật tư đã tiêu hao.
- `AIRequest` là tác vụ hỗ trợ; `reviewer` thể hiện việc con người rà soát, không tạo quyền để AI tự chẩn đoán hoặc tự cập nhật hồ sơ. `AIReportRequest` chỉ nên dùng dữ liệu tổng hợp theo quyền.
- Dùng giá nguyên đồng trong minh họa; kiểu số lượng vật tư, retention, actor khách hàng và các thuộc tính cần được xác nhận với thiết kế thật.
