from Pages.base_page import BasePage
from Utils.path_helper import PathFile

class ProfilePage(BasePage):
    URL_PROFILE_PAGE = "https://book.anhtester.com/user-management/my-profile"

    def __init__(self, page):
        super().__init__(page)
        self.avatar_input = page.locator("//input[@name='avatar']")

        self.name = page.get_by_role("textbox", name="Name")
        self.phone = page.get_by_role("textbox", name="Phone")
        self.select_division = page.get_by_role("combobox", name="Division")
        self.select_ward = page.get_by_role("combobox", name="Ward")
        self.address = page.get_by_role("textbox", name="Address")
        self.email = page.get_by_role("textbox", name="Email")

        self.old_password = page.get_by_role("textbox", name="Old Password")
        self.new_password = page.get_by_role("textbox", name="Password")
        self.confirm_password = page.get_by_role("textbox", name="Password Confirmation")

        self.save = page.get_by_role("button",name="Save Profile")

    def navigate_profile_page(self):
        self.navigate(self.URL_PROFILE_PAGE)

    def upload_photo(self, file_path: str):
        """
        Upload avatar.
        """
        self.upload_file(self.avatar_input, PathFile.get_string_file_path(file_path))
        self.click(self.save)

    def update_profile(
        self,
        name: str = None,
        email:str = None,
        phone: str = None,
        division: str = None,
        ward: str = None,
        address: str = None,
        avatar_photo:str = None
    ):

        # if profile.name:
        if name is not None:
            self.set_text(self.name, name)

        if email is not None:
            self.set_text(self.email, email)

        if phone is not None:
            self.set_text(self.phone, phone)

        if division is not None:
            self.select_dropdown(self.select_division, division, True)

        if ward is not None:
            self.select_dropdown(self.select_ward, ward, True)

        if address is not None:
            self.set_text(self.address, address)

        if avatar_photo is not None:
            self.upload_file(self.avatar_input, PathFile.get_string_file_path(avatar_photo))

        self.click(self.save)

    def change_password(self, old_password: str, new_password: str, confirm_password: str):
        """
        Change password.
        """
        self.set_text(self.old_password, old_password)
        self.set_text(self.new_password, new_password)
        self.set_text(self.confirm_password, confirm_password)
        self.click(self.save)