"""
Nhóm API - Chức năng Profile
Endpoint THẬT đã xác nhận qua Network tab:
    GET   /api/me       -> trả full object profile
    PATCH /api/profile  -> chỉ trả {"msg": "..."}, KHÔNG echo lại data đã lưu
                            => muốn verify dữ liệu đã lưu đúng, phải gọi lại GET /api/me

Mỗi endpoint đảm bảo tối thiểu 1 case 200 + 1 case lỗi (400/401...)
Data-driven: dữ liệu lấy từ test_data/api_profile_data.json
"""
import pytest
import allure

from api.endpoints import Endpoints
from utils.data_reader import load_json

DATA = load_json("api_profile_data.json")

def _headers(token, use_valid_token: bool) -> dict:
    if use_valid_token and token:
        return {"Authorization": f"Bearer {token}"}
    return {}

@allure.feature("API - Profile")
@pytest.mark.api
@pytest.mark.profile
class TestProfileAPI:

    @allure.story("GET /api/me")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case", DATA["get_profile_cases"], ids=[c["case_id"] for c in DATA["get_profile_cases"]]
    )
    def test_get_profile(self, api_client, auth_token, case):
        allure.dynamic.title(case["title"])

        with allure.step("Gọi GET /api/me"):
            headers = _headers(auth_token, case["use_valid_token"])
            response = api_client.get(Endpoints.GET_PROFILE, headers=headers)

        with allure.step(f"Xác minh status code = {case['expected_status']}"):
            assert response.status == case["expected_status"], (
                f"[{case['case_id']}] Kỳ vọng {case['expected_status']}, thực tế {response.status}. "
                f"Body: {response.text()[:500]}"
            )

        if case["expected_status"] == 200:
            with allure.step("Xác minh response trả đủ field cơ bản (id/name/email/config)"):
                body = response.json()
                for field in ("id", "name", "email", "config"):
                    assert field in body, f"Response GET /api/me thiếu field '{field}'"

    @allure.story("PATCH /api/profile (cập nhật thông tin cá nhân)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case", DATA["update_profile_cases"], ids=[c["case_id"] for c in DATA["update_profile_cases"]]
    )
    def test_update_profile(self, api_client, auth_token, case):
        allure.dynamic.title(case["title"])

        with allure.step("Gọi PATCH /api/profile với payload data-driven"):
            headers = _headers(auth_token, case["use_valid_token"])
            response = api_client.patch(
                Endpoints.UPDATE_PROFILE,
                data=case["payload"],
                headers=headers
            )

        with allure.step(f"Xác minh status code = {case['expected_status']}"):
            assert response.status == case["expected_status"], (
                f"[{case['case_id']}] Kỳ vọng {case['expected_status']}, thực tế {response.status}. "
                f"Body: {response.text()[:500]}"
            )

        if case["expected_status"] == 200:
            with allure.step("Xác minh response trả msg thành công"):
                body = response.json()
                assert "success" in body.get("msg", "").lower()

            with allure.step("Gọi lại GET /api/me để verify dữ liệu đã lưu đúng"):
                verify_response = api_client.get(Endpoints.GET_PROFILE, headers=headers)
                assert verify_response.status == 200
                verify_body = verify_response.json()
                assert verify_body.get("name") == case["payload"]["name"]
                assert verify_body.get("phone") == case["payload"]["phone"]
                assert verify_body.get("address") == case["payload"]["address"]
