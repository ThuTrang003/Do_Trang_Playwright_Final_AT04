import json
from typing import Any, Optional

import allure
from playwright.sync_api import APIRequestContext, APIResponse

from core.logger import get_logger

logger = get_logger("api_client")


class ApiClient:
    def __init__(self, request_context: APIRequestContext, base_url: str = ""):
        self._ctx = request_context
        self.base_url = base_url.rstrip("/")

    def _full_url(self, endpoint: str) -> str:
        if endpoint.startswith("http"):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _log_and_attach(self, method: str, url: str, payload: Optional[dict], response: APIResponse):
        try:
            body_preview = response.text()[:2000]
        except Exception:
            body_preview = "<binary or empty>"

        logger.info(f"{method} {url} | payload={payload} | status={response.status}")

        allure.attach(
            json.dumps(
                {
                    "method": method,
                    "url": url,
                    "request_payload": payload,
                    "status_code": response.status,
                    "response_body": _safe_json(body_preview),
                },
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            name=f"{method} {url}",
            attachment_type=allure.attachment_type.JSON,
        )

    def get(self, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> APIResponse:
        url = self._full_url(endpoint)
        response = self._ctx.get(url, params=params, headers=headers)
        self._log_and_attach("GET", url, params, response)
        return response

    def post(self, endpoint: str, data: Optional[dict] = None, headers: Optional[dict] = None) -> APIResponse:
        url = self._full_url(endpoint)
        response = self._ctx.post(url, data=data, headers=headers)
        self._log_and_attach("POST", url, data, response)
        return response

    def put(self, endpoint: str, data: Optional[dict] = None, headers: Optional[dict] = None) -> APIResponse:
        url = self._full_url(endpoint)
        response = self._ctx.put(url, data=data, headers=headers)
        self._log_and_attach("PUT", url, data, response)
        return response

    def patch(self, endpoint: str, data: Optional[dict] = None, headers: Optional[dict] = None) -> APIResponse:
        url = self._full_url(endpoint)
        response = self._ctx.patch(url, data=data, headers=headers)
        self._log_and_attach("PATCH", url, data, response)
        return response

    def delete(self, endpoint: str, headers: Optional[dict] = None) -> APIResponse:
        url = self._full_url(endpoint)
        response = self._ctx.delete(url, headers=headers)
        self._log_and_attach("DELETE", url, None, response)
        return response


def _safe_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return text
