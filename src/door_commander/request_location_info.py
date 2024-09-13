import ipaddress
import logging

from django.conf import settings
from icecream import ic

from clientipaddress.mqtt import wifi_locator_mqtt

log_ip = logging.getLogger(__name__ + ".ip")
IPWARE_KWARGS = getattr(settings, 'IPWARE_KWARGS', None)
PERMITTED_IP_NETWORKS = getattr(settings, 'PERMITTED_IP_NETWORKS', None)


from ipware import get_client_ip


def get_location_info(request):
    if IPWARE_KWARGS is None or PERMITTED_IP_NETWORKS is None:
        return dict(status="IPWARE_NOT_CONFIGURED")
    else:
        ip = get_client_ip(request, **IPWARE_KWARGS)
        log_ip.debug("Request IP is %r", ip)
        # log_ip.debug(ic.format(request.META))
        # log_ip.debug(ic.format(request.headers))
        if ip:
            networks = wifi_locator_mqtt.ip_networks
            locator_status = {
                locator_mqtt_id: [
                    (ip in locator_ip_network)
                    for locator_ip_network in locator_ip_networks
                ]
                for locator_mqtt_id, locator_ip_networks in networks.items()
            }
            permitted_networks_status = {
                str(network): (ipaddress.ip_address(ip) in network)
                for network in PERMITTED_IP_NETWORKS
            }
            return dict(ip=str(ip), permitted_networks_status=permitted_networks_status, locator_status=locator_status)
        else:
            return dict(status="NO_IP_PRESENT")
