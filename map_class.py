class InitialLocation:

  def __init__(self, lat, long):
    self.latitude = lat
    self.longitude = long
    self.provider_distance = dict()

  def find_ten_nearest_providers(self):
    self.provider_distance = {k: v for k, v in sorted(self.provider_distance.items(), key=lambda item: item[1])}
    return list(self.provider_distance.keys())[:10], list(self.provider_distance.values())[:10]


class ProviderLocation:
  def __init__(self, id, lat, long):
    self.latitude = lat
    self.longitude = long
    self.id = id
