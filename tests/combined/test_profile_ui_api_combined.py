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
from utils.data_reader import load_json

DATA = load_json("combined_data.json")
AVATARS_DIR = config.ROOT_DIR / "test_data" / "avatars"

def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}

@allure.feature("Combined UI + API")
@pytest.mark.combined
class TestProfileUIApiCombined:

    @allure.story("Cập nhật profile qua API -> verify hiển thị trên UI")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case", DATA["update_profile_api_cases"], ids=[c["case_id"] for c in DATA["update_profile_api_cases"]]
    )
    def test_update_profile_via_api_reflected_on_ui(self, api_client, auth_token, loggedin_home_storage, case):
        allure.dynamic.title(case["title"])
        new_name = case["payload"]["name"]

        with allure.step("Gọi PATCH /api/profile để đổi Name"):
            response = api_client.patch(
                Endpoints.UPDATE_PROFILE,
                data=case["payload"],
                headers=_auth_headers(auth_token),
            )
        with allure.step(f"Xác minh status code = {case['expected_status']}"):
            assert response.status == case["expected_status"], (
                f"[{case['case_id']}] Kỳ vọng {case['expected_status']}, thực tế {response.status}. "
                f"Body: {response.text()[:500]}"
            )

        with allure.step("Mở menu avatar -> 'Profile' và kiểm tra Name đã đổi trên UI"):
            profile_page = loggedin_home_storage.go_to_profile()
            profile_page.attach_screenshot("profile_after_api_update")
            assert profile_page.get_name_value() == new_name

    @allure.story("Cập nhật profile qua UI -> verify qua API")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
            "case",
            DATA["update_profile_ui_cases"],
            ids=[c["case_id"] for c in DATA["update_profile_ui_cases"]],
        )
    def test_update_profile_via_ui_reflected_on_api(self, loggedin_home_storage, api_client, auth_token, case):
        allure.dynamic.title(case["title"])
        new_name = case["payload"]["name"]
        new_phone = case["payload"]["phone"]

        with allure.step("Mở menu avatar -> 'Profile' và cập nhật Name qua UI"):
            profile_page = loggedin_home_storage.go_to_profile()
            profile_page.update_name(new_name)
            profile_page.update_phone(new_phone)
            profile_page.save()
            profile_page.wait_for_toast()

        with allure.step("Gọi GET /api/me để verify dữ liệu đồng bộ backend"):
            response = api_client.get(Endpoints.GET_PROFILE, headers=_auth_headers(auth_token))
            assert response.status == case["expected_status"], (
                f"[{case['case_id']}] Kỳ vọng {case['expected_status']}, thực tế {response.status}. "
                f"Body: {response.text()[:500]}"
            )
            body = response.json()
            assert body.get("name") == new_name, (
                f"[{case['case_id']}] Kỳ vọng {new_name}, thực tế {body.get("name")}."
            )
            assert body.get("phone") == new_phone, (
                f"[{case['case_id']}] Kỳ vọng {new_phone}, thực tế {body.get("phone")}."
            )

    @allure.story("Đổi mật khẩu qua UI -> đăng nhập lại bằng API với mật khẩu mới")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.parametrize(
            "case",
            DATA["change_password_cases"],
            ids=[c["case_id"] for c in DATA["change_password_cases"]],
        )
    def test_change_password_ui_then_login_api(self, loggedin_home_storage, api_client, auth_token, case):
        allure.dynamic.title(case["title"])
        old_password = config.LOGIN_PASSWORD
        new_password = case['new_password']

        with allure.step("Mở menu avatar -> 'Profile' và đổi mật khẩu qua UI"):
            profile_page = loggedin_home_storage.go_to_profile()
            profile_page.change_password(old_password, new_password, new_password)
            # Chờ API update password hoàn thành
            with profile_page.page.expect_response(
                lambda response:
                    "/api/profile" in response.url
                    and response.request.method == "PATCH"
            ) as response_info:
                profile_page.save()
            update_response = response_info.value
            assert update_response.status == case['expected_update_status'], (
                f"Update password thất bại: "
                f"status={update_response.status}"
            )
            profile_page.wait_for_toast()
        with allure.step("Gọi API Login bằng mật khẩu mới -> kỳ vọng 200"):
            response = api_client.post(
                Endpoints.LOGIN, data={
                    "email": config.LOGIN_EMAIL,
                    "password": new_password
                }
            )
            assert response.status == case['expected_login_status'], "Login API bằng mật khẩu mới không thành công"

        with allure.step("Rollback: đổi lại mật khẩu cũ từ API để không ảnh hưởng các test khác"):
            response = api_client.patch(
                Endpoints.UPDATE_PROFILE,
                data={
                    "email": config.LOGIN_EMAIL,
                    "password_old": new_password,
                    "password": old_password
                },
                headers=_auth_headers(auth_token),
            )
            assert response.status == case['expected_update_status'], "Đổi lại mật khẩu cũ từ API không thành công"

    @allure.story("Gọi API cập nhật profile với token không hợp lệ trong khi UI vẫn đang đăng nhập")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "case",
        DATA["invalid_token_cases"],
        ids=[c["case_id"] for c in DATA["invalid_token_cases"]],
    )
    def test_update_profile_api_invalid_token_does_not_affect_ui_session(
        self, api_client, loggedin_home_storage, case
    ):
        allure.dynamic.title(case["title"])
        with allure.step("Gọi PATCH /api/profile với token rác -> kỳ vọng 401"):
            response = api_client.patch(
                Endpoints.UPDATE_PROFILE,
                data=case["payload"],
                headers={"Authorization": case['token']},
            )
            assert response.status == case['expected_status'], "Lỗi: Cập nhật Profile thành công với Token không hợp lệ"

        with allure.step("Verify UI vẫn đang đăng nhập bình thường, dữ liệu không đổi"):
            profile_page = loggedin_home_storage.go_to_profile()
            profile_page.attach_screenshot("ui_session_unaffected")
            assert profile_page.get_name_value() != case["payload"]['name']

    @allure.story("Chuyển Theme qua UI -> verify qua API")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
            "case",
            DATA["switch_theme_cases"],
            ids=[c["case_id"] for c in DATA["switch_theme_cases"]],
        )
    def test_switch_theme_ui_reflected_on_api(self, loggedin_home_storage, api_client, auth_token, case):
        allure.dynamic.title(case["title"])
        with allure.step("Mở menu avatar -> 'Settings', chuyển Theme sang Dark, Save"):
            settings_page = loggedin_home_storage.go_to_settings()
            settings_page.select_theme(case['theme'])
            settings_page.save()
        with allure.step("Xác minh thông báo kết quả"):
            settings_page.attach_screenshot(f"after_upload_{case['case_id']}")
            settings_page.assert_toast_message(case)   

        with allure.step("Gọi GET /api/me verify config.theme đã lưu"):
            response = api_client.get(Endpoints.GET_PROFILE, headers=_auth_headers(auth_token))
            assert response.status == case['expected_status'], (
                f"[{case['case_id']}] Kỳ vọng {case['expected_status']}, thực tế {response.status}. "
            )
            body = response.json()
            assert body.get("config", {}).get("theme") == case['theme']

    @allure.story("Upload avatar qua UI -> verify field avatar qua API")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "case", 
        DATA["upload_avatar_cases"], 
        ids=[c["case_id"] for c in DATA["upload_avatar_cases"]]
    )
    def test_upload_avatar_ui_reflected_on_api(
        self, loggedin_home_storage, api_client, auth_token, case
    ):
        allure.dynamic.title(case["title"])
        with allure.step("Upload avatar qua UI"):
            profile_page = loggedin_home_storage.go_to_profile()
            file_path =  AVATARS_DIR / case["file_name"]
            assert file_path.exists(), (
                f"Không tìm thấy file resource: {file_path}. "
                f"Kiểm tra lại thư mục test_data/avatars/ file avatar đã tồn tại."
            )
            profile_page.upload_avatar(str(file_path))
            profile_page.save()
        with allure.step("Xác minh thông báo kết quả"):
            profile_page.attach_screenshot(f"after_upload_{case['case_id']}")
            profile_page.assert_toast_message(case)   

        with allure.step("Gọi GET /api/me để verify avatarUrl đã cập nhật (khác rỗng)"):
            response = api_client.get(Endpoints.GET_PROFILE, headers=_auth_headers(auth_token))
            assert response.status == case["expected_status"], (
                f"[{case['case_id']}] Kỳ vọng {case['expected_status']}, thực tế {response.status}. "
                f"Body: {response.text()[:500]}"
            )
            body = response.json()
            assert body.get("avatarUrl"), "Kỳ vọng có avatarUrl sau khi upload"
