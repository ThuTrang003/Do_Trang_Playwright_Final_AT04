from playwright.sync_api import APIRequestContext

class BaseApi:
    def __init__(self, request: APIRequestContext):
        self.request = request