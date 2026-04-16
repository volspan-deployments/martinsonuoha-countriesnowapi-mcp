from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
import threading
from fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("CountriesNow API")

BASE_URL = "https://countriesnow.space/api/v0.1/countries"


@mcp.tool()
async def get_countries() -> dict:
    """Retrieve a list of all countries with their cities. Use this when the user wants a full list of countries, or wants to explore available country data in the API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_cities(country: str) -> dict:
    """Retrieve all cities for a specific country. Use this when the user wants to know what cities exist in a given country.

    Args:
        country: The name of the country to retrieve cities for (e.g., 'Nigeria', 'United States').
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/cities",
            json={"country": country}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_states(country: str) -> dict:
    """Retrieve all states or provinces for a specific country. Use this when the user needs administrative divisions (states, provinces, regions) of a country.

    Args:
        country: The name of the country to retrieve states/provinces for (e.g., 'Canada', 'India').
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/states",
            json={"country": country}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_state_cities(country: str, state: str) -> dict:
    """Retrieve all cities within a specific state of a country. Use this when the user wants cities filtered by both country and state/province.

    Args:
        country: The name of the country (e.g., 'United States').
        state: The name of the state or province within the country (e.g., 'California').
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/state/cities",
            json={"country": country, "state": state}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_capital(country: str) -> dict:
    """Retrieve the capital city of a specific country. Use this when the user asks about the capital of a country.

    Args:
        country: The name of the country to look up the capital for (e.g., 'France', 'Brazil').
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/capital",
            json={"country": country}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_by_code(code: str) -> dict:
    """Retrieve country details using an ISO country code (e.g., dial code or ISO alpha code). Use this when the user provides a country code and wants to find the matching country information.

    Args:
        code: The ISO country code or dial code to look up (e.g., 'NG', 'US', '+234').
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/codes",
            params={"code": code}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_countries_dial_codes() -> dict:
    """Retrieve a list of all countries along with their international dial codes. Use this when the user needs phone dial codes or wants to map countries to their calling codes."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/codes/all")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_currency(country: str) -> dict:
    """Retrieve the currency information (name, symbol, code) for a specific country. Use this when the user asks about the currency used in a particular country.

    Args:
        country: The name of the country to retrieve currency information for (e.g., 'Japan', 'Germany').
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/currency",
            json={"country": country}
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
