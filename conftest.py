"""
conftest.py gốc của project.
Chứa:
- Fixture khởi tạo Playwright browser/page theo cấu hình .env
- Fixture đăng nhập sẵn (authenticated_page) -> LUÔN dừng lại ở HomePage sau khi login.
  Muốn tới "Change my profile" / "Setting account" PHẢI dùng HomePage.go_to_profile()/
  go_to_settings() (điều hướng client-side), KHÔNG được page.goto()/reload() vì hệ thống
  lưu phiên đăng nhập trong bộ nhớ JS - reload sẽ văng về Login.
- Fixture api_client (Playwright APIRequestContext) cho test API
- Hook tự động chụp screenshot + đính log vào Allure khi test FAIL
- Ghi file allure environment.properties để hiển thị thông tin môi trường trên report
"""
import pytest
import allure
from playwright.sync_api import sync_playwright

from config.config import config
from core.logger import get_logger
from core.api_client import ApiClient
from pages.login_page import LoginPage
from pages.home_page import HomePage

logger = get_logger("conftest")


# ---------------------------------------------------------------------------
# Playwright browser / context / page
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser_type = getattr(playwright_instance, config.BROWSER)
    browser = browser_type.launch(headless=config.HEADLESS, slow_mo=config.SLOW_MO)
    yield browser
    browser.close()


@pytest.fixture
def context(browser):
    context = browser.new_context(viewport=config.VIEWPORT)
    context.set_default_timeout(config.DEFAULT_TIMEOUT)
    yield context
    context.close()


@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()


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

# ---------------------------------------------------------------------------
# API request context
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def api_request_context(playwright_instance):
    ctx = playwright_instance.request.new_context(base_url=config.API_BASE_URL)
    yield ctx
    ctx.dispose()

@pytest.fixture
def api_client(api_request_context):
    return ApiClient(api_request_context, base_url=config.API_BASE_URL)


@pytest.fixture(scope="session")
def auth_token(playwright_instance):
    """
    Đăng nhập qua API 1 lần / session để lấy token dùng chung cho các test API.

    TODO QUAN TRỌNG (chưa xác nhận được với hệ thống thật):
    1) Path chính xác của API Login (đang đoán "/api/login" - xem api/endpoints.py).
    2) Cơ chế xác thực thật là Bearer token (header Authorization) hay cookie phiên?
       -> Mở tab Headers của request GET /api/me hoặc PATCH /api/profile trong DevTools,
          xem có "Authorization: Bearer ..." trong Request Headers không.
       -> Nếu hệ thống dùng COOKIE thay vì Bearer token, cách lấy token dưới đây sẽ không
          hoạt động; thay vào đó cần dùng `context.request` (chia sẻ cookie với browser
          context đã login qua UI) thay vì tạo APIRequestContext độc lập như hiện tại.
    """
    ctx = playwright_instance.request.new_context(base_url=config.API_BASE_URL)
    from api.endpoints import Endpoints

    response = ctx.post(
        Endpoints.LOGIN,
        data={"email": config.LOGIN_EMAIL, "password": config.LOGIN_PASSWORD},
    )
    token = None
    if response.ok:
        try:
            body = response.json()
            token = body.get("token") or body.get("accessToken") or body.get("data", {}).get("token")
        except Exception as e:
            logger.warning(f"Không parse được response login để lấy token: {e}")
    else:
        logger.warning(
            f"Login API trả về {response.status} - kiểm tra lại Endpoints.LOGIN trong api/endpoints.py "
            f"(có thể path chưa đúng, xem TODO trong file đó)."
        )
    ctx.dispose()
    return token


# ---------------------------------------------------------------------------
# Hook: tự động chụp screenshot + đính log khi test FAIL (bắt buộc theo yêu cầu)
# ---------------------------------------------------------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call" and rep.failed:
        logger.error(f"TEST FAILED: {item.nodeid}")

        # Nếu test có dùng fixture 'page' hoặc 'authenticated_page' -> chụp screenshot
        page = item.funcargs.get("page") or item.funcargs.get("authenticated_page")
        if page is not None:
            try:
                screenshot_bytes = page.screenshot(full_page=True)
                allure.attach(
                    screenshot_bytes,
                    name=f"FAILED_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
                # Lưu thêm ra thư mục screenshots/ dạng file để tiện xem ngoài Allure
                screenshot_path = config.SCREENSHOT_DIR / f"{item.name}.png"
                with open(screenshot_path, "wb") as f:
                    f.write(screenshot_bytes)
                logger.info(f"Đã lưu screenshot lỗi tại: {screenshot_path}")
            except Exception as e:
                logger.warning(f"Không thể chụp screenshot khi fail: {e}")


@pytest.fixture(autouse=True, scope="session")
def _write_allure_environment():
    """Ghi thông tin môi trường ra allure-results/environment.properties."""
    env_file = config.ALLURE_RESULTS_DIR / "environment.properties"
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(f"BASE_URL={config.BASE_URL}\n")
        f.write(f"API_BASE_URL={config.API_BASE_URL}\n")
        f.write(f"BROWSER={config.BROWSER}\n")
        f.write(f"HEADLESS={config.HEADLESS}\n")
    yield
