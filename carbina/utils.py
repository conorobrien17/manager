from .models import Address

# TODO add logging here, stop adding todos everywhere too


def are_nav_values_loaded(address):
    if address is None or not address:
        return -1
    try:
        if address.distance_shop and address.duration_shop and address.driving_summary:
            return 0
        return 1
    except Address.DoesNotExist:
        return -1
