from django.utils import timezone

from locations.services import LocationService

from .darksky_api_manager import DarkSkyApiManager
from .models import WeatherForecast
from .models import DailyWeatherForecast

class WeatherService:

    class NoForecast(RuntimeError):
        pass

    WEATHER_OUTDOOR = "outdoor"  # weather is good enough to go outside
    WEATHER_OUTDOOR_SNOW = "outdoor_snow"  # it is currently snowing, and not suitable to go outside
    WEATHER_INDOOR = "indoor"  # weather is unfit to go outside and one should stay indoors

    def __init__(self, user=None):
        self.__user = user
        self._client = DarkSkyApiManager(user = user)

    def make_forecast(latitude, longitude, time=None):
        if not time:
            time = timezone.now()

        dark_sky = DarkSkyApiManager()
        forecast = dark_sky.get_forecast(latitude, longitude, time)
        return WeatherForecast.objects.create(**forecast)

    def get_context(temperature, precipitation_probability, precipitation_type):
        if precipitation_probability > 0.0 and precipitation_type == WeatherForecast.SNOW and temperature > 25.0:
            return WeatherService.WEATHER_OUTDOOR_SNOW
        elif precipitation_probability < 70.0 and temperature > 32.0 and temperature < 90.0:
            return WeatherService.WEATHER_OUTDOOR
        else:
            return WeatherService.WEATHER_INDOOR

    def get_forecast_context(weather_forecast):
        return WeatherService.get_context(
            temperature = weather_forecast.apparent_temperature,
            precipitation_probability = weather_forecast.precip_probability,
            precipitation_type = weather_forecast.precip_type
        )

    def get_average_forecast_context(forecasts):
        """
        From a list of weather forecasts, make an average and return it's context
        """
        if not forecasts:
            raise WeatherService.NoForecast('No forecast')

        average_temperature = sum([forecast.apparent_temperature for forecast in forecasts])/len(forecasts)
        average_precipitation_probability = sum([forecast.precip_probability for forecast in forecasts])/len(forecasts)

        if WeatherForecast.SNOW in [forecast.precip_type for forecast in forecasts]:
            worst_precipitation_type = WeatherForecast.SNOW
        else:
            worst_precipitation_type = forecasts[0].precip_type

        return WeatherService.get_context(
            temperature = average_temperature,
            precipitation_probability = average_precipitation_probability,
            precipitation_type = worst_precipitation_type
        )

    def update_daily_forecast(self, date):
        location_service = LocationService(user=self.__user)
        location = location_service.get_location_on(date)
        
        forecast = self._client.get_daily_forecast(
            date = date,
            latitude = location.latitude,
            longitude = location.longitude
        )

        daily_forecast, created = DailyWeatherForecast.objects.update_or_create(
            user = self.__user,
            date = date,
            defaults = {
                'category': forecast['category'],
                'high': forecast['high'],
                'low': forecast['low']
            }
        )
        return daily_forecast

    def update_weekly_forecast(self):
        location_service = LocationService(user=self.__user)
        recent_location = location_service.get_last_location()

        forecasts = []
        for forecast in self._client.get_weekly_forecast(latitude = recent_location.latitude, longitude = recent_location.longitude):
            daily_forecast, created = DailyWeatherForecast.objects.update_or_create(
                user = self.__user,
                date = forecast['date'],
                defaults = {
                    'category': forecast['category'],
                    'high': forecast['high'],
                    'low': forecast['low']
                }
            )
            forecasts.append(daily_forecast)
        return forecasts

