import pytest
from Pages.login_page import LoginPage
from Pages.profile_page import ProfilePage
from Utils.path_helper import PathFile


@pytest.fixture(scope ="session")
def get_credential():
    credential = PathFile.read_json_data("Testdata/config.json")
    yield credential

@pytest.fixture(scope="function")
def login(page):
    return LoginPage(page)

@pytest.fixture
def logged_in_home(login, get_credential):
    login.login(
        get_credential["URL"],
        get_credential["EMAIL"],
        get_credential["PASSWORD"]
    )
    yield login

@pytest.fixture
def logged_in_profile_manage(page, login, get_credential):
    login.login(
        get_credential["URL"],
        get_credential["USERNAME"],
        get_credential["PASSWORD"]
    )
    profile_manage = ProfilePage(page)

    yield profile_manage
