from unittest.mock import MagicMock, patch

import pytest

from src.weather.weather import (
    check_api_key_and_subscription,
    format_alert,
    format_temperature,
    get_alerts,
    get_forecast,
    get_hourly_forecast,
    get_user_location,
    kelvin_to_unit,
    make_weather_request,
    test_api_connection,
)


@pytest.fixture
def mock_coordinates():
    return (40.4165, -3.7026)  # Madrid coordinates


@pytest.fixture
def mock_weather_data():
    return {
        "lat": 40.4165,
        "lon": -3.7026,
        "timezone": "Europe/Madrid",
        "timezone_offset": 7200,
        "current": {
            "dt": 1619352000,
            "sunrise": 1619324456,
            "sunset": 1619373563,
            "temp": 293.15,
            "feels_like": 292.15,
            "pressure": 1015,
            "humidity": 60,
            "dew_point": 285.15,
            "uvi": 6.7,
            "clouds": 20,
            "visibility": 10000,
            "wind_speed": 2.57,
            "wind_deg": 180,
            "weather": [{"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"}],
        },
        "daily": [
            {
                "dt": 1619352000,
                "sunrise": 1619324456,
                "sunset": 1619373563,
                "temp": {"day": 293.15, "min": 283.15, "max": 295.15, "night": 285.15, "eve": 290.15, "morn": 284.15},
                "feels_like": {"day": 292.15, "night": 284.15, "eve": 289.15, "morn": 283.15},
                "pressure": 1015,
                "humidity": 60,
                "dew_point": 285.15,
                "wind_speed": 2.57,
                "wind_deg": 180,
                "weather": [{"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"}],
                "clouds": 20,
                "pop": 0.2,
                "uvi": 6.7,
            }
        ],
        "hourly": [
            {
                "dt": 1619352000,
                "temp": 293.15,
                "feels_like": 292.15,
                "pressure": 1015,
                "humidity": 60,
                "dew_point": 285.15,
                "uvi": 6.7,
                "clouds": 20,
                "visibility": 10000,
                "wind_speed": 2.57,
                "wind_deg": 180,
                "wind_gust": 3.5,
                "weather": [{"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"}],
                "pop": 0.2,
            }
        ],
        "alerts": [
            {
                "sender_name": "Test Alert",
                "event": "Extreme Weather Warning",
                "start": 1619352000,
                "end": 1619438400,
                "description": "This is a test weather alert",
                "tags": ["Extreme"],
            }
        ],
    }


@pytest.fixture
def mock_ip_data():
    return {
        "ip": "8.8.8.8",
        "city": "Mountain View",
        "region": "California",
        "country": "US",
        "loc": "37.3860,-122.0838",
        "org": "AS15169 Google LLC",
        "postal": "94035",
        "timezone": "America/Los_Angeles",
    }


@pytest.mark.asyncio
async def test_format_alert():
    alert = {
        "sender_name": "Test Alert",
        "event": "Extreme Weather Warning",
        "start": 1619352000,
        "end": 1619438400,
        "description": "This is a test weather alert",
        "tags": ["Extreme"],
    }

    result = format_alert(alert)

    assert "Extreme Weather Warning" in result
    assert "This is a test weather alert" in result
    assert "Test Alert" in result


@pytest.mark.asyncio
async def test_kelvin_to_unit():
    # Test Celsius conversion
    celsius = kelvin_to_unit(273.15, "celsius")
    assert celsius == 0.0

    # Test Fahrenheit conversion
    fahrenheit = kelvin_to_unit(273.15, "fahrenheit")
    assert fahrenheit == 32.0

    # Test default (Kelvin)
    kelvin = kelvin_to_unit(273.15, "unknown")
    assert kelvin == 273.15


