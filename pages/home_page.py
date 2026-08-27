from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.profile_page import ProfilePage
from pages.settings_page import SettingsPage


class HomePage(BasePage):
    PATH = "/"

    def __init__(self, page: Page):
        super().__init__(page)
        self.avatar_button = page.locator("header button:has(.MuiAvatar-root)")
        self.profile_menu_item = page.get_by_role("menuitem", name="Profile")
        self.settings_menu_item = page.get_by_role("menuitem", name="Settings")
        self.home_menu_item = page.get_by_role("menuitem", name="Home")
        self.logout_button = page.get_by_role("button", name="Logout")

    def open(self):
        """Chỉ dùng để mở Home LẦN ĐẦU (vd ngay sau khi login redirect về '/').
        KHÔNG gọi lại open() giữa chừng test vì sẽ full-reload -> mất session."""
        self.goto(self.PATH)
        return self

    def open_avatar_menu(self):
        self.goto("/")
        self.avatar_button.wait_for(state="visible", timeout=10000)
        self.click(self.avatar_button, "Nút Avatar (mở menu tài khoản)")
        self.profile_menu_item.wait_for(state="visible", timeout=10000)
        return self

    def go_to_profile(self) -> ProfilePage:
        """Điều hướng client-side (không reload) tới 'Change my profile'."""
        self.open_avatar_menu()
        self.click(self.profile_menu_item, "Menu item 'Profile'")
        return ProfilePage(self.page)

    def go_to_settings(self) -> SettingsPage:
        """Điều hướng client-side (không reload) tới 'Setting account'."""
        self.open_avatar_menu()
        self.click(self.settings_menu_item, "Menu item 'Settings'")
        return SettingsPage(self.page)

    def logout(self):
        self.open_avatar_menu()
        self.click(self.logout_button, "Nút Logout")
        return self
