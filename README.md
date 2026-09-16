# hass-agent-gosling

Home Assistant custom integration that connects the [Agent Gosling add-on](https://github.com/Nemens1s/homeassistant-agent) to the HA Assist voice pipeline. Once installed, Agent Gosling appears as a conversation agent you can select in your voice assistant settings.

## Installation

### HACS (recommended)

1. HACS → Custom repositories → add `https://github.com/Nemens1s/hass-agent-gosling` → category: Integration → Install, then restart HA.
2. Settings → Devices & Services → Add Integration → **Agent Gosling**.
3. Set the App base URL (default `http://agent-gosling:8099` — the add-on's internal address on the same host).
4. Settings → Voice assistants → select **Agent Gosling** as the conversation agent.

### Manual

Copy `custom_components/agent_gosling/` into your HA `config/custom_components/` directory and restart.

## Prerequisites

The Agent Gosling add-on must be running and reachable from HA at the configured URL. The integration talks to the add-on's `/api/chat` endpoint over plain HTTP — no separate API key required.

**Security note:** the component→add-on hop is unauthenticated and assumes both sit in the same LAN trust domain. If the add-on port is ever exposed beyond the host, put an API token in front of it first.

**Assist wants a fast model:** the integration uses a 90 s HTTP timeout. Assist pipelines favour fast responses — a slow answer stalls the whole voice turn. Long-running questions belong in the chat UI, not Assist.

## Configuration

| Field | Default | Description |
|---|---|---|
| `base_url` | `http://agent-gosling:8099` | URL of the Agent Gosling add-on API |

## Development

```bash
uv sync           # installs dev deps (pytest, pytest-asyncio, aiohttp)
uv run pytest -q  # runs unit tests (no HA harness needed)
```

Tests that exercise the HA conversation API surface require the full harness:

```bash
uv sync --group ha
uv run pytest -q  # skips HA tests automatically if homeassistant is not installed
```