@pytest.mark.asyncio
async def test_format_temperature():
    # Test Celsius formatting
    celsius = format_temperature(25.123, "celsius")
    assert celsius == "25.1°C"

    # Test Fahrenheit formatting
    fahrenheit = format_temperature(98.6, "fahrenheit")
    assert fahrenheit == "98.6°F"

    # Test default (Kelvin) formatting
    kelvin = format_temperature(273.15, "unknown")
    assert kelvin == "273.1K"


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_forecast(mock_make_request, mock_get_coordinates, mock_coordinates, mock_weather_data):
    mock_get_coordinates.return_value = mock_coordinates
    mock_make_request.return_value = mock_weather_data

    result = await get_forecast("Madrid", "ES", days=1)

    assert "Weather Forecast for Madrid, ES" in result
    assert "Few clouds" in result  # Capitalized in the output
    mock_get_coordinates.assert_called_once_with("Madrid", "ES", "")
    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_forecast_no_coordinates(mock_make_request, mock_get_coordinates):
    mock_get_coordinates.return_value = None

    result = await get_forecast("InvalidCity", "XX")

    assert "Unable to find coordinates for InvalidCity, XX" in result
    mock_get_coordinates.assert_called_once_with("InvalidCity", "XX", "")
    mock_make_request.assert_not_called()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_forecast_no_data(mock_make_request, mock_get_coordinates, mock_coordinates):
    mock_get_coordinates.return_value = mock_coordinates
    mock_make_request.return_value = None

    result = await get_forecast("Madrid", "ES")

    assert "Could not retrieve forecast data for Madrid, ES" in result
    mock_get_coordinates.assert_called_once_with("Madrid", "ES", "")
    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_forecast_no_daily_data(mock_make_request, mock_get_coordinates, mock_coordinates):
    mock_get_coordinates.return_value = mock_coordinates
    mock_make_request.return_value = {"lat": 40.4165, "lon": -3.7026}  # No daily key

    result = await get_forecast("Madrid", "ES")

    assert "No forecast data available" in result
    mock_get_coordinates.assert_called_once_with("Madrid", "ES", "")
    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_hourly_forecast(mock_make_request, mock_get_coordinates, mock_coordinates, mock_weather_data):
    mock_get_coordinates.return_value = mock_coordinates
    mock_make_request.return_value = mock_weather_data

    result = await get_hourly_forecast("Madrid", "ES", hours=1)

    assert "Hourly Weather Forecast for Madrid, ES" in result
    assert "Few clouds" in result  # Capitalized in the output
    mock_get_coordinates.assert_called_once_with("Madrid", "ES", "")
    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_hourly_forecast_no_coordinates(mock_make_request, mock_get_coordinates):
    mock_get_coordinates.return_value = None

    result = await get_hourly_forecast("InvalidCity", "XX")

    assert "Unable to find coordinates for InvalidCity, XX" in result
    mock_get_coordinates.assert_called_once_with("InvalidCity", "XX", "")
    mock_make_request.assert_not_called()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_hourly_forecast_no_data(mock_make_request, mock_get_coordinates, mock_coordinates):
    mock_get_coordinates.return_value = mock_coordinates
    mock_make_request.return_value = None

    result = await get_hourly_forecast("Madrid", "ES")

    assert "Could not retrieve hourly forecast data for Madrid, ES" in result
    mock_get_coordinates.assert_called_once_with("Madrid", "ES", "")
    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_hourly_forecast_no_hourly_data(mock_make_request, mock_get_coordinates, mock_coordinates):
    mock_get_coordinates.return_value = mock_coordinates
    mock_make_request.return_value = {"lat": 40.4165, "lon": -3.7026}  # No hourly key

    result = await get_hourly_forecast("Madrid", "ES")

    assert "No hourly forecast data available" in result
    mock_get_coordinates.assert_called_once_with("Madrid", "ES", "")
    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_alerts(mock_make_request, mock_get_coordinates, mock_coordinates, mock_weather_data):
    mock_get_coordinates.return_value = mock_coordinates
    mock_make_request.return_value = mock_weather_data

    result = await get_alerts("Madrid", "ES")

    assert "Extreme Weather Warning" in result
    assert "This is a test weather alert" in result
    mock_get_coordinates.assert_called_once_with("Madrid", "ES", "")
    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_alerts_no_coordinates(mock_make_request, mock_get_coordinates):
    mock_get_coordinates.return_value = None

    result = await get_alerts("InvalidCity", "XX")

    assert "Unable to find coordinates for InvalidCity, XX" in result
    mock_get_coordinates.assert_called_once_with("InvalidCity", "XX", "")
    mock_make_request.assert_not_called()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_alerts_no_data(mock_make_request, mock_get_coordinates, mock_coordinates):
    mock_get_coordinates.return_value = mock_coordinates
    mock_make_request.return_value = None

    result = await get_alerts("Madrid", "ES")

    assert "Could not retrieve weather data for Madrid, ES" in result
    mock_get_coordinates.assert_called_once_with("Madrid", "ES", "")
    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.weather.weather.get_coordinates")
