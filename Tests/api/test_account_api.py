"""
Nhóm API - Login + Đổi mật khẩu + Setting account
Endpoint THẬT: đổi mật khẩu và cập nhật settings (theme/color) đều dùng CHUNG
PATCH /api/profile như test_profile_api.py, chỉ khác payload gửi lên:
    - Đổi mật khẩu:  {..., "password_old": "...", "password": "..."}
    - Setting account: {"config": {"theme": "...", "mainColor": "#hex"}}

Mỗi endpoint/nghiệp vụ đảm bảo tối thiểu 1 case 200 + 1 case lỗi (400/401...)
Data-driven: dữ liệu lấy từ test_data/api_account_data.json + credential từ .env
"""
import pytest
import allure

from api.endpoints import Endpoints
from config.config import config
from utils.data_reader import load_json

DATA = load_json("api_account_data.json")


def _headers(token, use_valid_token: bool) -> dict:
    if use_valid_token and token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@allure.feature("API - Account Settings")
@pytest.mark.api
class TestAccountAPI:

    # ---------------- Login ----------------
    @allure.story("POST /api/login")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.profile
    @pytest.mark.parametrize(
        "case", DATA["login_cases"], ids=[c["case_id"] for c in DATA["login_cases"]]
    )
    def test_login(self, api_client, case):
        allure.dynamic.title(case["title"])

        with allure.step("Chuẩn bị payload login (lấy từ .env, không hard code)"):
            password = config.LOGIN_PASSWORD if case["password_env"] else case["wrong_password"]
            payload = {"email": config.LOGIN_EMAIL, "password": password}

        with allure.step("Gọi API Login"):
            response = api_client.post(Endpoints.LOGIN, data=payload)

        with allure.step(f"Xác minh status code = {case['expected_status']}"):
            assert response.status == case["expected_status"], (
                f"[{case['case_id']}] Kỳ vọng {case['expected_status']}, thực tế {response.status}. "
                f"Body: {response.text()[:500]}"
            )

        if case["expected_status"] == 200:
            with allure.step("Xác minh response trả về token"):
                body = response.json()
                token = body.get("token") or body.get("accessToken") or body.get("data", {}).get("token")
                assert token, "Response login 200 phải trả về access token"

    # ---------------- Đổi mật khẩu (qua PATCH /api/profile) ----------------
    @allure.story("PATCH /api/profile (đổi mật khẩu)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.profile
    @pytest.mark.parametrize(
        "case",
        DATA["change_password_cases"],
        ids=[c["case_id"] for c in DATA["change_password_cases"]],
    )
    def test_change_password(self, api_client, auth_token, case):
        allure.dynamic.title(case["title"])

        with allure.step("Gọi PATCH /api/profile với password_old/password data-driven"):
            headers = _headers(auth_token, case["use_valid_token"])
            response = api_client.patch(Endpoints.UPDATE_PROFILE, data=case["payload"], headers=headers)

        with allure.step(f"Xác minh status code = {case['expected_status']}"):
            assert response.status == case["expected_status"], (
                f"[{case['case_id']}] Kỳ vọng {case['expected_status']}, thực tế {response.status}. "
                f"Body: {response.text()[:500]}"
            )

        if case["expected_status"] == 200:
            with allure.step("Xác minh response trả msg thành công"):
                body = response.json()
                assert "success" in body.get("msg", "").lower()

    # ---------------- Update Settings (qua PATCH /api/profile) ----------------
    @allure.story("PATCH /api/profile (Setting account: theme/color)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.settings
    @pytest.mark.parametrize(
        "case",
        DATA["update_settings_cases"],
        ids=[c["case_id"] for c in DATA["update_settings_cases"]],
    )
    def test_update_settings(self, api_client, auth_token, case):
        allure.dynamic.title(case["title"])

        with allure.step("Gọi PATCH /api/profile với payload config.theme/config.mainColor"):
            headers = _headers(auth_token, case["use_valid_token"])
            response = api_client.patch(Endpoints.UPDATE_PROFILE, data=case["payload"], headers=headers)

        with allure.step(f"Xác minh status code = {case['expected_status']}"):
            assert response.status == case["expected_status"], (
                f"[{case['case_id']}] Kỳ vọng {case['expected_status']}, thực tế {response.status}. "
                f"Body: {response.text()[:500]}"
            )

        if case["expected_status"] == 200:
            with allure.step("Xác minh response trả msg thành công + verify qua GET /api/me"):
                body = response.json()
                assert "success" in body.get("msg", "").lower()

                verify_response = api_client.get(Endpoints.GET_PROFILE, headers=headers)
                assert verify_response.status == 200
                verify_body = verify_response.json()
                assert verify_body.get("config", {}).get("theme") == case["payload"]["config"]["theme"]
                assert verify_body.get("config", {}).get("mainColor") == case["payload"]["config"]["mainColor"]
