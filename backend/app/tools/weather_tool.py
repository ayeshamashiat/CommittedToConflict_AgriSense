"""Owned by Member B: wraps the weather API behind the AgriTool interface.

Uses Open-Meteo (no API key required): geocode the location to lat/lon, then
pull current conditions + a 7-day forecast.
"""

import httpx

from app.config import get_settings
from app.schemas.tool_io import ForecastDay, WeatherInput, WeatherOutput
from app.tools.base import AgriTool

settings = get_settings()


class WeatherToolError(RuntimeError):
    pass


class WeatherTool(AgriTool):
    name = "weather"
    description = (
        "Fetches current temperature, rainfall, humidity, and a 7-day forecast "
        "for a given location. Call this before recommending crops so the "
        "recommendation can be grounded in real conditions."
    )
    input_schema = WeatherInput
    output_schema = WeatherOutput

    def __init__(self, client: httpx.Client | None = None):
        self._client = client

    def _http(self) -> httpx.Client:
        return self._client or httpx.Client(timeout=10.0)

    def _geocode(self, client: httpx.Client, location: str) -> tuple[float, float, str]:
        resp = client.get(
            settings.weather_geocoding_url,
            params={"name": location, "count": 1, "language": "en", "format": "json"},
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results") or []
        if not results:
            raise WeatherToolError(f"Could not geocode location: {location!r}")
        top = results[0]
        name = ", ".join(
            part for part in [top.get("name"), top.get("admin1"), top.get("country")] if part
        )
        return top["latitude"], top["longitude"], name or location

    def run(self, input_data: WeatherInput) -> WeatherOutput:
        client = self._http()
        try:
            lat, lon, resolved_name = self._geocode(client, input_data.location)

            resp = client.get(
                settings.weather_api_base_url,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,precipitation",
                    # relative_humidity_2m_mean lets the pest/disease risk tool
                    # evaluate humidity-based triggers (e.g. blast, blight) for
                    # future growth-stage days, not just today's snapshot.
                    "daily": (
                        "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                        "relative_humidity_2m_mean"
                    ),
                    "forecast_days": 7,
                    "timezone": "auto",
                },
            )
            resp.raise_for_status()
            data = resp.json()

            current = data.get("current", {})
            daily = data.get("daily", {})
            dates = daily.get("time", [])
            temp_max = daily.get("temperature_2m_max", [])
            temp_min = daily.get("temperature_2m_min", [])
            precip = daily.get("precipitation_sum", [])
            humidity_mean = daily.get("relative_humidity_2m_mean", [])

            forecast = [
                ForecastDay(
                    date=dates[i],
                    temperature_max=temp_max[i],
                    temperature_min=temp_min[i],
                    precipitation_mm=precip[i],
                    humidity_mean=humidity_mean[i] if i < len(humidity_mean) else None,
                )
                for i in range(len(dates))
            ]

            return WeatherOutput(
                location=resolved_name,
                latitude=lat,
                longitude=lon,
                temperature=current.get("temperature_2m", 0.0),
                rainfall=current.get("precipitation", 0.0),
                humidity=current.get("relative_humidity_2m", 0.0),
                forecast=forecast,
            )
        finally:
            if self._client is None:
                client.close()
