from django.shortcuts import render
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch API keys from environment variables
geocode_api_key = os.getenv('GEOCODE')
stormglass_api_key = os.getenv('APIKEY')

def index(request):
    context = {}  # Initialize context

    if request.method == 'POST':
        location = request.POST.get('location')
        
        # Geocoding URL and parameters
        geocode_url = 'https://api.opencagedata.com/geocode/v1/json'
        geocode_params = {
            'q': location,
            'key': geocode_api_key
        }
        
        # Make request to Geocoding API
        geocode_response = requests.get(geocode_url, params=geocode_params)
        geocode_data = geocode_response.json()

        if geocode_data['results']:
            # Get the latitude and longitude of the entered location
            latitude = geocode_data['results'][0]['geometry']['lat']
            longitude = geocode_data['results'][0]['geometry']['lng']
            
            # Storm Glass API URL and parameters
            stormglass_url = "https://api.stormglass.io/v2/weather/point"
            headers = {'Authorization': stormglass_api_key}
            params = {
                'lat': latitude,
                'lng': longitude,
                'params': 'airTemperature,windSpeed'
            }

            # Make request to Storm Glass API
            response = requests.get(stormglass_url, headers=headers, params=params)

            if response.status_code == 200:
                weather_data = response.json().get('hours', [{}])[0]  # Avoid KeyError
                temperature = weather_data.get('airTemperature', {}).get('sg')
                wind_speed = weather_data.get('windSpeed', {}).get('sg')
            else:
                temperature = None
                wind_speed = None
                context['error'] = 'Error fetching weather data.'

            context.update({
                'location': location,
                'latitude': latitude,
                'longitude': longitude,
                'temperature': temperature,
                'wind_speed': wind_speed,
            })
        else:
            context['error'] = 'Location not found. Please try again.'
    
    return render(request, 'index.html', context)
