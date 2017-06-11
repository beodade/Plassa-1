import json
from math import radians, cos, sin, asin, sqrt

def read_file(path):
	with open(path,'r') as json_data:
		d = json.load(json_data)
	return (d)
def save_file(data,path):
	with open(path,'w') as outfile:
		json.dump(data, outfile)
def clean_osm_file(path):
	data=open_json_file(path)
	try:
		d=data["geometries"][0]["coordinates"][0][0]
	except:
		return None
	f_data=[]
	for i in range(len(d)):
		f_data.append([d[i][1],d[i][0]])
	_save(f_data,path)
	return None
def haversine(lon1, lat1, lon2, lat2):
	"""
	Calculate the great circle distance between two points 
	on the earth (specified in decimal degrees) in meters
	"""
	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

	# haversine formula
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	r = 6371000 # Radius of earth in meters. Use 3956 for miles
	return c*r
fields='?fields=is_community_page,category,category_list,fan_count,hours,link,location,name,name_with_location_descriptor,overall_star_rating,parking,phone,rating_count,single_line_address,store_location_descriptor,website,were_here_count'
isLatin = lambda s: len(s) == len(s.encode())
