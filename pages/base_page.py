from __future__ import annotations

import allure
from playwright.sync_api import Page, Locator, expect

from config.config import config
from core.logger import get_logger

logger = get_logger("base_page")


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = config.BASE_URL
        self.SONNER_TOAST = (
            "section[aria-label*='Notifications'] "
            "[data-sonner-toast]"
        )

    # ---------- Điều hướng ----------
    def goto(self, path: str = "/"):
        url = path if path.startswith("http") else f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        logger.info(f"Navigate -> {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    # ---------- Thao tác dùng chung ----------
    def click(self, locator: Locator, description: str = ""):
        logger.info(f"Click: {description or locator}")
        locator.click()

    def fill(self, locator: Locator, value: str, description: str = ""):
        logger.info(f"Fill '{value}' vào: {description or locator}")
        locator.fill(value)

    def get_text(self, locator: Locator) -> str:
        return locator.inner_text().strip()

    def is_visible(self, locator: Locator, timeout: int = 5000) -> bool:
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    # ---------- Toast (notistack) ----------
    def wait_for_toast(self, timeout: int = 8000) -> str:
        """
        Chờ toast notistack xuất hiện trong <section aria-label="Notifications alt+T">.
        Fallback sang các selector thông báo phổ biến khác nếu không khớp.
        """
        try:
            # Locate the latest Sonner toast
            toast = self.page.locator(self.SONNER_TOAST).last

            # Wait until the toast is visible
            toast.wait_for(state="visible", timeout=timeout)

            # Get toast message
            message = toast.inner_text().strip()

            logger.info(f"Thông báo hiển thị: {message}")

            return message

        except Exception as e:
            logger.warning(
                f"Không thể lấy thông báo message: {e}"
            )
            raise

    # ---------- Validate lỗi MUI ----------
    def has_field_error(self, input_locator: Locator) -> bool:
        """
        Kiểm tra 1 input MUI TextField đang ở trạng thái lỗi:
        - input có aria-invalid="true", HOẶC
        - .MuiFormControl-root cha có class 'Mui-error'
        """
        try:
            aria_invalid = input_locator.get_attribute("aria-invalid")
            if aria_invalid == "true":
                return True
        except Exception:
            pass
 
        form_control = input_locator.locator(
            "xpath=ancestor::div[contains(@class,'MuiFormControl-root')][1]"
        )
        try:
            class_attr = form_control.get_attribute("class") or ""
            return "Mui-error" in class_attr
        except Exception:
            return False
 
    def get_field_error_text(self, input_locator: Locator, timeout: int = 5000) -> str:
        """
        Đọc nội dung text lỗi validate NGAY DƯỚI field
        """
        form_control = input_locator.locator(
            "xpath=ancestor::div[contains(@class,'MuiFormControl-root')][1]"
        )
        helper_text = form_control.locator(".MuiFormHelperText-root")
        try:
            helper_text.first.wait_for(state="visible", timeout=timeout)
            return helper_text.first.inner_text().strip()
        except Exception:
            return ""
 
    def get_first_field_error_text(self, *input_locators: Locator, timeout: int = 3000) -> str:
        """
        Kiểm tra NHIỀU field cùng lúc (vd Name + Phone, hoặc chỉ 1 field như Password), trả về text lỗi ĐẦU TIÊN tìm thấy. 
        Trả về "" nếu không field nào có lỗi hiển thị inline 
        """
        for locator in input_locators:
            text = self.get_field_error_text(locator, timeout=timeout)
            if text:
                return text
        return ""
 
    def wait_for_error_signal(self, *field_locators: Locator, timeout: int = 6000) -> str:
        """
        Chờ ĐỒNG THỜI (race) giữa: lỗi field (helper text dưới các field truyền vào)
        HOẶC toast Sonner - trả về nội dung của tín hiệu nào xuất hiện TRƯỚC.
        Dùng để xử lý trường hợp không biết trước lỗi hiển thị qua field hay qua toast.
        """
        combined = self.page.locator(self.SONNER_TOAST)
        for field_locator in field_locators:
            form_control = field_locator.locator(
                "xpath=ancestor::div[contains(@class,'MuiFormControl-root')][1]"
            )
            error_text_locator = form_control.locator(".MuiFormHelperText-root")
            combined = combined.or_(error_text_locator)
 
        combined.first.wait_for(state="visible", timeout=timeout)
        return combined.first.inner_text().strip()
 
    # ---------- Assert message dùng chung (gộp chờ + assert + build lỗi) ----------
    def assert_toast_message(self, case, timeout: int = 8000) -> str:
        """
        Chờ toast Sonner và assert nội dung chứa message kỳ vọng. Dùng cho case CHẮC CHẮN
        kết quả hiển thị qua toast (không có field-error liên quan).
        `case` có thể là:
        - dict (case data-driven từ JSON) -> lấy case['expect_message_contains'] + case['case_id']
        - str (message kỳ vọng đơn giản, dùng cho test không parametrize) -> vd "success"
        Trả về message thật.
        """
        if isinstance(case, dict):
            case_id = case.get("case_id", "")
            expected = case["expect_message_contains"]
        else:
            case_id = ""
            expected = case
 
        message = self.wait_for_toast(timeout=timeout)
        assert expected.lower() in message.lower(), (
            f"[{case_id}] Kỳ vọng thông báo chứa '{expected}', thực tế: '{message}'"
        )
        return message
 
    def assert_error_message(self, case: dict, *field_locators: Locator, timeout: int = 6000) -> str:
        """
        Chờ ĐỒNG THỜI field-error/toast (wait_for_error_signal) và assert nội dung chứa
        `case['expect_message_contains']`. Dùng cho case KHÔNG biết trước lỗi hiển thị
        qua field hay qua toast (trường hợp phổ biến nhất khi test validate lỗi).
        """
        error_text = self.wait_for_error_signal(*field_locators, timeout=timeout)
        assert case["expect_message_contains"].lower() in error_text.lower(), (
            f"[{case['case_id']}] Kỳ vọng thông báo (field hoặc toast) chứa "
            f"'{case['expect_message_contains']}', thực tế: '{error_text}'"
        )
        return error_text
 
    def assert_redirected_to(self, url_substring: str, case: dict, timeout: int = 10000):
        """
        Assert trang tự động điều hướng tới URL chứa `url_substring` 
        """
        try:
            self.page.wait_for_url(lambda url: url_substring in url, timeout=timeout)
            redirected = True
        except Exception:
            redirected = False
        assert redirected, (
            f"[{case['case_id']}] Kỳ vọng URL chuyển hướng chứa '{url_substring}', "
            f"nhưng URL hiện tại là '{self.page.url}'"
        )

    # ---------- Screenshot & Allure ----------
    def attach_screenshot(self, name: str = "screenshot"):
        try:
            screenshot_bytes = self.page.screenshot(full_page=True)
            allure.attach(
                screenshot_bytes,
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            logger.warning(f"Không thể chụp screenshot: {e}")

    def assert_visible(self, locator: Locator, message: str = ""):
        expect(locator).to_be_visible(timeout=config.DEFAULT_TIMEOUT)
