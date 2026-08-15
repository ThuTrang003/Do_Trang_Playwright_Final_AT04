"""
Trung tâm cấu hình của cả framework.
Toàn bộ giá trị được đọc từ file .env (KHÔNG hard code data trong code)
=> Tuân thủ yêu cầu "Config bằng file .env" + "Nghiêm cấm hard code data".
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def _get_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "y")


def _get_int(key: str, default: int) -> int:
    val = os.getenv(key)
    try:
        return int(val) if val is not None else default
    except ValueError:
        return default


class Config:
    # ---- UI ----
    BASE_URL: str = os.getenv("BASE_URL", "https://book.anhtester.com")
    BROWSER: str = os.getenv("BROWSER", "chromium")
    HEADLESS: bool = _get_bool("HEADLESS", True)
    SLOW_MO: int = _get_int("SLOW_MO", 0)
    DEFAULT_TIMEOUT: int = _get_int("DEFAULT_TIMEOUT", 30000)
    VIEWPORT = {
        "width": _get_int("VIEWPORT_WIDTH", 1440),
        "height": _get_int("VIEWPORT_HEIGHT", 900),
    }

    # ---- API ----
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://book.anhtester.com")

    # ---- Tài khoản test ----
    LOGIN_EMAIL: str = os.getenv("LOGIN_EMAIL", "")
    LOGIN_PASSWORD: str = os.getenv("LOGIN_PASSWORD", "")

    # ---- Thực thi ----
    PARALLEL_WORKERS: int = _get_int("PARALLEL_WORKERS", 4)

    # ---- Log ----
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ---- Đường dẫn ----
    LOG_DIR = ROOT_DIR / "logs"
    SCREENSHOT_DIR = ROOT_DIR / "screenshots"
    TEST_DATA_DIR = ROOT_DIR / "test_data"
    ALLURE_RESULTS_DIR = ROOT_DIR / "allure-results"


config = Config()

# Đảm bảo các thư mục output luôn tồn tại
config.LOG_DIR.mkdir(parents=True, exist_ok=True)
config.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
config.ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
