from playwright.sync_api import Page
from pages.base_page import BasePage

class LoginPage(BasePage):

    PATH = "/sign-in" 

    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = page.get_by_role("textbox", name="Email address")
        self.password_input = page.get_by_role("textbox", name="Password")
        self.login_button = page.get_by_role("button", name="Login account")
    
    def open(self):
        self.goto(self.PATH)
        return self

    def login(self, email: str, password: str):
        self.fill(self.email_input, email, "Email address")
        self.fill(self.password_input, password, "Password")
        self.click(self.login_button, "Login account")
        return self

    def get_error_message(self) -> str:
        return self.wait_for_toast()

    def is_logged_in(self) -> bool:
        """Sau khi login thành công, hệ thống điều hướng ra khỏi /sign-in."""
        try:
            self.page.wait_for_url(lambda url: "/sign-in" not in url, timeout=10000)
            return True
        except Exception:
            return False
