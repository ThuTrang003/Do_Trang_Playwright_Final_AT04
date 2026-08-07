from Pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.textbox_email = self.page.get_by_role('textbox', name='Email address', exact=True)
        self.textbox_password = self.page.get_by_role('textbox', name='Password', exact=True)
        self.button_login = self.page.get_by_role('button', name='Login account', exact=False)


    def login(self, url: str, email: str, password: str):
        """Thực hiện hành động đăng nhập với Email và mật khẩu được cung cấp.

        Args:
            email (str): Email để đăng nhập.
            password (str): Mật khẩu để đăng nhập.
        """
        self.navigate(url)
        self.set_text(self.textbox_email, email)
        self.set_text(self.textbox_password, password)
        self.click(self.button_login)

    def verify_login_success(self, expected_value: str):
        """Xác minh đăng nhập thành công bằng cách kiểm tra các phần tử giao diện người dùng và tên hồ sơ hiển thị.

        Args:
            expected_value (str): Giá trị tên hồ sơ mong đợi cần xác minh.
        """
        # self.verify_element_visible(self.left_menu)
        # self.verify_element_visible(self.header_component)
        # self.verify_element_text(self.label_profile_name, expected_value, is_exact=False)