## 1. Cài đặt

```bash
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
playwright install                # cài trình duyệt cho Playwright
```
File cấu hình: `.env`
```
BASE_URL=https://book.anhtester.com
API_BASE_URL=https://book.anhtester.com  
```

## 2. Cấu trúc project

```
book-automation/
├── .env                       # config (KHÔNG hard code, đọc qua os.getenv)
├── pytest.ini                 # markers, allure, testpaths
├── conftest.py                # fixtures: browser/page, home_page, api_client, auth_token,  screenshot khi fail
├── config/config.py           # đọc toàn bộ config từ .env
├── core/
│   ├── logger.py              # logging ra console + file logs/
│   └── api_client.py          # wrapper gọi API bằng Playwright APIRequestContext
├── api/endpoints.py           # khai báo tập trung path API thật (GET /api/me, PATCH /api/profile)
├── pages/                     # Page Object Model
│   ├── base_page.py
│   ├── login_page.py
│   ├── home_page.py           # Trang chủ + menu avatar 
│   ├── profile_page.py        # Change my profile
│   └── settings_page.py       # Setting account
├── test_data/                 # dữ liệu test JSON (data-driven)
├── utils/data_reader.py       # đọc JSON cho parametrize
└── tests/
    ├── ui/                    # nhóm UI 
    ├── api/                   # nhóm API
    └── combined/              # nhóm kết hợp UI + API 
```

## 3. Chạy test

Chạy toàn bộ:
```bash
pytest
```

Chạy riêng từng nhóm:
```bash
pytest -m ui
pytest -m api
pytest -m combined
```

### Chạy song song (Parallel Execution)
```bash
pytest -n 2          # 2 worker song song (dùng pytest-xdist)
# hoặc dùng số worker cấu hình trong .env
pytest -n auto
```

### Headed / debug (xem trình duyệt chạy)
Trong `.env` set `HEADLESS=false`, hoặc:
```bash
pytest --headed -m ui
```

## 4. Allure Report

Cài Allure commandline (1 lần):
```bash
npm install -g allure-commandline
```

Chạy test (kết quả tự sinh vào `allure-results/` nhờ cấu hình trong `pytest.ini`):
```bash
pytest
```

Xem report:
```bash
allure serve allure-results
```
hoặc build report tĩnh:
```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

Report sẽ có: log request/response API, screenshot khi FAIL, các bước (`allure.step`), feature/story theo từng nhóm chức năng.

## 5. Log
Mỗi lần chạy tạo 1 file log tại `logs/test_run_<timestamp>.log`, đồng thời in ra console (`log_cli = true` trong `pytest.ini`).