"""
skills/weather_skill.py — Phase 7: Weather Skill
Fetches real-time weather using Open-Meteo (free, no API key required).
"""
import re
from typing import List
from skills.base_skill import BaseSkill


class WeatherSkill(BaseSkill):
    """Fetches real-time weather data using Open-Meteo API (no API key required)."""

    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "Fetches real-time weather and forecasts. No API key needed. Try: 'What's the weather?', 'weather in London'"

    @property
    def triggers(self) -> List[str]:
        return ["weather", "temperature", "forecast", "rain", "sunny", "humidity", "wind speed", "how hot", "how cold"]

    def execute(self, user_input: str, core=None) -> str:
        """Fetches weather. Tries to extract location from user input."""
        location = self._extract_location(user_input)
        return self._get_weather(location)

    def _extract_location(self, text: str) -> str:
        """Tries to extract a city/location from the user's message."""
        text_lower = text.lower()
        # Patterns: "weather in London", "weather at Paris", "weather for New York"
        patterns = [
            r'weather\s+(?:in|at|for|near)\s+([A-Za-z\s]+)',
            r'(?:in|at|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+weather',
            r'temperature\s+(?:in|at|for)\s+([A-Za-z\s]+)',
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip(" .,!?")
                if len(location) > 2:
                    return location
        return "auto"  # Use IP-based geolocation

    def _get_weather(self, location: str) -> str:
        """Fetches weather from Open-Meteo using geocoding."""
        try:
            import requests

            # Step 1: Geocode (get lat/lon)
            if location == "auto":
                # Use ip-api for approximate location
                try:
                    ip_resp = requests.get("http://ip-api.com/json/", timeout=5)
                    ip_data = ip_resp.json()
                    lat = ip_data.get("lat", 28.6139)
                    lon = ip_data.get("lon", 77.2090)
                    city_name = ip_data.get("city", "your location")
                except Exception:
                    lat, lon, city_name = 28.6139, 77.2090, "New Delhi"
            else:
                # Geocode the named location
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
                geo_resp = requests.get(geo_url, timeout=6)
                geo_data = geo_resp.json()
                results = geo_data.get("results", [])
                if not results:
                    return f"I couldn't find weather data for '{location}'. Try a different city name."
                lat = results[0]["latitude"]
                lon = results[0]["longitude"]
                city_name = results[0].get("name", location)
                country = results[0].get("country", "")
                city_name = f"{city_name}, {country}" if country else city_name

            # Step 2: Fetch weather
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation"
                f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
                f"&timezone=auto&forecast_days=3"
            )
            resp = requests.get(weather_url, timeout=8)
            data = resp.json()

            current = data.get("current", {})
            daily = data.get("daily", {})

            temp = current.get("temperature_2m", "N/A")
            feels_like = current.get("apparent_temperature", "N/A")
            humidity = current.get("relative_humidity_2m", "N/A")
            wind = current.get("wind_speed_10m", "N/A")
            precip = current.get("precipitation", 0)
            weather_code = current.get("weather_code", 0)
            condition = self._weather_code_to_text(weather_code)

            # Daily forecast
            forecast_lines = []
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            precip_sums = daily.get("precipitation_sum", [])
            daily_codes = daily.get("weather_code", [])
            for i in range(min(3, len(dates))):
                day_label = ["Today", "Tomorrow", "Day after"][i] if i < 3 else dates[i]
                cond = self._weather_code_to_text(daily_codes[i]) if i < len(daily_codes) else ""
                forecast_lines.append(
                    f"  • {day_label}: {cond} — {max_temps[i]:.0f}°C / {min_temps[i]:.0f}°C"
                    + (f" 🌧 {precip_sums[i]:.1f}mm rain" if precip_sums[i] > 0 else "")
                )

            forecast_str = "\n".join(forecast_lines)

            return (
                f"### 🌤 Weather for {city_name}\n"
                f"**Condition**: {condition}\n"
                f"**Temperature**: {temp}°C (feels like {feels_like}°C)\n"
                f"**Humidity**: {humidity}%  |  **Wind**: {wind} km/h\n"
                f"**Precipitation**: {precip} mm\n\n"
                f"**3-Day Forecast:**\n{forecast_str}"
            )

        except requests.exceptions.ConnectionError:
            return "Weather check failed: No internet connection."
        except Exception as e:
            return f"Weather fetch error: {e}"

    @staticmethod
    def _weather_code_to_text(code: int) -> str:
        """Converts WMO weather code to human-readable description."""
        codes = {
            0: "☀️ Clear sky", 1: "🌤 Mainly clear", 2: "⛅ Partly cloudy", 3: "☁️ Overcast",
            45: "🌫 Foggy", 48: "🌫 Icy fog", 51: "🌦 Light drizzle", 53: "🌦 Moderate drizzle",
            55: "🌧 Dense drizzle", 61: "🌧 Light rain", 63: "🌧 Moderate rain", 65: "🌧 Heavy rain",
            71: "🌨 Light snow", 73: "❄️ Moderate snow", 75: "❄️ Heavy snow", 80: "🌦 Rain showers",
            81: "🌧 Moderate showers", 82: "⛈ Heavy showers", 95: "⛈ Thunderstorm",
            96: "⛈ Thunderstorm with hail", 99: "⛈ Severe thunderstorm"
        }
        return codes.get(code, "🌡 Unknown conditions")
