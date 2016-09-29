import urllib2
import json

access_token = "pk.eyJ1IjoiZ2FuZXNocmF2aWNoYW5kcmFuIiwiYSI6ImNpczUxMTBqNTBhNDUyb2xrcGwzdGQ5YzcifQ.QoSUWMk-EZJoPTn-K8OreA"

def get_water_sources(state_cd="NY", number_of_hits = 10):

	# {siteCode: name, lat, lon, label}
	geo_data = {}

	# USGS REST API
	url = "http://waterservices.usgs.gov/nwis/iv/?format=json&stateCd=%s" %(state_cd)
	res = urllib2.urlopen(url)

	# list of water sources
	data = json.loads(res.read())["value"]["timeSeries"][:number_of_hits]

	# iterate for number_of_hits
	for source in data:
		sourceInfo = source["sourceInfo"]
		siteCode = sourceInfo["siteCode"][0]["value"]
		sourceGeoInfo = sourceInfo["geoLocation"]["geogLocation"]

		name = sourceInfo["siteName"].replace (" ", "_")
		lon = sourceGeoInfo["longitude"]
		lat = sourceGeoInfo["latitude"]

		geo_data[siteCode] = {
			"name": name,
			"lon": lon,
			"lat": lat,
			"image_url": get_image_url_from_Mapbox(lon, lat)
		}

	return geo_data

def get_image_url_from_Mapbox(lon, lat, zoom=17):
	url = "https://api.mapbox.com/v4/mapbox.satellite/%s,%s,%s/1000x1000.png32?access_token=%s" % (lon, lat, zoom, access_token)
	return url