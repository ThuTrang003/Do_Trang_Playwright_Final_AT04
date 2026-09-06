from playwright.sync_api import Page
from pages.base_page import BasePage
from core.logger import get_logger

logger = get_logger("base_page")

class SettingsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # --- Theme ---
        self.theme_light_tab = page.get_by_role("tab", name="Light")
        self.theme_dark_tab = page.get_by_role("tab", name="Dark")
        self.theme_system_tab = page.get_by_role("tab", name="System")

        # --- Select color ---
        # Card "Select color" -> tìm theo tiêu đề rồi lấy toàn bộ swatch bên trong CardContent
        self.color_card = page.locator("div.MuiCard-root", has=page.get_by_text("Select color", exact=True))
        self.color_swatches = self.color_card.locator("div.MuiCardContent-root div.MuiStack-root > div.MuiBox-root")

        # --- Nút hành động ---
        self.save_button = page.get_by_role("button", name="Save")
        self.reset_button = page.get_by_role("button", name="Reset")

    # ---------- Theme ----------
    def select_theme(self, theme: str):
        """
        Chọn theme cho Settings.

        Args:
            theme: Theme cần chọn, gồm 'light', 'dark' hoặc 'system'.

        Returns:
            SettingsPage: Đối tượng SettingsPage hiện tại.
        """
        tab_map = {
            "light": self.theme_light_tab,
            "dark": self.theme_dark_tab,
            "system": self.theme_system_tab,
        }
        tab = tab_map[theme.lower()]
        self.click(tab, f"Tab theme '{theme}'")
        return self

    def get_selected_theme(self) -> str:
        """
        Lấy theme đang được chọn.

        Returns:
            str: Theme hiện tại gồm 'light', 'dark', 'system'.
                Trả về chuỗi rỗng nếu không có theme nào được chọn.
        """
        for name, tab in (
            ("light", self.theme_light_tab),
            ("dark", self.theme_dark_tab),
            ("system", self.theme_system_tab),
        ):
            if tab.get_attribute("aria-selected") == "true":
                return name
        return ""

    # ---------- Select color ----------
    def select_color(self, index: int):
        """
        Chọn màu theo vị trí trong lưới màu.

        Args:
            index: Vị trí màu cần chọn, bắt đầu từ 0.

        Returns:
            SettingsPage: Đối tượng SettingsPage hiện tại.
        """
        color = self.color_swatches.nth(index)

        logger.info(f"HTML: {color.evaluate('(el) => el.outerHTML')}")
        color.click()
        return self

    def color_count(self) -> int:
        """
        Lấy tổng số màu có trong lưới màu.

        Returns:
            int: Số lượng màu.
        """
        self.color_swatches.first.wait_for(state="visible")
        count = self.color_swatches.count()
        logger.info(f"Count color: {count}")
        return count

    # ---------- Hành động ----------
    def save(self):
        """
        Lưu các thiết lập Settings.

        Returns:
            SettingsPage: Đối tượng SettingsPage hiện tại.
        """
        self.click(self.save_button, "Nút Save settings")
        return self

    def reset(self):
        """
        Reset các thiết lập Settings về trạng thái ban đầu.

        Returns:
            SettingsPage: Đối tượng SettingsPage hiện tại.
        """
        self.click(self.reset_button, "Nút Reset settings")
        return self
