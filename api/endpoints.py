"""
Khai báo tập trung các endpoint API cho chức năng Profile / Setting account.

Đã XÁC NHẬN THẬT qua Network tab (DevTools):
- GET  /api/me       -> lấy thông tin profile hiện tại
- PATCH /api/profile -> dùng CHUNG cho cả 3 nghiệp vụ:
    1) Cập nhật thông tin cá nhân (name, phone, address, email, avatarUrl)
    2) Đổi mật khẩu (password_old, password) - gửi kèm trong CÙNG object trên
    3) Cập nhật Setting account (config.theme, config.mainColor)

Response mẫu của PATCH /api/profile (không echo lại data đã lưu):
    {"msg": "Updated profile successfully."}
=> Muốn xác minh dữ liệu đã lưu đúng chưa, phải gọi lại GET /api/me sau đó.

Response mẫu của GET /api/me:
    {
        "id": "...",
        "name": "Trang",
        "email": "auto82@gmail.com",
        "avatarUrl": "",
        "phone": "123456789",
        "address": "Thành phố Hà Nội",
        "config": {"theme": "dark", "mainColor": "#4caf50"}
    }

CÒN THIẾU / CẦN BẠN XÁC NHẬN THÊM:
- Path chính xác của API Login (hiện đang đoán "/api/login" theo pattern /api/me, /api/profile
  vì chưa bắt được request lúc đăng nhập). Mở Network tab lúc bấm nút đăng nhập để lấy chính xác.
- Cơ chế xác thực: Bearer token trong header "Authorization", hay cookie phiên?
  -> Mở tab "Headers" của request GET /api/me hoặc PATCH /api/profile, xem phần
     "Request Headers" có dòng "Authorization: Bearer ..." hay không. Nếu KHÔNG có,
     rất có thể hệ thống dùng cookie/session -> cần sửa lại cách gắn auth trong
     conftest.py (hàm auth_token / _headers) từ Bearer header sang cookie.
- Endpoint upload avatar thật (trả về URL để gán vào field "avatarUrl").
"""


class Endpoints:
    # ---- Auth ----
    LOGIN = "/api/login"  

    # ---- Profile / Setting account (dùng chung 2 endpoint bên dưới) ----
    GET_PROFILE = "/api/me"          # GET - đã xác nhận thật
    UPDATE_PROFILE = "/api/profile"   # PATCH - đã xác nhận thật (info + password + settings)

    # ---- Upload avatar ----
    UPLOAD_AVATAR = "/api/upload"     # TODO: xác nhận lại endpoint upload file thật
