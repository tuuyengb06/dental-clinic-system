# 01. Requirements

## 1. Document Information
- Project: Dental Management System (DMS)
- Version: 1.0
- Date: 2026-09-08
- Authors: Nhóm phát triển DMS
- Reviewers: Quản lý phòng khám và đại diện người dùng

## 2. Problem Statement
Phòng khám hiện đang quản lý hồ sơ bệnh nhân bằng giấy, dẫn đến nguy cơ thất lạc hoặc hư hỏng thông tin. Việc đặt lịch thủ công dễ gây trùng lịch bác sĩ, trong khi nhân viên khó theo dõi tiến độ điều trị, lịch sử thủ thuật và công nợ của bệnh nhân. Hệ thống DMS được xây dựng để tập trung hóa dữ liệu và hỗ trợ quy trình khám chữa răng trên một nền tảng số.

## 3. Goals and Objectives
- Số hóa 100% hồ sơ bệnh nhân, bao gồm thông tin cá nhân, bệnh sử, lịch sử điều trị và tài liệu liên quan.
- Cung cấp sơ đồ răng tương tác cho bộ răng người lớn 32 răng và bộ răng trẻ em 20 răng.
- Quản lý lịch hẹn theo thời gian thực, hạn chế trùng lịch và giúp các vai trò liên quan theo dõi lịch làm việc.
- Quản lý xuyên suốt kế hoạch điều trị, thủ thuật, hóa đơn, thanh toán trả góp và đơn thuốc.
- Hỗ trợ lưu trữ ảnh X-quang dạng tệp đính kèm trong hồ sơ bệnh nhân.

## 4. Stakeholders and User Roles
| ID | Stakeholder / Role | Responsibilities | Needs |
|---|---|---|---|
| ACT-001 | Lễ tân | Tạo và cập nhật hồ sơ bệnh nhân; đặt, đổi, hủy và xác nhận lịch hẹn; lập hóa đơn và ghi nhận thanh toán | Tra cứu nhanh thông tin bệnh nhân, xem lịch trống theo thời gian thực và theo dõi công nợ |
| ACT-002 | Bác sĩ nha khoa | Khám bệnh; cập nhật sơ đồ răng; lập kế hoạch điều trị; ghi nhận thủ thuật; kê đơn thuốc và chỉ định X-quang | Xem đầy đủ lịch sử điều trị, đánh giá tình trạng từng răng và quản lý kế hoạch điều trị an toàn |
| ACT-003 | Phụ tá | Chuẩn bị ca điều trị; hỗ trợ cập nhật ghi chú và thủ thuật; tải lên ảnh X-quang theo hồ sơ | Truy cập thông tin cần thiết của ca đang xử lý và phối hợp với bác sĩ |
| ACT-004 | Quản lý phòng khám | Quản lý người dùng và phân quyền; theo dõi lịch, doanh thu, hóa đơn và công nợ; xem báo cáo hoạt động | Có dữ liệu tập trung, chính xác và khả năng giám sát vận hành phòng khám |

## 5. Scope
### 5.1 In Scope
- Quản lý bệnh nhân: tạo, tìm kiếm, cập nhật hồ sơ, bệnh sử, dị ứng và lịch sử điều trị.
- Lịch hẹn khám: tạo, cập nhật, xác nhận, hủy và tra cứu lịch theo bác sĩ, phòng và thời gian; kiểm tra trùng lịch.
- Sơ đồ răng tương tác (Tooth Chart): hiển thị và cập nhật tình trạng 32 răng người lớn hoặc 20 răng trẻ em.
- Kế hoạch điều trị và thủ thuật: lập kế hoạch, cập nhật trạng thái, ghi nhận chi tiết thủ thuật và tiến độ thực hiện.
- Kê đơn thuốc: tạo và quản lý đơn thuốc; cảnh báo khi thuốc được kê có khả năng gây dị ứng theo thông tin bệnh nhân.
- Hóa đơn và thanh toán trả góp: lập hóa đơn theo dịch vụ, ghi nhận các lần thanh toán, số dư và trạng thái công nợ.
- Upload ảnh X-quang: tải lên, lưu trữ, xem và liên kết ảnh X-quang với hồ sơ bệnh nhân hoặc lần khám.

### 5.2 Out of Scope
- Quản lý kho vật tư tiêu hao.
- Tích hợp trực tiếp với máy chụp X-quang phần cứng.
- Quản lý hoặc tích hợp bảo hiểm y tế nhà nước.

## 6. Functional Requirements
| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| REQ-F-001 | Quản lý hồ sơ bệnh nhân | High | Người dùng được phân quyền có thể tạo, tìm kiếm, xem và cập nhật hồ sơ; dữ liệu được lưu và tra cứu lại chính xác. |
| REQ-F-002 | Quản lý lịch hẹn | High | Hệ thống hiển thị lịch theo thời gian thực, kiểm tra xung đột bác sĩ/phòng và không cho tạo lịch trùng hợp lệ. |
| REQ-F-003 | Sơ đồ răng tương tác | High | Bác sĩ có thể chọn bộ răng 32 răng hoặc 20 răng trẻ em, xem và cập nhật tình trạng từng răng. |
| REQ-F-004 | Kế hoạch điều trị và thủ thuật | High | Bác sĩ có thể tạo kế hoạch, thêm thủ thuật, cập nhật trạng thái và xem tiến độ theo bệnh nhân. |
| REQ-F-005 | Kê đơn thuốc và cảnh báo dị ứng | High | Hệ thống lưu đơn thuốc và hiển thị cảnh báo rõ ràng khi thuốc có liên quan đến dị ứng đã ghi nhận. |
| REQ-F-006 | Hóa đơn và thanh toán trả góp | High | Người dùng có quyền có thể lập hóa đơn, ghi nhận nhiều lần thanh toán, tính số dư và hiển thị trạng thái công nợ. |
| REQ-F-007 | Upload ảnh X-quang | Medium | Người dùng có quyền có thể tải lên, xem và liên kết tệp ảnh X-quang với đúng hồ sơ bệnh nhân/lần khám. |
| REQ-F-008 | Phân quyền theo vai trò | High | Lễ tân, bác sĩ, phụ tá và quản lý chỉ truy cập được các chức năng phù hợp với vai trò. |

