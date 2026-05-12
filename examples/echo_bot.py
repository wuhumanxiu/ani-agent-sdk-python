"""Minimal placeholder echo bot.

The receive loop will be expanded after the SDK absorbs the proven
Zebra/Hermes adapter WebSocket implementation.
"""

import asyncio
import os

from ani_agent_sdk import AniClient


async def main() -> None:
    client = AniClient(
        server_url=os.environ.get("ANI_SERVER_URL", "https://agent-native.im"),
        api_key=os.environ["ANI_API_KEY"],
    )
    me = await client.get_me()
    print(f"Connected as {me.display_name} ({me.public_id})")


if __name__ == "__main__":
    asyncio.run(main())

