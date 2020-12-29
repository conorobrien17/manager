import logging
from django_rq import job
import requests
from requests.exceptions import HTTPError
from urllib import parse
from carbina.models import Address

MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
logger = logging.getLogger("file")

LATITUDE_INDEX = 0
LONGITUDE_INDEX = 1

@job('default', timeout=3600)
def forward_geocode_call(address):
    # See documentation for the call made here: https://docs.mapbox.com/api/search/geocoding/#forward-geocoding
    try:
        # TODO cleanup the way this gets called and store the image in the model to avoid API calls/more dns requests
        requestURL = address.street + " " + address.city + " " + address.state + " " + str(address.zip_code) + ".json"
        requestURL = parse.quote(requestURL)
        requestURL = MAPBOX_BASE_URL + requestURL + "?access_token=pk.eyJ1IjoiY29ub3JvYnJpZW4iLCJhIjoiY2tnbDVhOThhMTc4cDJybnM5dHU3bjlvOCJ9.rApCMl8Y1fh3Iom20QnYKw"
        response = requests.get(requestURL)
        json = response.json()
        coordinates = json.get("features")[0].get("center")

        log_str = "Coordinates received: " + str(coordinates)
        logger.debug(log_str)

        latitude = coordinates[LATITUDE_INDEX]
        longitude = coordinates[LONGITUDE_INDEX]

        address = Address.objects.get(pk=address.pk)
        if latitude and longitude:
            address.latitude = latitude
            address.longitude = longitude
            address.save()
        else:
            address.save()
    except HTTPError as error:
        logger.exception("Error receiving geocoding API response")