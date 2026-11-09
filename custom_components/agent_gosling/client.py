"""HTTP client for the App API. Kept free of Home Assistant imports so it
is unit-testable without the HA harness."""

from __future__ import annotations

import asyncio

import aiohttp


class AgentApiError(Exception):
    """App unreachable or returned an error."""


class AgentApiClient:
    def __init__(self, base_url: str, session: aiohttp.ClientSession, timeout: float = 90.0):
        self._base_url = base_url.rstrip("/")
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def chat(
        self, text: str, conversation_id: str, context: dict | None = None
    ) -> str:
        """Send one Assist turn. ``context`` holds the raw HA ids (device,
        satellite, user) the App resolves to an area and a speaker; ids HA
        left unset are not sent."""
        body = {"message": text, "thread_id": conversation_id, "channel": "assist"}
        sent_context = {}
        for key, value in (context or {}).items():
            if value is not None:
                sent_context[key] = value
        if sent_context:
            body["context"] = sent_context
        try:
            async with self._session.post(
                f"{self._base_url}/api/chat",
                json=body,
                timeout=self._timeout,
            ) as resp:
                if resp.status != 200:
                    raise AgentApiError(f"App returned HTTP {resp.status}")
                data = await resp.json()
                return data["reply"]
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise AgentApiError(f"App unreachable: {exc}") from exc
