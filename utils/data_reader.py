"""
Data-Driven Testing helper.
Toàn bộ dữ liệu test (trừ credential nhạy cảm nằm trong .env) được đọc từ
các file JSON trong thư mục test_data/, KHÔNG hard code trong file test.
"""
import json
from pathlib import Path
from typing import Any

from config.config import config


def load_json(file_name: str) -> Any:
    """
    file_name: tên file trong thư mục test_data/, vd: 'profile_data.json'
    """
    file_path: Path = config.TEST_DATA_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy test data: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_cases(file_name: str, key: str = "cases"):
    """Đọc danh sách test case dùng cho pytest.mark.parametrize."""
    data = load_json(file_name)
    return data[key] if isinstance(data, dict) else data
