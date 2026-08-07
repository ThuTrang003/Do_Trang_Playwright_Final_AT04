from datetime import datetime

class TextData:
    @staticmethod
    def create_text_data(input_text: str) -> str:
        """Tạo một chuỗi duy nhất bằng cách nối thêm mốc thời gian hiện tại vào văn bản đầu vào.

        Args:
            input_text (str): Văn bản gốc cần nối thêm mốc thời gian.

        Returns:
            str: Chuỗi văn bản duy nhất chứa văn bản gốc và mốc thời gian.
        """
        return f"{input_text}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    