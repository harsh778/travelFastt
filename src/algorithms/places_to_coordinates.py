from geopy.geocoders import Nominatim

# Initialize Nominatim API
geolocator = Nominatim(user_agent="MyApp")

def return_coords(places): #takes in a list of places and returns a list of their coordinates
    to_return = []
    for place in places:
      try:
        location = geolocator.geocode(place)
        to_return.append([location.latitude, location.longitude])
      except:
        print("That isn't a valid place")
    return to_return

