from .models import Address
from .apps import ERROR_FLAG, FALSE_FLAG, TRUE_FLAG

# TODO add logging here, stop adding todos everywhere too


def are_nav_values_loaded(address):
    if address is None or not address:
        return ERROR_FLAG
    try:
        if address.distance_shop and address.duration_shop and address.driving_summary:
            return TRUE_FLAG
        return FALSE_FLAG
    except Address.DoesNotExist:
        return ERROR_FLAG
