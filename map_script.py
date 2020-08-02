import numpy as np
import requests
import json
from map_class import InitialLocation, ProviderLocation
from math import radians, sin, asin, sqrt, atan2, cos

def calculate_manhattan_distance(initial_location: InitialLocation, provider_location: ProviderLocation):
  # convert decimal degrees to radians
  lat1, lon1, lat2, lon2 = map(radians,
                               [initial_location.latitude, initial_location.longitude, provider_location.latitude,
                                provider_location.longitude])
  i_hat = [1, 0]
  j_hat = [0, 1]
  a = np.array([[i_hat[0], j_hat[0]], [i_hat[1], j_hat[1]]])
  b = np.array([lon2 - lon1, lat2 - lat1])
  x = (np.linalg.solve(a, b)).tolist()
  mid_point = [i_hat[0] * x[0] + lon1, i_hat[1] * x[0] + lat1]
  return abs(haversine(lon1, lat1, mid_point[0], mid_point[1])) + abs(
    haversine(mid_point[0], mid_point[1], lon2, lat2))


def haversine(lon1, lat1, lon2, lat2):
  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
  c = 2 * asin(sqrt(a))
  r = 6371
  return c * r


# This is the main function
def generate_list_of_providers(param, data):
  data = [value for key, value in data.items()]
  if param['TestingAvailability'][0] == "True":
    data = [x for x in data if x['testing_availability'] == True]
  if param['BedAvailability'][0] == "True":
    data = [x for x in data if x['bed_availability'] == True]
  if param['VentilatorAvailability'][0] == "True":
    data = [x for x in data if x['ventilator_availability'] == True]
  initial_location = InitialLocation(float(param['latitude'][0]), float(param['longitude'][0]))
  provider_locations = []
  for index, value in enumerate(data):
    provider_locations.append(ProviderLocation(value['properties']['id'], value['geometry']['coordinates'][0], value['geometry']['coordinates'][1]))
  for provider in provider_locations:
    initial_location.provider_distance[provider.id] = calculate_manhattan_distance(initial_location, provider)
  final_provider_list = initial_location.find_ten_nearest_providers()
  final_providers = [x for x in data if x['properties']['id'] in final_provider_list[0]]
  assert len(final_providers) == 10
  for provider in final_providers:
    index = final_provider_list[0].index(provider['properties']['id'])
    provider['distance'] = final_provider_list[1][index]
  final_providers = sorted(final_providers, key=lambda x: x['distance'])
  print(final_providers)
  return final_providers


def download_geojson():
  data = requests.get(
    "https://gis-a.ie.ehealthafrica.org/geoserver/eHA_db/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=eHA_db:sv_health_facilities&outputFormat=application%2Fjson&authkey=fdfe9a37-d2d0-4210-9a15-25dab5d907fa")
  data_object = json.loads(data.text)
  facilities = data_object['features']
  booleans = [True, False]
  final_data = {}
  for facility in facilities:
    facility['testing_availability'] = bool(np.random.choice(booleans))
    facility['bed_availability'] = bool(np.random.choice(booleans))
    facility['ventilator_availability'] = bool(np.random.choice(booleans))
    final_data[facility['properties']['global_id']] = facility
  with open('nigeria_data.json', 'w') as f:
    json.dump(final_data, f, indent=2)
  return final_data

if __name__ == "__main__":
  data = download_geojson()
  generate_list_of_providers({'longitude': ['7.411333'], 'latitude': ['9.082453'], 'TestingAvailability': ['True'], 'BedAvailability': ['False'], 'VentilatorAvailability': ['True']}, data)
