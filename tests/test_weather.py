import os
import sys
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

# Add the parent directory to sys.path to import the weather module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import src.weather.weather as weather

# Sample test data
SAMPLE_GEOCODING_RESPONSE = [{"name": "Madrid", "lat": 40.4165, "lon": -3.7026, "country": "ES", "state": ""}]

SAMPLE_WEATHER_RESPONSE = {
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

SAMPLE_WEATHER_2_5_RESPONSE = {
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


# Test the get_coordinates function
@pytest.mark.asyncio
async def test_get_coordinates(sample_geocoding_response):
    # Mock the API response
    with patch("src.weather.weather.make_weather_request") as mock_request:
        mock_request.return_value = sample_geocoding_response

        # Test with city and country code
        result = await weather.get_coordinates("Madrid", "ES")

        # Verify the result
        assert result is not None
        lat, lon = result
        assert lat == 40.4165
        assert lon == -3.7026

        # Verify the API was called correctly
        mock_request.assert_called_with("https://api.openweathermap.org/geo/1.0/direct", {"q": "Madrid,ES", "limit": 5})


# Test the get_weather_by_coordinates function with One Call API 3.0
@pytest.mark.asyncio
async def test_get_weather_by_coordinates_3_0(sample_coordinates, sample_weather_response):
    # Mock the API response
    with patch("src.weather.weather.make_weather_request") as mock_request:
        mock_request.return_value = sample_weather_response

        # Test with coordinates
        lat, lon = sample_coordinates
        result = await weather.get_weather_by_coordinates(lat, lon, "celsius")

        # Verify the result contains expected data
        assert "Current Weather for" in result
        assert "Temperature:" in result
        assert "11.0°C" in result  # 284.15K - 273.15 = 11.0°C
        assert "Feels Like:" in result
        assert "broken clouds" in result.lower()

        # Verify the API was called correctly
        mock_request.assert_called_with(
            weather.OPENWEATHER_API_BASE, {"lat": lat, "lon": lon, "exclude": "minutely,hourly,daily,alerts"}
        )


# Test the get_weather_by_coordinates function with fallback to API 2.5
@pytest.mark.asyncio
async def test_get_weather_by_coordinates_fallback(sample_coordinates, sample_weather_2_5_response):
    # Mock the API responses - first call fails, second succeeds
    with patch("src.weather.weather.make_weather_request") as mock_request:
        mock_request.side_effect = [None, sample_weather_2_5_response]

        # Test with coordinates
        lat, lon = sample_coordinates
        result = await weather.get_weather_by_coordinates(lat, lon, "celsius")

        # Verify the result contains expected data
        assert "Current Weather for" in result
        assert "Temperature:" in result
        assert "11.0°C" in result  # 284.15K - 273.15 = 11.0°C
        assert "Feels Like:" in result
        assert "broken clouds" in result.lower()

        # Verify both APIs were called
        assert mock_request.call_count == 2
        mock_request.assert_any_call(
            weather.OPENWEATHER_API_BASE, {"lat": lat, "lon": lon, "exclude": "minutely,hourly,daily,alerts"}
        )
        mock_request.assert_any_call("https://api.openweathermap.org/data/2.5/weather", {"lat": lat, "lon": lon})


# Test the kelvin_to_unit function
def test_kelvin_to_unit():
    # Test conversion to Celsius
    celsius = weather.kelvin_to_unit(273.15, "celsius")
    assert celsius == 0.0

    # Test conversion to Fahrenheit
    fahrenheit = weather.kelvin_to_unit(273.15, "fahrenheit")
    assert fahrenheit == 32.0

    # Test default (Kelvin)
    kelvin = weather.kelvin_to_unit(273.15, "unknown")
    assert kelvin == 273.15


# Test the format_temperature function
def test_format_temperature():
    # Test Celsius formatting
    celsius = weather.format_temperature(25.123, "celsius")
    assert celsius == "25.1°C"

    # Test Fahrenheit formatting
    fahrenheit = weather.format_temperature(72.987, "fahrenheit")
    assert fahrenheit == "73.0°F"

    # Test default (Kelvin) formatting
    kelvin = weather.format_temperature(300.456, "unknown")
    assert kelvin == "300.5K"


# Test the get_current_weather function
@pytest.mark.asyncio
async def test_get_current_weather(sample_coordinates, sample_weather_response):
    # Mock the coordinates and API response
    with (
        patch("src.weather.weather.get_coordinates") as mock_coordinates,
        patch("src.weather.weather.make_weather_request") as mock_request,
    ):

        mock_coordinates.return_value = sample_coordinates
        mock_request.return_value = sample_weather_response

        # Test with city and country
        result = await weather.get_current_weather("Madrid", "ES")

        # Verify the result contains expected data
        assert "Current Weather for Madrid, ES" in result
        assert "Temperature:" in result
        assert "11.0°C" in result

        # Verify the API calls
        mock_coordinates.assert_called_with("Madrid", "ES", "")
        mock_request.assert_called_with(
            weather.OPENWEATHER_API_BASE,
            {"lat": sample_coordinates[0], "lon": sample_coordinates[1], "exclude": "minutely,hourly,daily,alerts"},
        )


# Test error handling when coordinates can't be found
@pytest.mark.asyncio
async def test_get_current_weather_no_coordinates():
    # Mock the coordinates function to return None
    with patch("src.weather.weather.get_coordinates") as mock_coordinates:
        mock_coordinates.return_value = None

        # Test with invalid city
        result = await weather.get_current_weather("NonExistentCity", "XX")

        # Verify the error message
        assert "Unable to find coordinates for NonExistentCity" in result


# Test the API key and subscription check
@pytest.mark.asyncio
async def test_check_api_key_and_subscription(sample_weather_response, sample_weather_2_5_response):
    # Create mock responses
    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = sample_weather_2_5_response

    mock_response2 = MagicMock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = sample_weather_response

    # Set up the mock to return different responses for different calls
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = [mock_response1, mock_response2]

        # Run the test
        result = await weather.check_api_key_and_subscription()

        # Verify the result
        assert "API key is valid and One Call API 3.0 subscription is active" in result


# Test the API key check with invalid key
@pytest.mark.asyncio
async def test_check_api_key_invalid():
    # Create mock response for invalid key
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Invalid API key"

    # Set up the mock
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = mock_response

        # Run the test
        result = await weather.check_api_key_and_subscription()

        # Verify the result
        assert "API key may be invalid" in result
