"""Typed ANI data models used by adapter authors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AniUser:
    id: int | None = None
    public_id: str = ""
    bot_id: str = ""
    display_name: str = ""
    entity_type: str = ""

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "AniUser":
        return cls(
            id=data.get("id"),
            public_id=str(data.get("public_id") or ""),
            bot_id=str(data.get("bot_id") or ""),
            display_name=str(data.get("display_name") or data.get("name") or ""),
            entity_type=str(data.get("entity_type") or ""),
        )


@dataclass(slots=True)
class AniMessage:
    id: int | None = None
    conversation_id: int | str | None = None
    conversation_public_id: str = ""
    sender_public_id: str = ""
    summary: str = ""
    mentions: list[int] = field(default_factory=list)
    mention_public_ids: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_event(cls, data: dict[str, Any]) -> "AniMessage":
        layers = data.get("layers") or {}
        return cls(
            id=data.get("id"),
            conversation_id=data.get("conversation_id"),
            conversation_public_id=str(data.get("conversation_public_id") or ""),
            sender_public_id=str(data.get("sender_public_id") or ""),
            summary=str(layers.get("summary") or data.get("summary") or ""),
            mentions=list(data.get("mentions") or []),
            mention_public_ids=list(data.get("mention_public_ids") or []),
            raw=data,
        )


@dataclass(slots=True)
class SendMessageResult:
    id: int | None = None
    ok: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

