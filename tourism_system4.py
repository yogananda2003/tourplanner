import requests
import json
import time 

# IMPORTANT: Keep your User-Agent header here, as required by the Nominatim API.
NOMINATIM_HEADERS = {
    'User-Agent': 'TourismMultiAgentSystem/1.0 (byogananda6346@gmail.com)'
}

# ------------------------------------------------------------------------
# CORE INTENT DETECTION
# ------------------------------------------------------------------------

def detect_intent(user_input):
    """
    Simple function to detect the user's primary intent based on keywords.
    Returns: 'weather', 'places', 'coords', or 'full'.
    """
    input_lower = user_input.lower()
    
    # Check for specific coordinate request
    if 'coordinate' in input_lower or 'cordinate' in input_lower or 'lat' in input_lower or 'lon' in input_lower:
        return 'coords'
        
    # Check for weather/temperature keywords
    is_weather = any(keyword in input_lower for keyword in ['temp', 'weather', 'hot', 'cold', 'temperature'])
    
    # Check for places/attractions keywords
    is_places = any(keyword in input_lower for keyword in ['place', 'attraction', 'visit', 'go', 'trip', 'plan'])
    
    if is_weather and is_places:
        return 'full'
    elif is_weather:
        return 'weather'
    elif is_places:
        return 'places'
    
    # Default: if a place is mentioned but no specific intent, assume they want both
    return 'full'


# ------------------------------------------------------------------------
# CHILD AGENT 1: WEATHER AGENT (Open-Meteo API)
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# CHILD AGENT 1: WEATHER AGENT (Open-Meteo API)
# ------------------------------------------------------------------------

def get_weather_forecast(lat, lon):
    """
    Fetches the CURRENT temperature and the MAX precipitation probability for today.
    Returns a formatted string summary or None on failure.
    """
    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m',              # <--- CHANGED: Request current temp
        'daily': 'precipitation_probability_max', # Keep daily for rain chance
        'temperature_unit': 'celsius', 
        'timezone': 'auto',
        'forecast_days': 1 
    }
    
    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Get Current Temp
        current_temp = None
        if data.get('current') and 'temperature_2m' in data['current']:
            current_temp = round(data['current']['temperature_2m'])
            
        # Get Rain Chance (from daily forecast)
        rain_chance = 0
        if data.get('daily') and data['daily'].get('precipitation_probability_max'):
             rain_chance = data['daily']['precipitation_probability_max'][0]

        if current_temp is not None:
            # Updated string to be factually accurate
            summary = f"currently {current_temp}°C with a {rain_chance}% chance of rain today"
            return summary
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Weather API Error: {e}")
        return None
# ------------------------------------------------------------------------
# CHILD AGENT 2: PLACES AGENT (Overpass API)
# ------------------------------------------------------------------------

def get_attractions(lat, lon, radius=5000, limit=5):
    """
    Uses Overpass API to find tourist attractions within a given radius.
    Returns a list of up to 5 attraction names or an empty list on failure.
    """
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    
    query = f"""
    [out:json][timeout:25];
    (
      nwr[tourism=attraction](around:{radius},{lat},{lon});
      nwr[tourism=museum](around:{radius},{lat},{lon});
      nwr[tourism=gallery](around:{radius},{lat},{lon});
    );
    out {limit} center;
    """
    
    try:
        response = requests.post(OVERPASS_URL, data={'data': query}, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        attractions = []
        
        for element in data.get('elements', []):
            name = element.get('tags', {}).get('name')
            if name:
                attractions.append(name)
        
        return attractions[:limit]

    except requests.exceptions.RequestException:
        return []


# ------------------------------------------------------------------------
# PARENT AGENT: ORCHESTRATOR (Nominatim API)
# ------------------------------------------------------------------------

def get_coordinates(place_name):
    """
    Uses Nominatim API to get (latitude, longitude) for a given place name.
    """
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    
    params = {
        'q': place_name,
        'format': 'json',
        'limit': 1
    }
    
    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=NOMINATIM_HEADERS, timeout=5)
        response.raise_for_status() 
        data = response.json()
        
        if data:
            lat = data[0].get('lat')
            lon = data[0].get('lon')
            print(f"DEBUG: Found coordinates for {place_name}: ({lat}, {lon})")
            time.sleep(1) # Respect Nominatim rate limit
            return lat, lon
        else:
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Nominatim request failed: {e}")
        time.sleep(1) 
        return None, None

def run_tourism_system(user_input):
    """
    Parent Agent that detects intent, executes necessary child agents,
    and formats the output based on the user's request.
    """
    # 1. Intent Detection and Location Extraction 
    intent = detect_intent(user_input)
    
    input_lower = user_input.lower()
    place_name = ""
    
    # Extract the place name
    if 'to go to ' in input_lower:
        place_name = input_lower.split('to go to ')[-1].split(',')[0].split('?')[0].strip()
    elif ' for ' in input_lower:
        place_name = input_lower.split(' for ')[-1].split(',')[0].split('?')[0].strip()
    elif ' in ' in input_lower:
        place_name = input_lower.split(' in ')[-1].split(',')[0].split('?')[0].strip()
    else:
        place_name = user_input.strip()

    clean_place_name = place_name.title()
    
    print(f"\n--- Searching for: {clean_place_name} ---")
    print(f"--- Detected Intent: {intent} ---")

    # 2. Geocoding (Mandatory)
    lat, lon = get_coordinates(clean_place_name) 

    if lat is None or lon is None:
        return {
            "status": "Error",
            "message": f"🛑 I could not find the location '{clean_place_name}'. Please check the spelling."
        }

    # Special Intent: Coordinates only
    if intent == 'coords':
         return {
            "status": "Success",
            "message": f"The coordinates for {clean_place_name} are Latitude: {lat}, Longitude: {lon}."
        }

    # 3. Selective Agent Execution
    weather_summary = None
    attractions_list = []

    if intent in ['weather', 'full']:
        weather_summary = get_weather_forecast(lat, lon)
        
    if intent in ['places', 'full']:
        attractions_list = get_attractions(lat, lon)
        
    # 4. Compile Final Output
    output = ""
    has_weather = weather_summary is not None
    has_places = len(attractions_list) > 0
    
    if not has_weather and not has_places:
        return {
            "status": "Success",
            "message": f"In {clean_place_name}, I could not retrieve the requested information."
        }
        
    # --- FIXED FORMAT LOGIC ---

    # Step A: Add Weather if available
    if has_weather:
        output += f"In {clean_place_name} it's {weather_summary}."

    # Step B: Add Places if available
    if has_places:
        # If we already added weather, add a nice transition
        if has_weather:
            output += "\n\n**Also, here are the top places you can visit:**\n"
        else:
            # If no weather, start with the places header
            output += f"In {clean_place_name}, here are the top places to visit:\n"
            
        # Loop through the list (Now guaranteed to run if has_places is True)
        for attraction in attractions_list:
            output += f"- {attraction}\n"
    
    elif intent in ['places', 'full'] and not has_places:
        # If user wanted places but we found none
        output += "\n\n(No specific tourist attractions were found nearby)."

    return {
        "status": "Success",
        "message": output.strip() 
    }

# NOTE: The execution loop (if __name__ == "__main__":) has been intentionally 
# removed to make this file a clean module for the Flask application (app.py).