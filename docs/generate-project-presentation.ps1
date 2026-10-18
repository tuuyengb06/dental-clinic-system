$ErrorActionPreference = "Stop"

function Get-Color([string]$Hex) {
    $value = $Hex.TrimStart("#")
    $red = [Convert]::ToInt32($value.Substring(0, 2), 16)
    $green = [Convert]::ToInt32($value.Substring(2, 2), 16)
    $blue = [Convert]::ToInt32($value.Substring(4, 2), 16)
    return $red + 256 * $green + 65536 * $blue
}

$script:Palette = @{
    Background = Get-Color "#F7F4EC"
    Ink = Get-Color "#153F3A"
    Green = Get-Color "#17685D"
    Mint = Get-Color "#E7F1EC"
    Gold = Get-Color "#D4A64A"
    Coral = Get-Color "#CF755F"
    Muted = Get-Color "#657875"
    White = Get-Color "#FFFFFF"
    Dark = Get-Color "#102D2B"
    Line = Get-Color "#DCE4DE"
}

function Add-Shape($Slide, [double]$X, [double]$Y, [double]$Width, [double]$Height, [int]$Fill, [bool]$Rounded = $false) {
    $shapeType = 1
    if ($Rounded) { $shapeType = 5 }
    $shape = $Slide.Shapes.AddShape($shapeType, $X, $Y, $Width, $Height)
    $shape.Fill.Solid()
    $shape.Fill.ForeColor.RGB = $Fill
    $shape.Line.Visible = 0
    return $shape
}

function Add-Text($Slide, [double]$X, [double]$Y, [double]$Width, [double]$Height, [string]$Text, [double]$Size, [int]$Color, [bool]$Bold = $false, [int]$Alignment = 1) {
    $shape = $Slide.Shapes.AddTextbox(1, $X, $Y, $Width, $Height)
    $shape.Fill.Visible = 0
    $shape.Line.Visible = 0
    $shape.TextFrame.MarginLeft = 0
    $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0
    $shape.TextFrame.MarginBottom = 0
    $shape.TextFrame.WordWrap = -1
    $shape.TextFrame.AutoSize = 0
    $shape.TextFrame.TextRange.Text = $Text
    $shape.TextFrame.TextRange.Font.Name = "Aptos"
    $shape.TextFrame.TextRange.Font.Size = $Size
    $shape.TextFrame.TextRange.Font.Color.RGB = $Color
    $shape.TextFrame.TextRange.Font.Bold = [int]$Bold
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment = $Alignment
    $shape.TextFrame.TextRange.ParagraphFormat.SpaceAfter = 4
    return $shape
}

function Add-Chip($Slide, [double]$X, [double]$Y, [double]$Width, [string]$Text, [int]$Fill, [int]$Color) {
    [void](Add-Shape $Slide $X $Y $Width 22 $Fill $true)
    [void](Add-Text $Slide ($X + 6) ($Y + 3) ($Width - 12) 15 $Text 9 $Color $true 2)
}

function Add-Card($Slide, [double]$X, [double]$Y, [double]$Width, [double]$Height, [string]$Title, [string]$Body, [int]$Accent) {
    [void](Add-Shape $Slide $X $Y $Width $Height $script:Palette.White $true)
    [void](Add-Shape $Slide $X $Y 5 $Height $Accent)
    [void](Add-Text $Slide ($X + 15) ($Y + 11) ($Width - 27) 24 $Title 14 $script:Palette.Ink $true)
    [void](Add-Text $Slide ($X + 15) ($Y + 42) ($Width - 27) ($Height - 47) $Body 11 $script:Palette.Muted)
}

function Add-Image($Slide, [string]$Path, [double]$X, [double]$Y, [double]$Width, [double]$Height) {
    [void](Add-Shape $Slide ($X - 4) ($Y - 4) ($Width + 8) ($Height + 8) $script:Palette.White $true)
    $null = $Slide.Shapes.AddPicture($Path, 0, -1, $X, $Y, $Width, $Height)
}

function Add-Slide($Presentation, [string]$Section, [string]$Title, [string]$Subtitle) {
    $slide = $Presentation.Slides.Add($Presentation.Slides.Count + 1, 12)
    $slide.Background.Fill.ForeColor.RGB = $script:Palette.Background
    $titleSize = 25
    if ($Title.Length -gt 43) { $titleSize = 22 }
    [void](Add-Text $slide 42 20 850 18 $Section.ToUpper() 9 $script:Palette.Green $true)
    [void](Add-Text $slide 42 45 876 40 $Title $titleSize $script:Palette.Ink $true)
    [void](Add-Text $slide 44 91 865 27 $Subtitle 11 $script:Palette.Muted)
    [void](Add-Shape $slide 42 511 876 1 $script:Palette.Line)
    [void](Add-Text $slide 43 517 700 15 "DMS  •  Dental Management System" 8 $script:Palette.Muted)
    [void](Add-Text $slide 857 516 61 16 ("{0:00} / 12" -f $Presentation.Slides.Count) 9 $script:Palette.Muted $false 3)
    return $slide
}

