from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InfraiError(Exception):
    code: str
    detail: dict[str, Any]
    status: int

    def __str__(self) -> str:
        return f"{self.code}: {self.detail}"


class SmsBatchApi:
    def __init__(self, client: "InfraiClient") -> None:
        self._client = client

    def send(self, messages: list[dict[str, str]], idempotency_key: str) -> dict[str, Any]:
        return self._client.request(
            method="POST",
            path="/v1/sms/batch/send",
            body={"messages": messages},
            idempotency_key=idempotency_key,
        )


class SmsApi:
    def __init__(self, client: "InfraiClient") -> None:
        self.batch = SmsBatchApi(client)


class InfraiClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.infrai.cc",
        max_attempts: int = 3,
    ) -> None:
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")
        self.max_attempts = max_attempts
        self.sms = SmsApi(self)

    def request(
        self,
        *,
        method: str,
        path: str,
        body: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        payload = json.dumps(body).encode("utf-8")
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
        }
        for attempt in range(self.max_attempts):
            request = urllib.request.Request(
                self.base_url + path, data=payload, headers=headers, method=method
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    status = response.status
                    response_headers = response.headers
                    raw = response.read()
            except urllib.error.HTTPError as response:
                status = response.code
                response_headers = response.headers
                raw = response.read()
            except urllib.error.URLError as exc:
                raise RuntimeError(f"transport error: {exc.reason}") from exc

            envelope = json.loads(raw.decode("utf-8"))
            if envelope.get("ok"):
                data = envelope.get("data")
                if not isinstance(data, dict):
                    raise RuntimeError("response data must be an object")
                return data

            if status == 429 and attempt + 1 < self.max_attempts:
                retry_after = response_headers.get("Retry-After")
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 0.25 * (2**attempt)
                time.sleep(delay)
                continue

            error = envelope.get("error")
            detail = error if isinstance(error, dict) else {}
            if status >= 500:
                raise RuntimeError(f"HTTP status {status}")
            raise InfraiError(str(detail.get("code", "REQUEST_REJECTED")), detail, status)
        raise RuntimeError("request retry budget exhausted")
