import logging
from django_rq import job
from django.core import files
import requests
from tempfile import NamedTemporaryFile
from requests.exceptions import HTTPError
from urllib import parse
from carbina.models import Address

MAPBOX_KEY = 'pk.eyJ1IjoiY29ub3JvYnJpZW4iLCJhIjoiY2tnbDVhOThhMTc4cDJybnM5dHU3bjlvOCJ9.rApCMl8Y1fh3Iom20QnYKw'
MAPBOX_GEOCODE_URL = 'https://api.mapbox.com/geocoding/v5/mapbox.places/'
MAPBOX_SMAP_URL = 'https://api.mapbox.com/styles/v1/mapbox/dark-v10/static/'
logger = logging.getLogger('file')

LATITUDE_INDEX = 0
LONGITUDE_INDEX = 1


@job('default', timeout=3600)
def forward_geocode_call(address):
    # See documentation for the call made here: https://docs.mapbox.com/api/search/geocoding/#forward-geocoding
    try:
        # TODO cleanup the way this gets called and store the image in the model to avoid API calls/more dns requests
        requestURL = address.street + " " + address.city + " " + address.state + " " + str(address.zip_code) + ".json"
        requestURL = parse.quote(requestURL)
        requestURL = MAPBOX_GEOCODE_URL + requestURL + "?access_token=pk.eyJ1IjoiY29ub3JvYnJpZW4iLCJhIjoiY2tnbDVhOThhMTc4cDJybnM5dHU3bjlvOCJ9.rApCMl8Y1fh3Iom20QnYKw"
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


@job('default', timeout=3600)
def get_static_map_image(address):
    latitude = str(address.latitude)
    longitude = str(address.longitude)

    if not latitude and not longitude:
        return -1

    image_url = MAPBOX_SMAP_URL + str(latitude) + "," + str(longitude) + ",12,0/500x500@2x?access_token=" + MAPBOX_KEY
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code != requests.codes.ok:
            logger.warning("Response while getting static map image was not OK")

        # TODO check that response is actually an image not json
        temp_image = NamedTemporaryFile()
        for block in response.iter_content(1024 * 8):
            if not block:
                break
            temp_image.write(block)

        filename = str(address.pk) + "_" + str(latitude) + "_" + str(longitude) + ".png"
        address.static_map.save(filename, files.File(temp_image))
    except HTTPError as error:
        logger.warning("HTTPError occurred while getting static map image")