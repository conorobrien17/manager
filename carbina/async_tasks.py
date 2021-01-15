import logging
from django_rq import job
from django.core import files
import requests
from tempfile import NamedTemporaryFile
from requests.exceptions import HTTPError
from carbina.models import Address
from carbina.apps import ERROR_FLAG

MAPBOX_KEY = 'pk.eyJ1IjoiY29ub3JvYnJpZW4iLCJhIjoiY2tnbDVhOThhMTc4cDJybnM5dHU3bjlvOCJ9.rApCMl8Y1fh3Iom20QnYKw'
MAPBOX_GEOCODE_URL = 'https://api.mapbox.com/geocoding/v5/mapbox.places/'
MAPBOX_SMAP_URL = 'https://api.mapbox.com/styles/v1/mapbox/dark-v10/static/'
MAPBOX_DRIVING_URL = 'https://api.mapbox.com/directions/v5/mapbox/driving/'
logger = logging.getLogger('file')

SHOP_LAT = '-75.375504'
SHOP_LONG = '40.159940'

LATITUDE_INDEX = 0
LONGITUDE_INDEX = 1

METERS_TO_MILES = 1609.344


# TODO watch out for HTTP 429 Too Many Requests from Mapbox when usage exceeds limit of requests/min
def map_box_json_call(request_url):
    response = requests.get(request_url)
    if response.status_code == 200:
        json = response.json()
        return json
    if response.status_code == 429:
        return response.status_code
    return ERROR_FLAG


@job('default', timeout=3600)
def forward_geocode_call(address):
    # See documentation for the call made here: https://docs.mapbox.com/api/search/geocoding/#forward-geocoding
    try:
        # TODO cleanup the way this gets called and store the image in the model to avoid API calls/more dns requests
        requestURL = MAPBOX_GEOCODE_URL + address.street + " " + address.city + " " + address.state + " " + str(address.zip_code) + ".json?access_token=" + MAPBOX_KEY
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
    except HTTPError or ConnectionError as error:
        logger.exception("Error receiving geocoding API response")

    return address


@job('default', timeout=3600)
def get_static_map_image(address):
    import hashlib

    if address.static_map is None:
        hash_object = hashlib.md5(str(address.__str__()).encode('utf-8'))
    else:
        return address

    if address.latitude is None or address.longitude is None:
        return ERROR_FLAG

    latitude = str(address.latitude)
    longitude = str(address.longitude)


    image_url = MAPBOX_SMAP_URL + latitude + "," + longitude + ",12,0/500x500@2x?access_token=" + MAPBOX_KEY
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

        filename = hash_object.hexdigest() + ".png"
        address.static_map.save(filename, files.File(temp_image))
    except HTTPError or ConnectionError as error:
        logger.warning("HTTPError occurred while getting static map image")

    return address


@job('default', timeout=3600)
def get_navigation_info(address):
    if address is None or address.latitude is None or address.longitude is None:
        return ERROR_FLAG

    # Cast the float values to strings
    latitude = str(address.latitude)
    longitude = str(address.longitude)

    # Build the URL for the API call
    request_url = MAPBOX_DRIVING_URL + SHOP_LAT + "," + SHOP_LONG + ";" + latitude + "," + longitude + '?access_token=' + MAPBOX_KEY

    try:
        # Issue the API call, store the JSON returned by the call
        json = map_box_json_call(request_url)
        # Parse the JSON
        routes = json.get('routes')[0]
        duration_seconds = routes.get('duration')
        distance_meters = routes.get('distance')
        summary = routes.get('legs')[0].get('summary')

        if duration_seconds:
            address.duration_shop = float(duration_seconds / 60)
        else:
            address.duration_shop = None

        if distance_meters:
            address.distance_shop = distance_meters / METERS_TO_MILES
        else:
            address.distance_shop = None

        if summary:
            address.driving_summary = summary
        else:
            address.driving_summary = None

        address.save()
        logger.debug("Updated Address with navigation information")
    except HTTPError or ConnectionError as error:
        logger.error("HTTP error occurred while fetching navigation info for Address")
    return address
