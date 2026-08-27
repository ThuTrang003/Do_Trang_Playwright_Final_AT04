import pytest

from config.config import config
from pages.login_page import LoginPage
from pages.home_page import HomePage

@pytest.fixture
def loggedin_home_storage(context, auth_token):
    context.add_init_script(
        f"window.localStorage.setItem('accessToken', '{auth_token}')"
    )
    page = context.new_page()
    home_page = HomePage(page)

    yield home_page

@pytest.fixture
def authenticated_page(page):
    """
    Page đã đăng nhập sẵn bằng tài khoản trong .env, DỪNG LẠI ở HomePage ('/').
    Từ đây, dùng HomePage(page).go_to_profile() / go_to_settings() để điều hướng tiếp
    """
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(config.LOGIN_EMAIL, config.LOGIN_PASSWORD)
    assert login_page.is_logged_in(), "Đăng nhập thất bại trong fixture authenticated_page"
    yield page


@pytest.fixture
def home_page(authenticated_page):
    """Trả về HomePage đã sẵn sàng để điều hướng tới Profile/Settings."""
    return HomePage(authenticated_page)