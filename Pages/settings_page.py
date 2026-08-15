"""
SettingsPage - chức năng "Setting account"
(chỉ truy cập được bằng cách điều hướng qua HomePage.go_to_settings(),
KHÔNG có route/URL riêng để goto() trực tiếp - xem giải thích trong pages/home_page.py)

Selector lấy TRỰC TIẾP từ DOM thật:
- Theme: 3 tab với role="tab", tên "Light" / "Dark" / "System"
- Select color: danh sách các ô màu (MuiBox) KHÔNG có text/aria-label riêng
  -> chọn theo vị trí (index) trong danh sách, xem TODO bên dưới.
- Nút Save / Reset: 2 button dưới cùng, LUÔN enabled (không bị disable theo trạng thái dirty
  như trang Profile).

Ghi chú quan trọng:
- API thật đứng sau nút Save: CÙNG endpoint PATCH /api/profile như trang Profile,
  nhưng payload chỉ gồm {"config": {"theme": "...", "mainColor": "#hex"}}.
- "mainColor" là mã hex (vd "#4caf50"), KHÔNG phải tên màu -> nếu muốn assert theo API,
  cần map vị trí swatch UI sang đúng mã hex tương ứng (hiện chưa xác nhận được mapping
  chính xác trong DOM vì swatch không có title/aria-label).

TODO quan trọng: các ô màu (color swatch) trong DOM thu thập được không có aria-label/title
riêng biệt để phân biệt (chỉ có class css-xxxx do Emotion sinh ngẫu nhiên, không ổn định giữa
các lần build). Vì vậy hàm select_color() ở đây chọn theo INDEX (vị trí) trong lưới màu.
Nếu trang thực tế có thêm title/aria-label cho từng màu (nên kiểm tra lại bằng DevTools),
hãy đổi sang get_by_label(color_name) để test rõ nghĩa và ổn định hơn.
"""
from playwright.sync_api import Page

from pages.base_page import BasePage


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
        self.color_swatches = self.color_card.locator(".MuiCardContent-root .MuiBox-root")

        # --- Nút hành động ---
        self.save_button = page.get_by_role("button", name="Save")
        self.reset_button = page.get_by_role("button", name="Reset")

    # ---------- Theme ----------
    def select_theme(self, theme: str):
        """theme: 'light' | 'dark' | 'system'"""
        tab_map = {
            "light": self.theme_light_tab,
            "dark": self.theme_dark_tab,
            "system": self.theme_system_tab,
        }
        tab = tab_map[theme.lower()]
        self.click(tab, f"Tab theme '{theme}'")
        return self

    def get_selected_theme(self) -> str:
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
        """Chọn màu theo vị trí (0-based) trong lưới màu."""
        self.color_swatches.nth(index).click()
        return self

    def color_count(self) -> int:
        return self.color_swatches.count()

    # ---------- Hành động ----------
    def save(self):
        self.click(self.save_button, "Nút Save settings")
        return self

    def reset(self):
        self.click(self.reset_button, "Nút Reset settings")
        return self
