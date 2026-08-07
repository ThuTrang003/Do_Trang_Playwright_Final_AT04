from playwright.sync_api import Page, Locator, Error as PlaywrightError, expect

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        """
        Điều hướng trình duyệt đến URL chỉ định.

        Args:
            url (str): Địa chỉ URL cần điều hướng đến.

        Raises:
            PlaywrightError: Khi URL không hợp lệ hoặc không thể kết nối đến trang.
        """
        try:
            self.page.goto(url)
        except PlaywrightError as e:
            raise PlaywrightError(
                f"Không thể navigate đến URL: {url}"
            ) from e

    def click(self, element_locator: Locator):
        """
        Click vào một element trên trang.

        Args:
            element_locator (Locator): Locator của element cần click.

        Raises:
            PlaywrightError: Khi không thể thực hiện click vào element.
        """
        try:
            element_locator.click()
        except PlaywrightError as e:
            raise PlaywrightError(
                f"Không thực hiện click được vào test object {element_locator}"
            ) from e

    def set_text(self, element_locator: Locator, input_value: str):
        """
        Nhập giá trị văn bản vào một ô input.

        Args:
            element_locator (Locator): Locator của element input cần nhập liệu.
            input_value (str): Giá trị văn bản cần nhập vào.

        Raises:
            PlaywrightError: Khi không thể nhập giá trị vào element.
        """
        try:
            element_locator.fill(input_value)
        except PlaywrightError as e:
            raise PlaywrightError(
                f"Không thực hiện nhập {input_value} vào test object {element_locator}"
            ) from e

    def select_dropdown(self, element_locator: Locator, option: str, by_label: bool = False):
        """
        Chọn một option trong dropdown.

        Args:
            element_locator (Locator): Locator của element <select>.
            option (str): Giá trị cần chọn.
            by_label (bool): Flag xác định kiểu chọn option.
                - False (default) : Chọn theo thuộc tính value của option.
                - True            : Chọn theo text hiển thị (label) của option.

        Raises:
            PlaywrightError: Khi không tìm thấy option hoặc không thể chọn.
        """
        try:
            if by_label:
                element_locator.select_option(label=option)
            else:
                element_locator.select_option(value=option)
        except PlaywrightError as e:
            select_by = "label" if by_label else "value"
            raise PlaywrightError(
                f"Không thể chọn option '{option}' (by {select_by}) trong dropdown {element_locator}"
            ) from e

    def upload_file(self, element_locator: Locator, file_path: str):
        """
        Upload file thông qua element input[type=file].

        Args:
            element_locator (Locator): Locator của element input[type=file].
            file_path (str): Đường dẫn tuyệt đối hoặc tương đối đến file cần upload.

        Raises:
            FileNotFoundError: Khi file không tồn tại tại đường dẫn đã chỉ định.
            PlaywrightError: Khi element không phải input[type=file] hoặc không thể tương tác.
        """
        try:
            element_locator.set_input_files(file_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Không tìm thấy file để upload: '{file_path}'"
            ) from e
        except PlaywrightError as e:
            raise PlaywrightError(
                f"Không thể upload file '{file_path}' vào {element_locator}"
            ) from e

    def verify_element_visible(self, element_locator: Locator):
        """
        Kiểm tra element có hiển thị trên trang hay không.

        Args:
            element_locator (Locator): Locator của element cần kiểm tra.

        Raises:
            PlaywrightError: Khi element không hiển thị trên trang.
        """
        try:
            expect(element_locator).to_be_visible()
        except PlaywrightError as e:
            raise PlaywrightError(
                f"Element không hiển thị trên trang: {element_locator}"
            ) from e

    def verify_element_text(self, element_locator: Locator, expected_text: str, is_exact: bool = True):
        """
        Kiểm tra text của element.

        Args:
            element_locator (Locator): Locator của element cần kiểm tra.
            expected_text (str): Text kỳ vọng cần so khớp.
            is_exact (bool): Flag xác định kiểu so khớp text.
                - True  (default) : Khớp toàn bộ text (exact match).
                - False           : Chỉ cần chứa chuỗi con (partial match).

        Raises:
            PlaywrightError: Khi text của element không khớp với expected_text.
        """
        try:
            if is_exact:
                expect(element_locator).to_have_text(expected_text)
            else:
                expect(element_locator).to_contain_text(expected_text)
        except PlaywrightError as e:
            mode = "have_text" if is_exact else "contains_text"
            raise PlaywrightError(
                f"Verify text thất bại | Element: {element_locator} "
                f"| Expected: '{expected_text}' | Mode: {mode}"
            ) from e    