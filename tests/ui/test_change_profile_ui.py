"""
Nhóm UI - Chức năng "Change my profile"
- Update: Name/Phone/Division/Ward/Address/Avatar + Change Password.
- Data-driven: dữ liệu lấy từ test_data/profile_data.json
"""
import pytest
import allure

from config.config import config
from pages.home_page import HomePage
from pages.login_page import LoginPage
from utils.data_reader import load_json

DATA = load_json("profile_data.json")
AVATARS_DIR = config.ROOT_DIR / "test_data" / "avatars"

@allure.feature("Change my profile")
@pytest.mark.ui
@pytest.mark.profile
class TestChangeProfileUI:

    # ---------------- Thông tin cá nhân (Name / Phone) ----------------
    @allure.story("Cập nhật thông tin cá nhân (Name/Phone)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case", DATA["info_cases"], ids=[c["case_id"] for c in DATA["info_cases"]]
    )
    def test_update_name_phone(self, home_page, case):
        allure.dynamic.title(case["title"])

        with allure.step("Mở menu avatar -> chọn 'Profile'"):
            profile_page = home_page.go_to_profile()

        with allure.step(f"Nhập Name='{case['name']}', Phone='{case['phone']}'"):
            profile_page.update_name(case["name"])
            profile_page.update_phone(case["phone"])

        with allure.step("Nhấn Save Profile"):
            profile_page.save()

        with allure.step("Xác minh kết quả"):
            profile_page.attach_screenshot(f"after_save_{case['case_id']}")
            if case["expect_success"]:
                profile_page.assert_toast_message(case)
                assert profile_page.get_name_value() == case["name"]
            else:
                profile_page.assert_error_message(case, profile_page.name_input, profile_page.phone_input)

    # ---------------- Địa chỉ (Division / Ward) ----------------
    @allure.story("Cập nhật địa chỉ (Division/Ward)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "case", DATA["address_cases"], ids=[c["case_id"] for c in DATA["address_cases"]]
    )
    def test_update_address(self, home_page, case):
        allure.dynamic.title(case["title"])

        with allure.step("Mở menu avatar -> chọn 'Profile'"):
            profile_page = home_page.go_to_profile()

        with allure.step(f"Chọn Division='{case['division']}', Ward='{case['ward']}'"):
            profile_page.update_division(case["division"])
            profile_page.update_ward(case["ward"])

        with allure.step("Nhấn Save Profile"):
            profile_page.save()

        with allure.step("Xác minh lưu thành công"):
            profile_page.attach_screenshot(f"after_save_{case['case_id']}")
            message = profile_page.wait_for_toast()
            assert case["expect_message_contains"].lower() in message.lower()

    # ---------------- Đổi mật khẩu ----------------
    @allure.story("Đổi mật khẩu")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case", DATA["password_cases"], ids=[c["case_id"] for c in DATA["password_cases"]]
    )
    def test_change_password(self, home_page, case):
        """
        Email/Password dùng để đăng nhập LẤY TỪ config (.env):
        - Case cần "mật khẩu hiện tại đúng" (use_config_old_password=true) -> dùng config.LOGIN_PASSWORD.
        - Case cố tình test "sai mật khẩu hiện tại" (use_config_old_password=false) -> dùng
          giá trị sai cố định trong JSON (case["old_password"]), vì đây là input KHÔNG hợp lệ,
          không phải credential thật nên không cần lấy từ config.

        Nếu case đổi mật khẩu THÀNH CÔNG (case["rollback"]=true), test sẽ tự động đổi lại
        mật khẩu về đúng config.LOGIN_PASSWORD ngay sau khi verify - để các test/fixture khác
        (vốn luôn login bằng config.LOGIN_PASSWORD) không bị lỗi đăng nhập ở các test chạy sau.
        """
        allure.dynamic.title(case["title"])
        old_password = config.LOGIN_PASSWORD if case["use_config_old_password"] else case["old_password"]
        page = home_page.page

        with allure.step("Mở menu avatar -> chọn 'Profile'"):
            profile_page = home_page.go_to_profile()

        with allure.step("Nhập Old Password / New Password / Confirmation"):
            profile_page.change_password(
                old_password=old_password,
                new_password=case["new_password"],
                confirm_password=case["confirm_password"],
            )
        with allure.step("Nhấn Save Profile"):
            profile_page.save()

        if case["expect_success"]:
            with allure.step("Xác minh hệ thống tự đăng xuất và chuyển về '/sign-in'"):
                profile_page.assert_redirected_to("/sign-in", case)
                profile_page.attach_screenshot(f"after_change_password_{case['case_id']}")
        else:
            with allure.step("Xác minh thông báo lỗi"):
                profile_page.attach_screenshot(f"after_change_password_{case['case_id']}")
                profile_page.assert_error_message(case, profile_page.confirm_password_input)

        if case.get("rollback") and case["expect_success"]:
            with allure.step(
                "Rollback: đăng nhập lại bằng mật khẩu MỚI, sau đó đổi mật khẩu về lại config.LOGIN_PASSWORD "
                "để các test/fixture sau vẫn đăng nhập được"
            ):
                relogin_page = LoginPage(page)
                relogin_page.open()
                relogin_page.login(config.LOGIN_EMAIL, case["new_password"])
                assert relogin_page.is_logged_in(), (
                    f"[{case['case_id']}] Rollback THẤT BẠI ở bước đăng nhập lại bằng mật khẩu mới "
                    f"'{case['new_password']}' - cần kiểm tra thủ công tài khoản {config.LOGIN_EMAIL}!"
                )

                rollback_home = HomePage(page)
                rollback_profile = rollback_home.go_to_profile()
                rollback_profile.change_password(
                    old_password=case["new_password"],
                    new_password=config.LOGIN_PASSWORD,
                    confirm_password=config.LOGIN_PASSWORD,
                )
                rollback_profile.save()

    # ---------------- Upload avatar ----------------
    # @allure.story("Upload ảnh đại diện")
    # @allure.severity(allure.severity_level.NORMAL)
    # def test_upload_avatar_success(self, home_page, tmp_path):
    #     with allure.step("Chuẩn bị file ảnh test (PNG 1x1 tạo động, không phụ thuộc file cố định)"):
    #         avatar_file = tmp_path / "avatar_test.png"
    #         png_1x1 = bytes.fromhex(
    #             "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753"
    #             "de0000000c4944415478da6360000002000100e921bc330000000049454e44ae426082"
    #         )
    #         avatar_file.write_bytes(png_1x1)

    #     with allure.step("Mở menu avatar -> chọn 'Profile' rồi upload avatar"):
    #         profile_page = home_page.go_to_profile()
    #         profile_page.upload_avatar(str(avatar_file))
    #         profile_page.save()
 
    #     with allure.step("Xác minh upload thành công"):
    #         profile_page.attach_screenshot("after_upload_avatar")
    #         profile_page.assert_toast_message("success")

    @allure.story("Upload ảnh đại diện")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "case", DATA["upload_cases"], ids=[c["case_id"] for c in DATA["upload_cases"]]
    )
    def test_upload_avatar(self, home_page, case):
        allure.dynamic.title(case["title"])
        file_path = AVATARS_DIR / case["file_name"]
        assert file_path.exists(), (
            f"Không tìm thấy file resource: {file_path}. "
            f"Kiểm tra lại thư mục test_data/avatars/ file avatar đã tồn tại."
        )

        with allure.step("Mở menu avatar -> chọn 'Profile'"):
            profile_page = home_page.go_to_profile()

        with allure.step(f"Chọn file '{case['file_name']}' để upload avatar"):
            profile_page.upload_avatar(str(file_path))
            profile_page.save()

        with allure.step("Xác minh thông báo kết quả"):
            profile_page.attach_screenshot(f"after_upload_{case['case_id']}")
            profile_page.assert_toast_message(case)

        if case["expect_success"]:
            with allure.step("Verify ảnh preview đã cập nhật đúng theo user hiện tại"):
                avatar_src = profile_page.get_avatar_src()
                assert "/$avatar-image/" in avatar_src, (
                    f"[{case['case_id']}] avatar src không đúng định dạng: '{avatar_src}'"
                )
                assert config.LOGIN_EMAIL in avatar_src, (
                    f"[{case['case_id']}] avatar src không chứa đúng email user hiện tại: "
                    f"'{avatar_src}'"
                )

    # ---------------- Nút Save bị disable khi chưa có thay đổi ----------------
    @allure.story("Trạng thái nút Save Profile")
    @allure.severity(allure.severity_level.MINOR)
    def test_save_button_disabled_when_no_change(self, home_page):
        with allure.step("Mở menu avatar -> chọn 'Profile', chưa chỉnh sửa gì"):
            profile_page = home_page.go_to_profile()

        with allure.step("Xác minh nút Save Profile đang bị disable"):
            profile_page.attach_screenshot("save_button_initial_state")
            assert not profile_page.is_save_button_enabled(), (
                "Kỳ vọng nút 'Save Profile' bị disable khi chưa có thay đổi nào trên form"
            )

        with allure.step("Sau khi sửa Name -> nút Save Profile phải được enable"):
            profile_page.update_name("Trigger Enable Save")
            assert profile_page.is_save_button_enabled(), (
                "Kỳ vọng nút 'Save Profile' được enable ngay sau khi có thay đổi"
            )

