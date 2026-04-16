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
    """Retrieve a list of all countries with their cities. Use this as a starting point when the user wants to explore available countries or get a full list of countries and their associated cities."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_cities(country: str) -> dict:
    """Get all cities belonging to a specific country. Use this when the user wants to find cities within a particular country.

    Args:
        country: The name of the country to retrieve cities for (e.g. 'Nigeria', 'Canada').
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
    """Get all states or provinces within a specific country. Use this when the user needs administrative divisions (states, provinces, regions) of a country.

    Args:
        country: The name of the country to retrieve states for (e.g. 'United States', 'India').
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
    """Get all cities within a specific state of a country. Use this when the user wants to drill down from a country to a state and then see its cities.

    Args:
        country: The name of the country containing the state (e.g. 'United States').
        state: The name of the state within the country (e.g. 'California').
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
    """Retrieve the capital city of a specific country. Use this when the user asks for the capital of a country.

    Args:
        country: The name of the country whose capital is requested (e.g. 'France', 'Brazil').
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
    """Look up country information using a country code (ISO2 or ISO3). Use this when the user has a country code and wants to resolve it to full country details such as name, dial code, or currency.

    Args:
        code: The ISO2 (e.g. 'NG') or ISO3 (e.g. 'NGA') country code to look up.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/codes",
            params={"code": code}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_dial_codes(country: Optional[str] = None) -> dict:
    """Retrieve dial codes (phone country codes) for all countries or a specific country. Use this when the user needs international phone dialing codes.

    Args:
        country: Optional. The name of a specific country to get its dial code (e.g. 'Germany'). If omitted, dial codes for all countries are returned.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        if country:
            response = await client.post(
                f"{BASE_URL}/dialing-codes",
                json={"country": country}
            )
        else:
            response = await client.get(f"{BASE_URL}/dialing-codes")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_country_currency(country: Optional[str] = None) -> dict:
    """Retrieve currency information for all countries or a specific country. Use this when the user needs to know what currency a country uses, including the currency name and symbol.

    Args:
        country: Optional. The name of a specific country to get its currency (e.g. 'Japan'). If omitted, currency data for all countries is returned.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        if country:
            response = await client.post(
                f"{BASE_URL}/currency",
                json={"country": country}
            )
        else:
            response = await client.get(f"{BASE_URL}/currency")
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
