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
        self.avatar_preview_image = page.locator("img[src*='avatar-image']")
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
        """
        Cập nhật tên người dùng.
        Args:
            name: Tên mới cần cập nhật.
        Returns:
            ProfilePage: Đối tượng ProfilePage hiện tại.
        """
        self.fill(self.name_input, name, "Name")
        return self

    def update_phone(self, phone: str):
        """
        Cập nhật số điện thoại người dùng.

        Args:
            phone: Số điện thoại mới.

        Returns:
            ProfilePage: Đối tượng ProfilePage hiện tại.
        """
        self.fill(self.phone_input, phone, "Phone")
        return self

    def update_division(self, division: str):
        """
        Chọn Division từ MUI Autocomplete.

        Args:
            division: Tên Division cần chọn.

        Returns:
            ProfilePage: Đối tượng ProfilePage hiện tại.
        """
        self.division_input.click()
        self.division_input.fill(division)
        
        logger.info(f"Division value: {division}")

        option = self.page.get_by_role("option", name=division)
        option.wait_for(state="visible")
        option.filter(has_text=division)
        option.click()
            
        return self

    def update_ward(self, ward: str):
        """
        Chọn Ward từ MUI Autocomplete.

        Args:
            ward: Tên Ward cần chọn.

        Returns:
            ProfilePage: Đối tượng ProfilePage hiện tại.
        """
        self.ward_input.click()
        self.ward_input.fill(ward)

        logger.info(f"Ward value: {ward}")
        option = self.page.get_by_role("option", name=ward)
        option.wait_for(state="visible")
        option.filter(has_text=ward)
        option.click()

        return self

    def upload_avatar(self, file_path: str):
        """
        Upload avatar từ file.

        Args:
            file_path: Đường dẫn đến file avatar.

        Returns:
            ProfilePage: Đối tượng ProfilePage hiện tại.
        """
        self.avatar_file_input.set_input_files(file_path)
        return self

    # ---------- Đổi mật khẩu ----------
    def change_password(self, old_password: str, new_password: str, confirm_password: str):
        """
        Nhập thông tin để đổi mật khẩu.

        Args:
            old_password: Mật khẩu hiện tại.
            new_password: Mật khẩu mới.
            confirm_password: Xác nhận mật khẩu mới.

        Returns:
            ProfilePage: Đối tượng ProfilePage hiện tại.
        """
        self.fill(self.old_password_input, old_password, "Old Password")
        self.fill(self.new_password_input, new_password, "New Password")
        self.fill(self.confirm_password_input, confirm_password, "Password Confirmation")
        return self

    # ---------- Hành động ----------
    def save(self):
        """
        Lưu thông tin Profile.

        Returns:
            ProfilePage: Đối tượng ProfilePage hiện tại.
        """
        self.click(self.save_button, "Nút Save Profile")
        return self

    def reset(self):
        """
        Reset thông tin Profile về trạng thái ban đầu.

        Returns:
            ProfilePage: Đối tượng ProfilePage hiện tại.
        """

        self.click(self.reset_button, "Nút Reset")
        return self

    def is_save_button_enabled(self) -> bool:
        """
        Kiểm tra trạng thái enabled của nút Save Profile.

        Returns:
            bool: True nếu nút Save được enable, ngược lại False.
        """
        return self.save_button.is_enabled()

    # ---------- Getter để verify ----------
    def get_name_value(self) -> str:
        """
        Lấy giá trị hiện tại của trường Name.

        Returns:
            str: Giá trị Name hiện tại.
        """
        return self.name_input.input_value()

    def get_avatar_src(self, timeout: int = 8000) -> str:
        """
        Lấy giá trị src của ảnh preview avatar.

        Args:
            timeout: Thời gian tối đa chờ avatar hiển thị, tính bằng milliseconds.

        Returns:
            str: Giá trị src của avatar.
                Trả về chuỗi rỗng nếu không tìm thấy avatar.
        """
        try:
            self.avatar_preview_image.first.wait_for(state="visible", timeout=timeout)
            return self.avatar_preview_image.first.get_attribute("src") or ""
        except Exception:
            return ""

    def get_phone_value(self) -> str:
        """
        Lấy giá trị hiện tại của trường Phone.

        Returns:
            str: Giá trị Phone hiện tại.
        """
        return self.phone_input.input_value()

    def get_email_value(self) -> str:
        """
        Lấy giá trị hiện tại của trường Email.

        Returns:
            str: Giá trị Email hiện tại.
        """
        return self.email_input.input_value()

    def get_division_value(self) -> str:
        """
        Lấy giá trị Division hiện tại.

        Returns:
            str: Giá trị Division hiện tại.
        """
        return self.division_input.input_value()
