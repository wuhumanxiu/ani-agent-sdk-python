import httpx
import pytest

from ani_agent_sdk import AniClient


@pytest.mark.asyncio
async def test_ws_url_uses_wss_and_token():
    client = AniClient("https://agent-native.im", "aim_test")
    assert client.ws_url == "wss://agent-native.im/api/v1/ws?token=aim_test"


@pytest.mark.asyncio
async def test_get_me_parses_user():
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer aim_test"
        return httpx.Response(
            200,
            json={
                "ok": True,
                "data": {
                    "id": 9,
                    "public_id": "public-9",
                    "bot_id": "bot_huangyaoshi",
                    "display_name": "黄药师",
                    "entity_type": "bot",
                },
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http:
        client = AniClient("https://agent-native.im", "aim_test", client=http)
        me = await client.get_me()

    assert me.public_id == "public-9"
    assert me.bot_id == "bot_huangyaoshi"


@pytest.mark.asyncio
async def test_send_text_uses_public_mentions():
    seen = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        seen["json"] = request.read().decode()
        return httpx.Response(200, json={"ok": True, "data": {"id": 123}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http:
        client = AniClient("https://agent-native.im", "aim_test", client=http)
        result = await client.send_text(
            42,
            "@Alice hello",
            mention_public_ids=["alice-public"],
            reply_to=7,
        )

    assert result.id == 123
    assert '"mention_public_ids":["alice-public"]' in seen["json"].replace(" ", "")
    assert '"reply_to":7' in seen["json"].replace(" ", "")


@pytest.mark.asyncio
async def test_create_conversation_uses_public_ids():
    seen = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        seen["json"] = request.read().decode()
        return httpx.Response(200, json={"ok": True, "data": {"id": 77}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http:
        client = AniClient("https://agent-native.im", "aim_test", client=http)
        result = await client.create_conversation(
            title="Team",
            participant_public_ids=["alice-public"],
            source_public_id="bot-public",
        )

    assert result["id"] == 77
    compact = seen["json"].replace(" ", "")
    assert '"participant_public_ids":["alice-public"]' in compact
    assert '"source_public_id":"bot-public"' in compact


@pytest.mark.asyncio
async def test_batch_presence_uses_public_ids():
    async def handler(request: httpx.Request) -> httpx.Response:
        assert '"public_ids":["alice-public"]' in request.read().decode().replace(" ", "")
        return httpx.Response(
            200,
            json={"ok": True, "data": {"presence_by_public_id": {"alice-public": True}}},
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http:
        client = AniClient("https://agent-native.im", "aim_test", client=http)
        presence = await client.batch_presence(["alice-public"])

    assert presence == {"alice-public": True}
