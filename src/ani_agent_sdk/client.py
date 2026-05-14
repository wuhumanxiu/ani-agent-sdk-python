"""Small ANI HTTP/WebSocket client.

This is intentionally conservative. It provides the stable primitives adapter
authors need first, while leaving runtime orchestration to Zebra/Hermes/etc.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import httpx

from .models import AniUser, SendMessageResult


class AniClient:
    """Authenticated ANI API client."""

    def __init__(
        self,
        server_url: str,
        api_key: str,
        *,
        timeout: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = client
        self._owns_client = client is None

    @property
    def api_base_url(self) -> str:
        return f"{self.server_url}/api/v1"

    @property
    def ws_url(self) -> str:
        ws_base = self.server_url.replace("https://", "wss://").replace("http://", "ws://")
        return f"{ws_base}/api/v1/ws?{urlencode({'token': self.api_key})}"

    async def __aenter__(self) -> "AniClient":
        await self._ensure_client()
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._client and self._owns_client:
            await self._client.aclose()
        self._client = None

    async def get_me(self) -> AniUser:
        data = await self._request("GET", "/me")
        return AniUser.from_api(data)

    async def send_text(
        self,
        conversation_id: int | str,
        text: str,
        *,
        conversation_public_id: str | None = None,
        mention_public_ids: list[str] | None = None,
        mention_refs: list[dict[str, Any]] | None = None,
        assigned_public_ids: list[str] | None = None,
        reply_to: int | str | None = None,
        content_type: str = "text",
    ) -> SendMessageResult:
        payload: dict[str, Any] = {
            "content_type": content_type,
            "layers": {"summary": text},
        }
        if conversation_public_id:
            payload["conversation_public_id"] = conversation_public_id
        elif isinstance(conversation_id, str) and not conversation_id.strip().isdigit():
            payload["conversation_public_id"] = conversation_id
        else:
            payload["conversation_id"] = conversation_id
        if mention_public_ids:
            payload["mention_public_ids"] = mention_public_ids
        if mention_refs:
            payload["mention_refs"] = mention_refs
        if assigned_public_ids is not None:
            payload["assigned_public_ids"] = assigned_public_ids
        if reply_to:
            payload["reply_to"] = int(reply_to)

        data = await self._request("POST", "/messages/send", json=payload)
        return SendMessageResult(
            id=data.get("id") or data.get("message_id"),
            ok=True,
            raw=data,
        )

    async def create_conversation(
        self,
        *,
        title: str = "",
        conv_type: str = "direct",
        participant_public_ids: list[str] | None = None,
        source_public_id: str | None = None,
        description: str = "",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "conv_type": conv_type,
            "participant_public_ids": participant_public_ids or [],
        }
        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if source_public_id:
            payload["source_public_id"] = source_public_id
        return await self._request("POST", "/conversations", json=payload)

    async def batch_presence(self, public_ids: list[str]) -> dict[str, bool]:
        data = await self._request("POST", "/presence/batch", json={"public_ids": public_ids})
        presence = data.get("presence_by_public_id") or {}
        return {str(key): bool(value) for key, value in presence.items()}

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
            self._owns_client = True
        return self._client

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        client = await self._ensure_client()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.api_key}"
        response = await client.request(
            method,
            f"{self.api_base_url}{path}",
            headers=headers,
            **kwargs,
        )
        response.raise_for_status()
        body = response.json()
        if isinstance(body, dict) and body.get("ok") is False:
            raise RuntimeError(body.get("error") or body)
        if isinstance(body, dict) and "data" in body:
            return body["data"] or {}
        return body if isinstance(body, dict) else {"value": body}
