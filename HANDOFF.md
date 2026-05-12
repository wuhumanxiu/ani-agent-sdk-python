# Handoff: ani-agent-sdk-python

Last updated: 2026-05-12

## Goal

Create the canonical Python SDK used by Python AI agent runtimes to connect to ANI. Zebra and Hermes should eventually depend on this package instead of copying ANI WebSocket, message-send, mention, file, reconnect, and presence logic.

## Related Projects

- ANI backend: `/Users/donaldford/code/SuperBody/dev/agent-native-im`
- ANI web: `/Users/donaldford/code/SuperBody/dev/agent-native-im-web`
- Existing Python SDK reference: `/Users/donaldford/code/SuperBody/dev/agent-native-im-sdk-python`
- Zebra runtime: `/Users/donaldford/code/SuperBody/dev/zebra-agent`
- Hermes runtime: `/Users/donaldford/code/SuperBody/dev/hermes-agent`
- Hermes ANI adapter: `/Users/donaldford/code/SuperBody/dev/hermes-ani-adapter`
- OpenClaw installer/extension: `/Users/donaldford/code/SuperBody/dev/openclaw-ani-installer`

## Production Environment

- Public app: `https://agent-native.im`
- API prefix: `https://agent-native.im/api/v1`
- WebSocket: `wss://agent-native.im/api/v1/ws`
- Production backend host used by operations: `ubuntu@192.168.14.123`
- Backend service name: `agent-im.service`
- Database: PostgreSQL database `agent_im`

Do not hard-code production credentials. Bot access packs provide `ANI_SERVER_URL`, `ANI_API_KEY`, `ANI_BOT_ID`, `ANI_PUBLIC_ID`, and `ANI_BOT_NAME`.

## Design Principles

- `public_id` is the external stable identity. Numeric entity IDs are legacy/internal compatibility.
- `mention_public_ids` is the preferred structured mention field for agent-generated messages.
- SDK code owns ANI protocol details. Runtime adapters should be thin.
- Sending to the current conversation is a side effect. Agent runtimes must not also auto-deliver the same final response.
- Reconnect and retry behavior must avoid infinite duplicate sends.

## Development Commands

```bash
cd /Users/donaldford/code/SuperBody/dev/ani-agent-sdk-python
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m py_compile src/ani_agent_sdk/*.py
```

## Protocol Sync

The SDK vendors the backend protocol contract under `protocol/`, including `routes.generated.json` generated from the backend router.

```bash
python scripts/fetch_protocol.py
pytest contract-tests
```

The canonical source is `/Users/donaldford/code/SuperBody/dev/agent-native-im/docs/protocol/`.
If those contract tests fail after refreshing, update SDK types/helpers before publishing.

## Suggested Next Tasks

1. Port proven primitives from `agent-native-im-sdk-python` into this cleaner package.
2. Add a real WebSocket receive loop with reconnect and backoff.
3. Add file upload/download helpers.
4. Add a conformance test suite that can be reused by Zebra/Hermes adapters.
5. Publish to PyPI only after Zebra and Hermes both pass conformance tests.
