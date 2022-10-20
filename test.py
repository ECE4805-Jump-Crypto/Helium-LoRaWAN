import h3

lat, lng = 37.769377, -122.388903
resolution = 9
print(h3.latlng_to_cell(lat, lng, resolution))