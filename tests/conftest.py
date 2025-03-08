import os
import sys

import pytest

# Add the parent directory to sys.path to import the weather module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# This enables the pytest-asyncio plugin for all tests
pytest_plugins = ["pytest_asyncio"]


# Define fixtures that can be used across tests
@pytest.fixture
def sample_coordinates():
    """Return sample coordinates for Madrid, Spain."""
    return 40.4165, -3.7026


@pytest.fixture
def sample_geocoding_response():
    """Return a sample geocoding API response."""
    return [{"name": "Madrid", "lat": 40.4165, "lon": -3.7026, "country": "ES", "state": ""}]


@pytest.fixture
def sample_weather_response():
    """Return a sample One Call API 3.0 response."""
    return {
        "lat": 40.4165,
        "lon": -3.7026,
        "timezone": "Europe/Madrid",
        "timezone_offset": 7200,
        "current": {
            "dt": 1618317040,
            "sunrise": 1618282134,
            "sunset": 1618333901,
            "temp": 284.15,  # 11°C
            "feels_like": 282.75,
            "pressure": 1010,
            "humidity": 56,
            "dew_point": 275.45,
            "uvi": 1.93,
            "clouds": 75,
            "visibility": 10000,
            "wind_speed": 2.5,
            "wind_deg": 262,
            "weather": [{"id": 803, "main": "Clouds", "description": "broken clouds", "icon": "04d"}],
        },
    }


@pytest.fixture
def sample_weather_2_5_response():
    """Return a sample Weather API 2.5 response."""
    return {
        "coord": {"lon": -3.7026, "lat": 40.4165},
        "weather": [{"id": 803, "main": "Clouds", "description": "broken clouds", "icon": "04d"}],
        "base": "stations",
        "main": {
            "temp": 284.15,  # 11°C
            "feels_like": 282.75,
            "temp_min": 282.59,
            "temp_max": 285.37,
            "pressure": 1010,
            "humidity": 56,
        },
        "visibility": 10000,
        "wind": {"speed": 2.5, "deg": 262},
        "clouds": {"all": 75},
        "dt": 1618317040,
        "sys": {"type": 1, "id": 6443, "country": "ES", "sunrise": 1618282134, "sunset": 1618333901},
        "timezone": 7200,
        "id": 3117735,
        "name": "Madrid",
        "cod": 200,
    }
