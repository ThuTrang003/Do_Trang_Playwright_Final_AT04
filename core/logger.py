"""
Cấu hình logging dùng chung cho toàn bộ framework.
- Ghi log ra console
- Ghi log ra file logs/test_run_<timestamp>.log
- Mỗi test có thể lấy logger riêng bằng get_logger(__name__)
"""
import logging
import sys
from datetime import datetime

from config.config import config

_LOG_FILE = config.LOG_DIR / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

_FORMATTER = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _build_root_logger() -> logging.Logger:
    root = logging.getLogger("book_automation")
    root.setLevel(config.LOG_LEVEL)

    if root.handlers:
        return root  # tránh add handler trùng khi import nhiều lần

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(_FORMATTER)

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(_FORMATTER)

    root.addHandler(console_handler)
    root.addHandler(file_handler)
    return root


_root_logger = _build_root_logger()


def get_logger(name: str = "book_automation") -> logging.Logger:
    """Trả về logger con, log của nó vẫn đi qua handler của root."""
    return logging.getLogger(f"book_automation.{name}") if name != "book_automation" else _root_logger


def get_log_file_path():
    return _LOG_FILE
