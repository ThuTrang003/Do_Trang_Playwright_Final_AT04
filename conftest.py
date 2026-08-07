# conftest.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def playwright_instance():
    p = sync_playwright().start()
    yield p
    p.stop()

@pytest.fixture(scope="session")
def browser_instance(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=False)
    browser_context = browser.new_context(viewport={"width": 1920, "height": 1080})

    yield browser_context

    browser_context.close()
    browser.close()

@pytest.fixture(scope="function")
def page(browser_instance):
    page = browser_instance.new_page()
    yield page
    page.close()

@pytest.fixture(scope="session")
def api_context(playwright_instance):
    request_context = playwright_instance.request.new_context(
        base_url="https://book.anhtester.com",
        extra_http_headers={
            "Accept" : "application/json"
        }
    )
    yield request_context
    request_context.dispose()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):

    outcome = yield

    report = outcome.get_result()

    if report.when=="call" and report.failed:

        page=item.funcargs["page"]

        page.screenshot(
            path=f"Reports/{item.name}.png"
        )