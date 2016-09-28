import urllib2
import json

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

		geo_data[siteCode] = {
			"name": sourceInfo["siteName"].replace (" ", "_"),
			"lat": sourceGeoInfo["latitude"],
			"lon": sourceGeoInfo["longitude"],
			"label": 1
		}

	return geo_data