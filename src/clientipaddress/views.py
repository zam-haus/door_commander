from ipaddress import IPv4Address, IPv6Address

from django.http import JsonResponse
from django.shortcuts import render
from icecream import ic
from ipware import get_client_ip


# Create your views here.
def myip(request):
    #ic(request.headers)
    #ic(request.META)
    try:
        ip = get_client_ip(request)
        if isinstance(ip, IPv4Address):
            return JsonResponse({"ip": str(ip), "protocol": "IPv4"})
        elif isinstance(ip, IPv6Address):
            return JsonResponse({"ip": str(ip), "protocol": "IPv6"})
        else:
            raise Exception("Unrecognized IP format.")
    except:
        return JsonResponse({"error": "Exception"}, status=500)
