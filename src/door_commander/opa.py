import logging
import urllib.parse
from dataclasses import dataclass

import requests
from icecream import ic
from django.conf import settings

log = logging.getLogger(__name__)

@dataclass
class Policy:
    id:str
    raw:str
    def __repr__(self):
        return f"Policy(id={self.id!r}, raw={self.raw[:100]!r}...)"

def get_polices():
    try:
        url = settings.OPA_URL
        token = settings.OPA_BEARER_TOKEN
        response = requests.get(url + "/v1/policies", headers=get_auth_header())

        if response.status_code != 200:
            raise Exception("Querying OPA failed")

        result_wrapper = response.json()
        result = result_wrapper["result"]
        policies = [Policy(item["id"], item["raw"]) for item in result]
        log.debug(f"Loaded policies: {policies}")
        return policies
    except Exception as e:
        raise Exception(f"OPA query failed: {e}")

def get_query_result(query, function):
    """

    :param query: might be
        data.servers[i].ports[_] = "p2"; data.servers[i].name = name
        data.example.allow == true
    :param function:
    :return:
    """
    try:
        url = settings.OPA_URL
        token = settings.OPA_BEARER_TOKEN
        input = create_default_input(function)
        payload = dict(input=input, query=query)
        response = requests.post(url + "/v1/query", json=input, headers=get_auth_header())

        if response.status_code != 200:
            raise Exception("Auth failed")

        result_wrapper = response.json()
        result = result_wrapper["result"]
    except Exception as e:
        raise Exception(f"OPA query failed: {e}")


def get_auth_header():
    return dict(Authorization="Bearer " + settings.OPA_BEARER_TOKEN)


def get_allowed_result(path, function, key="allow"):
    return get_data_result(path+"/"+key, function) is True

def check_allowed(path, function):
    if get_data_result(path+"/allow", function) is True:
        return
    else:
        raise Exception("Unauthorized")  # TODO 401/403

def get_data_result(path, function):
    """

    :param path: might be "system/authz/allow"
    :param function:
    :return:
    """
    try:
        url = settings.OPA_URL
        token = settings.OPA_BEARER_TOKEN
        input = dict(input=create_default_input(function))
        # Normalize the URL, OPA uses problematic redirects https://github.com/open-policy-agent/opa/issues/2137
        url: str
        fullurl = url \
                  + ("" if url.endswith("/") else "/") \
                  + "v1/data" \
                  + ("" if path.startswith("/") else "/") \
                  + path
        response = requests.post(fullurl, json=input, headers=get_auth_header())

        if response.status_code != 200:
            raise Exception("OPA query failed")

        result = response.json()
        # log.setLevel(logging.DEBUG)
        log.debug("Return authorization result %s", ic.format(path, input, result))
        return result['result'] if 'result' in result else None
    except Exception as e:
        raise Exception(f"OPA query failed: {e}")


def create_default_input(function):
    return function
