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
MAPBOX_DRIVING_URL = 'https://api.mapbox.com/directions/v5/mapbox/driving/'
logger = logging.getLogger('file')

SHOP_LAT = -75.375504
SHOP_LONG = 40.159940

LATITUDE_INDEX = 0
LONGITUDE_INDEX = 1

METERS_TO_MILES = 1609.344

# TODO watch out for HTTP 429 Too Many Requests from Mapbox when usage exceeds limit of requests/min
def map_box_json_call(request_url):
    response = requests.get(request_url)
    json = response.json()
    return json


@job('default', timeout=3600)
def forward_geocode_call(address):
    # See documentation for the call made here: https://docs.mapbox.com/api/search/geocoding/#forward-geocoding
    try:
        # TODO cleanup the way this gets called and store the image in the model to avoid API calls/more dns requests
        requestURL = address.street + " " + address.city + " " + address.state + " " + str(address.zip_code) + ".json?access_token=" + MAPBOX_KEY
        json = map_box_json_call(requestURL)
        coordinates = json.get('features')[0].get('center')

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


@job('default', timeout=3600)
def get_navigation_info(address_pk):
    address = Address.objects.get(pk=int(address_pk))
    latitude = str(address.latitude)
    longitude = str(address.longitude)
    request_url = MAPBOX_DRIVING_URL + str(SHOP_LAT) + "," + str(SHOP_LONG) + ";" + latitude + "," + longitude + '?access_token=' + MAPBOX_KEY
    json = map_box_json_call(request_url)
    routes = json.get('routes')[0]
    duration_seconds = routes.get('duration')
    duration = duration_seconds / 60
    distance_meters = routes.get('distance')
    distance = distance_meters / METERS_TO_MILES
    summary = routes.get('legs')[0].get('summary')
    address.distance_shop = float(distance)
    address.duration_shop = float(duration)
    address.driving_summary = str(summary)
    address.save()