$assets = Join-Path $PSScriptRoot "presentation-assets"
$output = Join-Path $PSScriptRoot "project-presentation.pptx"
$nl = [char]13
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.DisplayAlerts = 1
$ppt.Visible = 1
$presentation = $ppt.Presentations.Add()
$presentation.PageSetup.SlideSize = 16
$presentation.PageSetup.SlideWidth = 960
$presentation.PageSetup.SlideHeight = 540

try {
    $slide = $presentation.Slides.Add(1, 12)
    $slide.Background.Fill.ForeColor.RGB = $Palette.Background
    [void](Add-Shape $slide 0 0 14 540 $Palette.Green)
    Add-Chip $slide 48 43 180 "TỔNG QUAN DỰ ÁN" $Palette.Mint $Palette.Green
    [void](Add-Text $slide 48 101 355 106 "Quản lý nha khoa${nl}liền mạch, rõ ràng" 33 $Palette.Ink $true)
    [void](Add-Text $slide 50 222 340 30 "Dental Management System (DMS)" 17 $Palette.Green $true)
    [void](Add-Text $slide 50 269 330 72 "Kết nối lịch hẹn, khám bệnh, hóa đơn và tư vấn thông tin." 14 $Palette.Muted)
    Add-Chip $slide 48 382 242 "HIỆN TRẠNG + ĐỊNH HƯỚNG AI" $Palette.White $Palette.Green
    Add-Image $slide (Join-Path $assets "02-dashboard.png") 422 104 486 304
    [void](Add-Text $slide 424 420 477 19 "Giao diện thật · dữ liệu demo" 9 $Palette.Muted $false 3)
    [void](Add-Shape $slide 42 511 876 1 $Palette.Line)
    [void](Add-Text $slide 43 517 700 15 "DMS  •  Dental Management System" 8 $Palette.Muted)
    [void](Add-Text $slide 857 516 61 16 "01 / 12" 9 $Palette.Muted $false 3)

    $slide = Add-Slide $presentation "01 / Bối cảnh" "Từ thao tác rời rạc tới quy trình phối hợp" "Dự án số hóa vận hành phòng khám và tạo dữ liệu nhất quán giữa các vai trò."
    Add-Card $slide 46 151 270 112 "Thách thức" "Lịch, thông tin khám và thu phí cần phối hợp giữa lễ tân, bác sĩ và quản trị." $Palette.Coral
    Add-Card $slide 345 151 270 112 "Giải pháp" "Quản lý bệnh nhân, lịch, EMR, dịch vụ, hóa đơn, thanh toán và thống kê." $Palette.Green
    Add-Card $slide 644 151 270 112 "Người dùng" "Quản trị, lễ tân và bác sĩ; quyền thao tác khác nhau theo vai trò." $Palette.Gold
    [void](Add-Text $slide 51 294 405 22 "PHẠM VI CHỨC NĂNG" 10 $Palette.Green $true)
    [void](Add-Text $slide 53 328 390 142 ("• Bệnh nhân và lịch hẹn${nl}• EMR và dịch vụ chỉ định${nl}• Hóa đơn, tiền mặt, QR đối soát${nl}• Chatbot tra giá / khung giờ${nl}• Dashboard doanh thu / lượt khám") 14 $Palette.Ink)
    [void](Add-Shape $slide 490 303 422 145 $Palette.Mint $true)
    [void](Add-Text $slide 513 323 374 24 "Hiện trạng và đề xuất" 15 $Palette.Ink $true)
    [void](Add-Text $slide 513 357 370 77 "Chatbot hiện tra cứu theo quy tắc và dữ liệu hệ thống. Tóm tắt EMR, nhắc tái khám bằng AI chưa được triển khai." 13 $Palette.Muted)

    $slide = Add-Slide $presentation "02 / Quy trình" "Một hành trình dữ liệu, giá trị ở mỗi bước" "Các bước nối từ tiếp nhận tới thống kê, theo đúng quyền được cấp."
    $xs = @(52, 280, 508, 736)
    $roles = @("LỄ TÂN", "BÁC SĨ", "LỄ TÂN", "QUẢN TRỊ")
    $bodies = @("Tra hồ sơ, xem ca làm, đặt lịch hẹn.", "Khám, cập nhật EMR, chọn dịch vụ chỉ định.", "Tạo hóa đơn, nhận tiền hoặc đối soát QR.", "Xem doanh thu và lượt khám theo thời gian.")
    for ($i = 0; $i -lt 4; $i++) {
        [void](Add-Shape $slide $xs[$i] 177 170 174 $Palette.White $true)
        Add-Chip $slide ($xs[$i] + 16) 194 136 $roles[$i] $Palette.Mint $Palette.Green
        [void](Add-Text $slide ($xs[$i] + 16) 237 139 76 $bodies[$i] 12 $Palette.Ink)
        if ($i -lt 3) { [void](Add-Shape $slide ($xs[$i] + 173) 258 54 3 $Palette.Gold) }
    }
    [void](Add-Shape $slide 68 395 824 69 $Palette.Dark $true)
    [void](Add-Text $slide 86 418 788 26 "Bệnh nhân → lịch → EMR → hóa đơn / giao dịch → dashboard" 17 $Palette.White $true 2)

    $slide = Add-Slide $presentation "03 / Kiến trúc" "Web, API, dữ liệu theo module nghiệp vụ" "Tóm lược cấu trúc frontend và backend trong repository."
    [void](Add-Shape $slide 50 159 190 130 $Palette.White $true)
    [void](Add-Text $slide 65 179 160 21 "FRONTEND" 10 $Palette.Green $true 2)
    [void](Add-Text $slide 65 216 160 52 "React UI${nl}Vite · trình duyệt" 16 $Palette.Ink $true 2)
    [void](Add-Shape $slide 285 159 363 130 $Palette.Mint $true)
    [void](Add-Text $slide 300 179 332 21 "DJANGO REST API" 10 $Palette.Green $true 2)
    [void](Add-Text $slide 300 215 332 55 "authentication · clinic${nl}appointments · chatbot/dashboard" 13 $Palette.Ink $true 2)
    [void](Add-Shape $slide 694 159 216 130 $Palette.White $true)
    [void](Add-Text $slide 708 179 187 21 "CƠ SỞ DỮ LIỆU" 10 $Palette.Green $true 2)
    [void](Add-Text $slide 708 216 187 52 "SQLite mặc định${nl}SQL Server tùy chọn" 13 $Palette.Ink $true 2)
    [void](Add-Shape $slide 240 222 45 3 $Palette.Gold)
    [void](Add-Shape $slide 648 222 46 3 $Palette.Gold)
    Add-Card $slide 50 316 262 116 "QR" "VietQR tạo ảnh; không có webhook hay xác minh ngân hàng tự động." $Palette.Gold
    Add-Card $slide 349 316 262 116 "Chatbot hiện hành" "Quy tắc + truy vấn dịch vụ/lịch trong cơ sở dữ liệu." $Palette.Green
    Add-Card $slide 648 316 262 116 "AI tương lai" "Chưa kết nối dịch vụ AI, API tóm tắt EMR hoặc job nhắc tái khám." $Palette.Coral

    $slide = Add-Slide $presentation "04 / Đặt lịch" "Kiểm tra lịch trước khi xác nhận đặt hẹn" "API kiểm tra ca làm, thời lượng dịch vụ và lịch bị trùng."
    Add-Image $slide (Join-Path $assets "03-booking-dialog.png") 43 141 558 349
    [void](Add-Text $slide 47 494 548 14 "Giao diện thật · dữ liệu demo" 8 $Palette.Muted $false 3)
    Add-Card $slide 636 153 274 89 "Nhập thông tin" "Bệnh nhân, bác sĩ, dịch vụ, ngày, giờ và lý do khám." $Palette.Green
    Add-Card $slide 636 261 274 89 "Kiểm tra" "Đúng ca làm, đủ thời lượng, không xung đột lịch." $Palette.Gold
    Add-Card $slide 636 369 274 89 "Kết quả" "Chỉ báo thành công khi API tạo lịch." $Palette.Green

    $slide = Add-Slide $presentation "05 / Khám bệnh" "Hồ sơ bệnh án điện tử (EMR) gắn với lịch hẹn" "Bác sĩ ghi nhận nội dung khám và dịch vụ được chỉ định."
    Add-Image $slide (Join-Path $assets "04-emr.png") 43 141 558 349
    [void](Add-Text $slide 47 494 548 14 "Giao diện EMR thật · hồ sơ demo" 8 $Palette.Muted $false 3)
    Add-Card $slide 636 153 274 89 "Liên kết" "Mỗi EMR gắn một-một với lịch hẹn." $Palette.Green
    Add-Card $slide 636 261 274 89 "Ghi nhận" "Chẩn đoán, hướng điều trị, răng và dịch vụ." $Palette.Gold
    [void](Add-Shape $slide 636 369 274 89 $Palette.Mint $true)
    Add-Chip $slide 650 382 161 "AI SUMMARY · ĐỀ XUẤT" $Palette.White $Palette.Green
    [void](Add-Text $slide 650 415 245 34 "AI tóm tắt EMR chưa được triển khai." 11 $Palette.Muted)

    $slide = Add-Slide $presentation "06 / Thanh toán" "Tính tiền từ dịch vụ, lưu trạng thái giao dịch" "Hóa đơn giữ đơn giá tại thời điểm phát hành; giao dịch có phương thức và trạng thái."
    Add-Image $slide (Join-Path $assets "05-cash-payment-confirmation.png") 43 141 558 349
    [void](Add-Text $slide 47 494 548 14 "Hộp thoại thật · hóa đơn demo" 8 $Palette.Muted $false 3)
    Add-Card $slide 636 153 274 89 "Tiền mặt" "Xác nhận đủ số dư; ghi giao dịch COMPLETED." $Palette.Green
    Add-Card $slide 636 261 274 89 "QR" "Tạo QR chỉ tạo giao dịch PENDING, chưa đồng nghĩa đã nhận tiền." $Palette.Gold
    Add-Card $slide 636 369 274 89 "Đối soát" "Nhân viên khớp tiền + mã tham chiếu, lưu người xác minh." $Palette.Coral

    $slide = Add-Slide $presentation "07 / Chatbot" "Tra cứu theo dữ liệu; không tự bịa câu trả lời" "Ví dụ thật: giá dịch vụ lấy từ danh mục đang hoạt động."
    Add-Image $slide (Join-Path $assets "06-chatbot-price.png") 43 141 558 349
    [void](Add-Text $slide 47 494 548 14 "Chatbot với dữ liệu demo · ảnh thật" 8 $Palette.Muted $false 3)
    [void](Add-Shape $slide 636 153 274 304 $Palette.White $true)
    Add-Chip $slide 652 170 235 "THEO QUY TẮC · KHÔNG GỌI LLM" $Palette.Mint $Palette.Green
    [void](Add-Text $slide 653 211 238 219 ("HỖ TRỢ${nl}• Tra giá dịch vụ hoạt động${nl}• Gợi ý giờ theo lịch hiện có${nl}${nl}GIỚI HẠN${nl}• Không chẩn đoán / xem EMR${nl}• Không đặt hoặc giữ lịch${nl}• Câu hỏi khác → liên hệ lễ tân") 12 $Palette.Ink)

    $slide = Add-Slide $presentation "08 / Định hướng AI" "Hai luồng AI là đề xuất, chưa triển khai" "Chưa có API, dịch vụ AI, lịch chạy nền hay kênh nhắc trong source hiện tại."
    [void](Add-Shape $slide 47 151 419 295 $Palette.White $true)
    Add-Chip $slide 66 168 186 "TÓM TẮT EMR · ĐỀ XUẤT" $Palette.Mint $Palette.Green
    [void](Add-Text $slide 70 211 373 212 ("Bác sĩ chọn hồ sơ${nl}↓${nl}API kiểm tra quyền, giảm thiểu dữ liệu${nl}↓${nl}AI tạo bản nháp${nl}↓${nl}Bác sĩ rà soát / chỉnh sửa${nl}↓${nl}Chỉ lưu khi được duyệt") 12 $Palette.Ink)
    [void](Add-Shape $slide 493 151 419 295 $Palette.White $true)
    Add-Chip $slide 511 168 210 "NHẮC TÁI KHÁM · ĐỀ XUẤT" $Palette.Mint $Palette.Green
    [void](Add-Text $slide 516 211 373 212 ("Xác nhận ngày + đồng thuận${nl}↓${nl}AI soạn nháp không chẩn đoán${nl}↓${nl}Nhân viên / bác sĩ duyệt${nl}↓${nl}Lưu lịch gửi + audit${nl}↓${nl}Job nền gửi, lưu kết quả") 12 $Palette.Ink)
    Add-Chip $slide 327 462 306 "CHƯA CÓ API · DỊCH VỤ AI · LỊCH NỀN" $Palette.White $Palette.Coral

    $slide = Add-Slide $presentation "09 / An toàn" "AI hỗ trợ hành chính, không thay bác sĩ" "Phân biệt biện pháp hiện có với điều kiện cần có trước khi triển khai AI tương lai."
    [void](Add-Shape $slide 48 151 416 304 $Palette.Mint $true)
    [void](Add-Text $slide 69 172 370 25 "ĐANG CÓ" 14 $Palette.Green $true)
    [void](Add-Text $slide 69 212 370 222 ("• API nghiệp vụ phân quyền theo vai trò${nl}• Chatbot không cần dữ liệu bệnh nhân${nl}• Trả lời dựa trên danh mục / lịch${nl}• Thiếu dữ liệu: báo rõ, hướng lễ tân${nl}• QR chỉ cập nhật sau đối soát") 13 $Palette.Ink)
    [void](Add-Shape $slide 496 151 416 304 $Palette.White $true)
    [void](Add-Text $slide 518 172 370 25 "TRƯỚC KHI BẬT AI" 14 $Palette.Coral $true)
    [void](Add-Text $slide 518 212 370 222 ("• Duyệt quyền và sự đồng thuận${nl}• Giảm thiểu dữ liệu gửi đi${nl}• Bác sĩ / nhân viên duyệt bản nháp${nl}• Lưu nguồn, phiên bản, nhật ký kiểm toán${nl}• Lỗi: báo rõ, chuyển người phụ trách") 13 $Palette.Ink)
    [void](Add-Text $slide 52 471 853 18 "Hiện tại chưa gửi hồ sơ bệnh án tới nhà cung cấp AI." 10 $Palette.Green $true 2)

    $slide = Add-Slide $presentation "10 / Demo" "Một tình huống xuyên suốt hệ thống" "Kịch bản gợi ý 3 phút; dùng dữ liệu demo, không cần giao dịch ngân hàng thật."
    $steps = @(
        @("01", "ĐẶT HẸN", "Chọn bệnh nhân, dịch vụ, bác sĩ và giờ hợp lệ."),
        @("02", "GHI EMR", "Bác sĩ lưu ghi nhận khám và dịch vụ chỉ định."),
        @("03", "THANH TOÁN", "Mở hóa đơn; minh họa hộp thoại tiền mặt."),
        @("04", "CHATBOT", "Tra giá và nêu rõ giới hạn tư vấn.")
    )
    for ($i = 0; $i -lt 4; $i++) {
        $x = 47 + 228 * $i
        [void](Add-Shape $slide $x 173 199 167 $Palette.White $true)
        [void](Add-Text $slide ($x + 17) 191 55 31 $steps[$i][0] 21 $Palette.Gold $true)
        [void](Add-Text $slide ($x + 17) 232 166 22 $steps[$i][1] 11 $Palette.Green $true)
        [void](Add-Text $slide ($x + 17) 267 166 60 $steps[$i][2] 11 $Palette.Muted)
    }
    [void](Add-Text $slide 55 376 849 68 "Không trình diễn AI tóm tắt EMR hoặc gửi nhắc tái khám như chức năng đã có. Trình bày đó là đề xuất ở trang 9." 14 $Palette.Ink $true 2)

    $slide = Add-Slide $presentation "11 / Chạy thử" "Kịch bản trình bày 10 phút — nhóm chốt người nói" "Phân vai gợi ý; thay bằng tên thành viên sau khi thống nhất."
    Add-Card $slide 49 158 267 174 "THÀNH VIÊN A · 3 PHÚT" "Bài toán, mục tiêu, phạm vi, kiến trúc (trang 1–4). Người trình bày: ________" $Palette.Green
    Add-Card $slide 346 158 267 174 "THÀNH VIÊN B · 3 PHÚT" "Đặt lịch, khám, EMR; dẫn demo (trang 5–6, 11). Người trình bày: ________" $Palette.Gold
    Add-Card $slide 643 158 267 174 "THÀNH VIÊN C · 4 PHÚT" "Thanh toán, chatbot, an toàn AI (trang 7–10, 12). Người trình bày: ________" $Palette.Coral
    [void](Add-Shape $slide 51 362 858 94 $Palette.Dark $true)
    [void](Add-Text $slide 74 384 812 48 "Tập dượt: 1 phút chuyển cảnh + 3 phút demo + 6 phút nội dung. Rà chính tả, thuật ngữ, hình ảnh, cỡ chữ và thời lượng." 13 $Palette.White $false 2)

    $presentation.SaveAs($output, 24)
    Write-Output "Created $output with $($presentation.Slides.Count) slides."
}
finally {
    if ($presentation) { $presentation.Close() }
    if ($ppt) { $ppt.Quit() }
}