@patch("src.weather.weather.make_weather_request")
async def test_get_alerts_no_alerts(mock_make_request, mock_get_coordinates, mock_coordinates):
    mock_get_coordinates.return_value = mock_coordinates
    mock_make_request.return_value = {"lat": 40.4165, "lon": -3.7026}  # No alerts key

    result = await get_alerts("Madrid", "ES")

    assert "No active alerts for Madrid, ES" in result
    mock_get_coordinates.assert_called_once_with("Madrid", "ES", "")
    mock_make_request.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_get_user_location(mock_get, mock_ip_data):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_ip_data
    mock_get.return_value = mock_response

    result = await get_user_location()

    assert "Your location: Mountain View" in result
    assert "37.3860, -122.0838" in result
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_get_user_location_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    # Mock the json method to return a dict with get method
    mock_response.json.return_value = {}

    result = await get_user_location()

    assert "Your location:" in result
    assert "Coordinates unavailable" in result
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_get_user_location_exception(mock_get):
    mock_get.side_effect = Exception("Connection error")

    result = await get_user_location()

    assert "Could not determine your location due to an error" in result
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_get_user_location_no_loc(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Return data without loc field
    mock_response.json.return_value = {
        "ip": "8.8.8.8",
        "city": "Mountain View",
        "region": "California",
        "country": "US",
        "org": "AS15169 Google LLC",
        "postal": "94035",
        "timezone": "America/Los_Angeles",
    }
    mock_get.return_value = mock_response

    result = await get_user_location()

    assert "Your location: Mountain View, California, US" in result
    assert "Coordinates unavailable" in result
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_test_api_connection_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Add the 'current' key that the function expects
    mock_response.json.return_value = {"cod": 200, "current": {"temp": 293.15}}
    mock_get.return_value = mock_response

    result = await test_api_connection()

    assert "API test successful" in result
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_test_api_connection_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"cod": 401, "message": "Invalid API key"}
    mock_get.return_value = mock_response

    # Mock the text property
    mock_response.text = '{"cod": 401, "message": "Invalid API key"}'

    result = await test_api_connection()

    assert "API request failed with status code: 401" in result
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_test_api_connection_exception(mock_get):
    mock_get.side_effect = Exception("Connection error")

    result = await test_api_connection()

    assert "API connection test failed with error: Connection error" in result
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_check_api_key_and_subscription_success(mock_get):
    # Create two different response objects for the two API calls
    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = {"cod": 200, "list": [{"id": 123, "name": "London"}]}

    mock_response2 = MagicMock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = {"cod": 200, "current": {"temp": 293.15}}

    # Configure the mock to return different responses on consecutive calls
    mock_get.side_effect = [mock_response1, mock_response2]

    result = await check_api_key_and_subscription()

    assert "API key is valid" in result
    assert mock_get.call_count == 2  # Should be called twice


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_check_api_key_and_subscription_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"cod": 401, "message": "Invalid API key"}
    mock_get.return_value = mock_response

    # Mock the text property
    mock_response.text = '{"cod": 401, "message": "Invalid API key"}'

    result = await check_api_key_and_subscription()

    assert "API key may be invalid" in result
    assert mock_get.call_count >= 1


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_check_api_key_and_subscription_one_call_error(mock_get):
    # First response is successful
    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = {"cod": 200, "list": [{"id": 123, "name": "London"}]}

    # Second response is an error
    mock_response2 = MagicMock()
    mock_response2.status_code = 401
    mock_response2.json.return_value = {"cod": 401, "message": "Invalid API key"}
    mock_response2.text = '{"cod": 401, "message": "Invalid API key"}'

    # Configure the mock to return different responses on consecutive calls
    mock_get.side_effect = [mock_response1, mock_response2]

    result = await check_api_key_and_subscription()

    assert "API key is valid but One Call API 3.0 subscription is not active" in result
    assert mock_get.call_count == 2


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_check_api_key_and_subscription_quota_exceeded(mock_get):
    # First response is successful
    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = {"cod": 200, "list": [{"id": 123, "name": "London"}]}

    # Second response is a quota exceeded error
    mock_response2 = MagicMock()
    mock_response2.status_code = 429
    mock_response2.json.return_value = {"cod": 429, "message": "Quota exceeded"}

    # Configure the mock to return different responses on consecutive calls
    mock_get.side_effect = [mock_response1, mock_response2]

    result = await check_api_key_and_subscription()

    assert "API key is valid but you've exceeded your One Call API 3.0 quota" in result
    assert mock_get.call_count == 2


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_check_api_key_and_subscription_other_error(mock_get):
    # First response is successful
    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = {"cod": 200, "list": [{"id": 123, "name": "London"}]}

    # Second response is another error
    mock_response2 = MagicMock()
    mock_response2.status_code = 500
    mock_response2.json.return_value = {"cod": 500, "message": "Server error"}
    mock_response2.text = '{"cod": 500, "message": "Server error"}'

    # Configure the mock to return different responses on consecutive calls
    mock_get.side_effect = [mock_response1, mock_response2]

    result = await check_api_key_and_subscription()

    assert "One Call API 3.0 request failed with status code: 500" in result
    assert mock_get.call_count == 2


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_check_api_key_and_subscription_exception(mock_get):
    mock_get.side_effect = Exception("Connection error")

    result = await check_api_key_and_subscription()

    assert "Error testing One Call API 3.0: Connection error" in result
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_make_weather_request_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"cod": 200, "data": "test"}
    mock_get.return_value = mock_response

    result = await make_weather_request("https://test.com", {"param": "value"})

    assert result == {"cod": 200, "data": "test"}
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_make_weather_request_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"cod": 401, "message": "Invalid API key"}
    mock_get.return_value = mock_response

    # For error cases, the function returns the error response, not None
    result = await make_weather_request("https://test.com", {"param": "value"})

    assert result == {"cod": 401, "message": "Invalid API key"}
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_make_weather_request_exception(mock_get):
    mock_get.side_effect = Exception("Connection error")

    result = await make_weather_request("https://test.com", {"param": "value"})

    assert result is None
    mock_get.assert_called_once()
    mock_get.assert_called_once()
