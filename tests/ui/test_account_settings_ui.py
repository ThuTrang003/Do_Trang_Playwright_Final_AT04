"""
Nhóm UI - Chức năng "Setting account"
- Theme (Light/Dark/System) + Select color + Save/Reset.
- Data-driven: dữ liệu lấy từ test_data/settings_data.json
"""
import pytest
import allure

from utils.data_reader import load_json

DATA = load_json("settings_data.json")


@allure.feature("Setting account")
@pytest.mark.ui
@pytest.mark.settings
class TestAccountSettingsUI:

    # ---------------- Chuyển đổi Theme ----------------
    @allure.story("Chuyển đổi Theme")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "case", DATA["theme_cases"], ids=[c["case_id"] for c in DATA["theme_cases"]]
    )
    def test_switch_theme(self, home_page, case):
        allure.dynamic.title(case["title"])

        with allure.step("Mở menu avatar -> chọn 'Settings'"):
            settings_page = home_page.go_to_settings()

        with allure.step(f"Chọn tab Theme = {case['theme']}"):
            settings_page.select_theme(case["theme"])

        with allure.step("Xác minh tab đã được chọn và lưu"):
            settings_page.attach_screenshot(f"theme_{case['case_id']}")
            assert settings_page.get_selected_theme() == case["theme"].lower(), (
                f"[{case['case_id']}] Theme đang chọn không phải '{case['theme']}'"
            )
            settings_page.save()

    # ---------------- Chọn màu & Save ----------------
    @allure.story("Chọn màu tài khoản (Select color)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "case", DATA["color_cases"], ids=[c["case_id"] for c in DATA["color_cases"]]
    )
    def test_select_color_and_save(self, home_page, case):
        allure.dynamic.title(case["title"])

        with allure.step("Mở menu avatar -> chọn 'Settings'"):
            settings_page = home_page.go_to_settings()

        with allure.step(f"Chọn màu tại vị trí index={case['color_index']}"):
            assert settings_page.color_count() > case["color_index"], "Không đủ số lượng màu để chọn"
            settings_page.select_color(case["color_index"])

        with allure.step("Nhấn Save"):
            settings_page.save()

        with allure.step("Xác minh lưu thành công"):
            settings_page.attach_screenshot(f"color_{case['case_id']}")
            message = settings_page.wait_for_toast()
            assert case["expect_message_contains"].lower() in message.lower()

    # ---------------- Reset không lưu thay đổi ----------------
    @allure.story("Reset thay đổi chưa lưu")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "case", DATA["reset_cases"], ids=[c["case_id"] for c in DATA["reset_cases"]]
    )
    def test_reset_discards_unsaved_change(self, home_page, case):
        allure.dynamic.title(case["title"])

        with allure.step("Mở menu avatar -> chọn 'Settings', ghi nhận theme ban đầu"):
            settings_page = home_page.go_to_settings()
            original_theme = settings_page.get_selected_theme()

        with allure.step(f"Đổi theme sang '{case['theme']}' nhưng KHÔNG Save"):
            settings_page.select_theme(case["theme"])
            assert settings_page.get_selected_theme() == case["theme"].lower()

        with allure.step("Bấm Reset"):
            settings_page.reset()

        with allure.step("Xác minh theme quay lại trạng thái ban đầu"):
            settings_page.attach_screenshot(f"after_reset_{case['case_id']}")
            assert settings_page.get_selected_theme() == original_theme, (
                "Kỳ vọng Reset đưa theme về trạng thái trước khi thay đổi"
            )

    # ---------------- Save không có thay đổi vẫn hoạt động bình thường ----------------
    @allure.story("Save khi không có thay đổi")
    @allure.severity(allure.severity_level.MINOR)
    def test_save_without_change_does_not_error(self, home_page):
        with allure.step("Mở menu avatar -> chọn 'Settings' và bấm Save ngay (không đổi gì)"):
            settings_page = home_page.go_to_settings()
            settings_page.save()

        with allure.step("Xác minh không có lỗi phát sinh (trang vẫn hoạt động bình thường)"):
            settings_page.attach_screenshot("save_no_change")
            assert settings_page.save_button.is_visible()
