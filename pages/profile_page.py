from playwright.sync_api import Page

from pages.base_page import BasePage
from core.logger import get_logger

logger = get_logger("base_page")


class ProfilePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # --- Thông tin cá nhân ---
        self.name_input = page.locator('input[name="name"]')
        self.phone_input = page.locator('input[name="phone"]')
        self.division_input = page.locator("#address-division")
        self.ward_input = page.locator("#address-ward")
        self.address_textarea = page.locator("#address")
        self.avatar_file_input = page.locator('input[name="avatar"]')
        self.avatar_dropzone = page.get_by_text("Upload photo")
        self.email_input = page.locator('input[name="email"]')

        # --- Đổi mật khẩu (nằm chung trang Profile) ---
        self.old_password_input = page.locator('input[name="oldPassword"]')
        self.new_password_input = page.locator('input[name="password"]')
        self.confirm_password_input = page.locator('input[name="password_confirmation"]')

        # --- Nút hành động ---
        self.save_button = page.get_by_role("button", name="Save Profile")
        self.reset_button = page.get_by_role("button", name="Reset")

    # ---------- Thông tin cá nhân ----------
    def update_name(self, name: str):
        self.fill(self.name_input, name, "Name")
        return self

    def update_phone(self, phone: str):
        self.fill(self.phone_input, phone, "Phone")
        return self

    def update_division(self, division: str):
        """Select Division from MUI Autocomplete."""
        self.division_input.click()
        self.division_input.fill(division)
        
        logger.info(f"Division value: {division}")

        option = self.page.get_by_role("option", name=division)
        option.wait_for(state="visible")
        option.filter(has_text=division)
        option.click()
            
        return self

    def update_ward(self, ward: str):
        """Select Ward from MUI Autocomplete."""
        self.ward_input.click()
        self.ward_input.fill(ward)

        option = self.page.get_by_role("option", name=ward)
        option.wait_for(state="visible")
        option.filter(has_text=ward)
        option.click()

        return self

    def upload_avatar(self, file_path: str):
        # input[type=file] bị ẩn (visually-hidden) -> set_input_files vẫn hoạt động trực tiếp
        self.avatar_file_input.set_input_files(file_path)
        return self

    # ---------- Đổi mật khẩu ----------
    def change_password(self, old_password: str, new_password: str, confirm_password: str):
        self.fill(self.old_password_input, old_password, "Old Password")
        self.fill(self.new_password_input, new_password, "New Password")
        self.fill(self.confirm_password_input, confirm_password, "Password Confirmation")
        return self

    # ---------- Hành động ----------
    def save(self):
        self.click(self.save_button, "Nút Save Profile")
        return self

    def reset(self):
        self.click(self.reset_button, "Nút Reset")
        return self

    def is_save_button_enabled(self) -> bool:
        return self.save_button.is_enabled()

    # ---------- Getter để verify ----------
    def get_name_value(self) -> str:
        return self.name_input.input_value()

    def get_phone_value(self) -> str:
        return self.phone_input.input_value()

    def get_email_value(self) -> str:
        return self.email_input.input_value()

    def get_division_value(self) -> str:
        return self.division_input.input_value()
