from __future__ import annotations

import os

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_BASE_URL, DOMAIN

_SUPERVISOR_ADDONS = "http://supervisor/addons"


async def _discover_addon_url(hass) -> str | None:
    """Query the Supervisor addon list and derive the Agent Gosling URL.

    Works in HA OS / Supervised installs. Returns None in any other case so
    the caller can fall back to manual entry.
    """
    token = os.environ.get("SUPERVISOR_TOKEN")
    if not token:
        return None
    try:
        session = async_get_clientsession(hass)
        async with session.get(
            _SUPERVISOR_ADDONS,
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=5),
        ) as resp:
            if resp.status != 200:
                return None
            payload = await resp.json()
            for addon in payload.get("data", {}).get("addons", []):
                slug: str = addon.get("slug", "")
                if slug.endswith("_agent_gosling") or slug == "agent_gosling":
                    hostname = slug.replace("_", "-")
                    return f"http://{hostname}:8099"
    except Exception:
        return None
    return None


class LocalHaAgentConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="Agent Gosling", data=user_input)
        discovered = await _discover_addon_url(self.hass)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_BASE_URL, default=discovered or ""): str}
            ),
            description_placeholders={"discovered": discovered or ""},
        )

    async def async_step_reconfigure(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=user_input,
            )
        current_url = self._get_reconfigure_entry().data.get(CONF_BASE_URL, "")
        discovered = await _discover_addon_url(self.hass)
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {vol.Required(CONF_BASE_URL, default=current_url or discovered or ""): str}
            ),
            description_placeholders={"discovered": discovered or ""},
        )