## 7. Non-Functional Requirements
| ID | Category | Requirement | Measure / Target |
|---|---|---|---|
| REQ-NF-001 | Security | Bảo vệ dữ liệu bệnh nhân và giới hạn truy cập theo vai trò. | 100% API/chức năng nghiệp vụ yêu cầu xác thực và kiểm tra phân quyền. |
| REQ-NF-002 | Performance | Tra cứu hồ sơ và lịch hẹn phải phản hồi nhanh trong điều kiện vận hành thông thường. | 95% yêu cầu đọc hoàn tất trong không quá 2 giây với quy mô dữ liệu dự kiến. |
| REQ-NF-003 | Availability | Dữ liệu lịch hẹn và thanh toán phải được cập nhật nhất quán. | Các thao tác ghi thành công hoặc thất bại toàn vẹn; không tạo giao dịch một phần. |
| REQ-NF-004 | Usability | Giao diện phù hợp cho thao tác hằng ngày của lễ tân, bác sĩ và phụ tá. | Các tác vụ chính có thể thực hiện trên giao diện web với thông báo lỗi và trạng thái rõ ràng. |
| REQ-NF-005 | Maintainability | Hệ thống được tách lớp rõ ràng và có API để frontend sử dụng. | Backend dùng Django REST Framework; frontend dùng React + TailwindCSS. |
| REQ-NF-006 | Data portability | Dữ liệu có thể chạy trên cơ sở dữ liệu phù hợp môi trường phát triển và triển khai. | Hỗ trợ PostgreSQL và SQLite thông qua cấu hình môi trường. |

## 8. Constraints and Assumptions
### Constraints
- Công nghệ backend: Django REST Framework.
- Công nghệ frontend: React và TailwindCSS.
- Cơ sở dữ liệu: PostgreSQL hoặc SQLite.
- Ảnh X-quang được upload dưới dạng tệp; hệ thống không điều khiển trực tiếp phần cứng chụp ảnh.
- Người dùng phải đăng nhập và được cấp vai trò trước khi sử dụng các chức năng nghiệp vụ.

### Assumptions
- Phòng khám có kết nối mạng và thiết bị phù hợp để sử dụng ứng dụng web.
- Thông tin dị ứng do nhân viên y tế thu thập và cập nhật là cơ sở để hệ thống đưa ra cảnh báo.
- Dữ liệu bệnh nhân, lịch hẹn, hóa đơn và đơn thuốc được nhập bởi người dùng có trách nhiệm.
- Quy trình nghiệp vụ và quyền truy cập cụ thể sẽ được phòng khám xác nhận trước khi triển khai chính thức.

## 9. Open Questions and Risks
| ID | Question / Risk | Owner | Status | Resolution |
|---|---|---|---|---|
| Q-001 | Chưa xác định định dạng và giới hạn dung lượng tệp X-quang. | Quản lý phòng khám | Open | Xác nhận trước khi triển khai và cấu hình giới hạn upload phù hợp. |
| Q-002 | Dữ liệu dị ứng không đầy đủ có thể làm giảm hiệu quả cảnh báo thuốc. | Bác sĩ nha khoa | Open | Chuẩn hóa trường dị ứng và bắt buộc xác nhận khi tiếp nhận bệnh nhân. |
| Q-003 | Quy tắc thanh toán trả góp có thể khác nhau theo chính sách phòng khám. | Quản lý phòng khám | Open | Chốt quy tắc kỳ hạn, hạn thanh toán và cách tính số dư trong thiết kế chi tiết. |

## 10. Requirements Traceability
| Requirement ID | Use Case / User Story | Design Reference | Test Reference |
|---|---|---|---|
| REQ-F-001 | US-01: Lễ tân quản lý hồ sơ bệnh nhân | TBD | TBD |
| REQ-F-002 | US-02: Lễ tân đặt lịch không trùng | TBD | TBD |
| REQ-F-003 | US-03: Bác sĩ cập nhật Tooth Chart | TBD | TBD |
| REQ-F-004 | US-04: Bác sĩ theo dõi kế hoạch điều trị | TBD | TBD |
| REQ-F-005 | US-05: Bác sĩ kê đơn an toàn | TBD | TBD |
| REQ-F-006 | US-06: Lễ tân ghi nhận thanh toán trả góp | TBD | TBD |
| REQ-F-007 | US-07: Phụ tá tải ảnh X-quang | TBD | TBD |
| REQ-F-008 | US-08: Quản lý phân quyền người dùng | TBD | TBD |

## 11. Approval
- Prepared by: Nhóm phát triển DMS
- Reviewed by: Quản lý phòng khám và đại diện người dùng
- Approved by: TBD
- Approval date: TBD

STATUS: PASS
