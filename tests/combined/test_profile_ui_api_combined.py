"""
Nhóm kết hợp UI + API cho "Change my profile" & "Setting account".
Dùng endpoint THẬT:
    GET   /api/me
    PATCH /api/profile  (dùng chung cho info / đổi mật khẩu / theme-color)
Điều hướng UI PHẢI qua HomePage.go_to_profile()/go_to_settings() (session lưu memory,
không dùng page.goto trực tiếp).
"""
import pytest
import allure

from api.endpoints import Endpoints
from config.config import config


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


@allure.feature("Combined UI + API")
@pytest.mark.combined
class TestProfileUIApiCombined:

    @allure.story("Cập nhật profile qua API -> verify hiển thị trên UI")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_profile_via_api_reflected_on_ui(self, api_client, auth_token, home_page):
        new_name = "Combined API Update User"

        with allure.step("Gọi PATCH /api/profile để đổi Name"):
            response = api_client.patch(
                Endpoints.UPDATE_PROFILE,
                data={
                    "name": new_name,
                    "email": config.LOGIN_EMAIL,
                    "password_old": "",
                    "password": "",
                    "avatarUrl": "",
                    "phone": "0911222333",
                    "address": "Thành phố Hà Nội",
                },
                headers=_auth_headers(auth_token),
            )
            assert response.status == 200, f"Update profile qua API thất bại: {response.text()[:300]}"

        with allure.step("Mở menu avatar -> 'Profile' và kiểm tra Name đã đổi trên UI"):
            profile_page = home_page.go_to_profile()
            profile_page.attach_screenshot("profile_after_api_update")
            assert profile_page.get_name_value() == new_name

    @allure.story("Cập nhật profile qua UI -> verify qua API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_profile_via_ui_reflected_on_api(self, home_page, api_client, auth_token):
        new_name = "Combined UI Update User"

        with allure.step("Mở menu avatar -> 'Profile' và cập nhật Name qua UI"):
            profile_page = home_page.go_to_profile()
            profile_page.update_name(new_name)
            profile_page.update_phone("0933444555")
            profile_page.save()
            profile_page.wait_for_toast()

        with allure.step("Gọi GET /api/me để verify dữ liệu đồng bộ backend"):
            response = api_client.get(Endpoints.GET_PROFILE, headers=_auth_headers(auth_token))
            assert response.status == 200
            body = response.json()
            assert body.get("name") == new_name

    @allure.story("Đổi mật khẩu qua UI -> đăng nhập lại bằng API với mật khẩu mới")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_change_password_ui_then_login_api(self, home_page, api_client):
        old_password = config.LOGIN_PASSWORD
        new_password = "CombinedNew1234@"

        with allure.step("Mở menu avatar -> 'Profile' và đổi mật khẩu qua UI"):
            profile_page = home_page.go_to_profile()
            profile_page.change_password(old_password, new_password, new_password)
            profile_page.save()
            profile_page.wait_for_toast()

        with allure.step("Gọi API Login bằng mật khẩu mới -> kỳ vọng 200"):
            response = api_client.post(
                Endpoints.LOGIN, data={"email": config.LOGIN_EMAIL, "password": new_password}
            )
            assert response.status == 200, "Login API bằng mật khẩu mới phải thành công"

        with allure.step("Rollback: đổi lại mật khẩu cũ qua UI để không ảnh hưởng các test khác"):
            # Vẫn đang ở trang Profile (chưa điều hướng đi đâu) nên có thể thao tác tiếp
            profile_page.change_password(new_password, old_password, old_password)
            profile_page.save()
            profile_page.wait_for_toast()

    @allure.story("Gọi API cập nhật profile với token không hợp lệ trong khi UI vẫn đang đăng nhập")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_profile_api_invalid_token_does_not_affect_ui_session(
        self, api_client, home_page
    ):
        with allure.step("Gọi PATCH /api/profile với token rác -> kỳ vọng 401"):
            response = api_client.patch(
                Endpoints.UPDATE_PROFILE,
                data={"name": "Should Not Update", "email": config.LOGIN_EMAIL},
                headers={"Authorization": "Bearer invalid.token.value"},
            )
            assert response.status == 401

        with allure.step("Verify UI vẫn đang đăng nhập bình thường, dữ liệu không đổi"):
            profile_page = home_page.go_to_profile()
            profile_page.attach_screenshot("ui_session_unaffected")
            assert profile_page.get_name_value() != "Should Not Update"

    @allure.story("Chuyển Theme qua UI -> verify qua API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_switch_theme_ui_reflected_on_api(self, home_page, api_client, auth_token):
        with allure.step("Mở menu avatar -> 'Settings', chuyển Theme sang Dark, Save"):
            settings_page = home_page.go_to_settings()
            settings_page.select_theme("dark")
            settings_page.save()
            settings_page.wait_for_toast()

        with allure.step("Gọi GET /api/me verify config.theme đã lưu là 'dark'"):
            response = api_client.get(Endpoints.GET_PROFILE, headers=_auth_headers(auth_token))
            assert response.status == 200
            body = response.json()
            assert body.get("config", {}).get("theme") == "dark"

    @allure.story("Upload avatar qua UI -> verify field avatar qua API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_upload_avatar_ui_reflected_on_api(self, home_page, api_client, auth_token, tmp_path):
        with allure.step("Upload avatar qua UI"):
            profile_page = home_page.go_to_profile()
            avatar_file = tmp_path / "avatar_combined.png"
            png_1x1 = bytes.fromhex(
                "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753"
                "de0000000c4944415478da6360000002000100e921bc330000000049454e44ae426082"
            )
            avatar_file.write_bytes(png_1x1)
            profile_page.upload_avatar(str(avatar_file))
            profile_page.save()
            profile_page.wait_for_toast()

        with allure.step("Gọi GET /api/me để verify avatarUrl đã cập nhật (khác rỗng)"):
            response = api_client.get(Endpoints.GET_PROFILE, headers=_auth_headers(auth_token))
            assert response.status == 200
            body = response.json()
            assert body.get("avatarUrl"), "Kỳ vọng có avatarUrl sau khi upload"
