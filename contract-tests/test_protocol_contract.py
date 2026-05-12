import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocol"


def test_protocol_manifest_required_paths_exist_in_openapi():
    manifest = json.loads((PROTOCOL / "manifest.json").read_text())
    openapi = (PROTOCOL / "openapi.yaml").read_text()
    route_contract = json.loads((PROTOCOL / "routes.generated.json").read_text())
    routes = {route["path"] for route in route_contract["routes"]}

    for path in manifest["requiredRestPaths"]:
        assert path in openapi
        assert path in routes


def test_send_fields_exist_in_protocol_contract():
    manifest = json.loads((PROTOCOL / "manifest.json").read_text())
    openapi = (PROTOCOL / "openapi.yaml").read_text()
    ws_schema = (PROTOCOL / "ws-events.schema.json").read_text()

    for field in manifest["requiredSendFields"]:
        assert field in openapi or field in ws_schema


def test_websocket_events_exist_in_schema():
    manifest = json.loads((PROTOCOL / "manifest.json").read_text())
    schema = json.loads((PROTOCOL / "ws-events.schema.json").read_text())
    events = set(schema["properties"]["type"]["enum"])

    for event in manifest["requiredWebSocketEvents"]:
        assert event in events
