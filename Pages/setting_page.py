from Pages.base_page import BasePage


class SettingPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        # Theme
        self.light_theme = page.get_by_role("tab", name="Light")
        self.dark_theme = page.get_by_role("tab", name="Dark")
        self.system_theme = page.get_by_role("tab", name="System")

        # Color
        self.color_card = page.locator("//span[text()='Select color']/ancestor::div[contains(@class,'MuiPaper-root')]")
        self.colors = self.color_card.locator(".//div[contains(@class,'MuiBox-root')]")

        # Button
        self.btn_save = page.get_by_role("button", name="Save")
        self.btn_reset = page.get_by_role("button", name="Reset")


    def switch_theme(self, theme: str):
        """
        Switch application theme.

        Args:
            theme: light | dark | system
        """

        theme = theme.lower()

        if theme == "light":
            self.click(self.light_theme)
        elif theme == "dark":
            self.click(self.dark_theme)
        elif theme == "system":
            self.click(self.system_theme)
        else:
            raise ValueError(f"Theme '{theme}' is not supported.")

        self.click(self.btn_save)

    def reset_setting(self):
        """
        Reset setting
        """
        self.click(self.btn_reset)

    def select_color(self, index: int):
        """
        Select color by index.

        Args:
            index (int): vị trí màu (0 -> n-1)
        """
        self.click(self.colors.nth(index))
        self.click(self.btn_save)