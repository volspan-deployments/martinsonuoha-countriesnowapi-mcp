from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
import threading
from fastmcp import FastMCP
import httpx
import os
from typing import Optional

mcp = FastMCP("CountriesNow API")

BASE_URL = "https://countriesnow.space/api/v0.1/countries"


@mcp.tool()
async def get_countries() -> dict:
    """Retrieve a list of all countries with their cities. Use this when the user wants a full list of countries, or wants to explore available country data. Returns country names and associated cities."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_cities(country: str) -> dict:
    """Retrieve all cities for a specific country. Use this when the user wants to know what cities exist in a particular country.

    Args:
        country: The name of the country to fetch cities for, e.g. 'Nigeria', 'United States'
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/cities",
            json={"country": country},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_states(country: str) -> dict:
    """Retrieve all states or provinces for a specific country. Use this when the user needs administrative divisions (states, provinces, regions) of a country.

    Args:
        country: The name of the country to fetch states/provinces for, e.g. 'India', 'Australia'
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/states",
            json={"country": country},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_state_cities(country: str, state: str) -> dict:
    """Retrieve all cities within a specific state of a given country. Use this when the user wants cities scoped to a particular state or province.

    Args:
        country: The name of the country the state belongs to, e.g. 'United States'
        state: The name of the state or province to fetch cities for, e.g. 'California'
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/state/cities",
            json={"country": country, "state": state},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_capital(country: str) -> dict:
    """Retrieve the capital city of a specific country. Use this when the user asks for the capital of a country.

    Args:
        country: The name of the country whose capital is needed, e.g. 'France', 'Japan'
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/capital",
            json={"country": country},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_dial_codes(country: Optional[str] = None) -> dict:
    """Retrieve dial codes (phone country codes) for all countries or a specific country. Use this when the user needs international dialing codes or country phone prefixes.

    Args:
        country: Optional country name to filter results to a single country's dial code, e.g. 'Germany'. If omitted, returns all countries with dial codes.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        if country:
            response = await client.post(
                f"{BASE_URL}/codes",
                json={"country": country},
                headers={"Content-Type": "application/json"}
            )
        else:
            response = await client.get(f"{BASE_URL}/codes")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_currency(country: Optional[str] = None) -> dict:
    """Retrieve currency information for all countries or a specific country. Use this when the user wants to know what currency a country uses, including currency name and symbol.

    Args:
        country: Optional country name to get currency info for a specific country, e.g. 'Mexico'. If omitted, returns currency data for all countries.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        if country:
            response = await client.post(
                f"{BASE_URL}/currency",
                json={"country": country},
                headers={"Content-Type": "application/json"}
            )
        else:
            response = await client.get(f"{BASE_URL}/currency")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_flag(country: str) -> dict:
    """Retrieve the flag image URL or Unicode flag for a specific country. Use this when the user wants to display or reference a country's flag.

    Args:
        country: The name of the country whose flag is needed, e.g. 'Kenya', 'Sweden'
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/flag/images",
            json={"country": country},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()




_SERVER_SLUG = "martinsonuoha-countriesnowapi"

def _track(tool_name: str, ua: str = ""):
    try:
        import urllib.request, json as _json
        data = _json.dumps({"slug": _SERVER_SLUG, "event": "tool_call", "tool": tool_name, "user_agent": ua}).encode()
        req = urllib.request.Request("https://www.volspan.dev/api/analytics/event", data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass

async def health(request):
    return JSONResponse({"status": "ok", "server": mcp.name})

async def tools(request):
    registered = await mcp.list_tools()
    tool_list = [{"name": t.name, "description": t.description or ""} for t in registered]
    return JSONResponse({"tools": tool_list, "count": len(tool_list)})

sse_app = mcp.http_app(transport="sse")

app = Starlette(
    routes=[
        Route("/health", health),
        Route("/tools", tools),
        Mount("/", sse_app),
    ],
    lifespan=sse_app.lifespan,
)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
