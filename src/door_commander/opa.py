import logging

import requests
from django.contrib.auth import login
from icecream import ic
from django.conf import settings

log = logging.getLogger(__name__)
log_explain = log.getChild("explain")


def get_query_result(query, input_data):
    """

    :param query: might be
        data.servers[i].ports[_] = "p2"; data.servers[i].name = name
        data.example.allow == true
    :param function:
    :return:
    """
    try:
        url = settings.OPA_URL
        payload = dict(input=input_data, query=query)
        response = requests.post(url + "/v1/query", json=payload, headers=get_auth_header())

        if response.status_code != 200:
            raise Exception("Auth failed")

        result_wrapper = response.json()
        result = result_wrapper["result"]
        return result
    except Exception as exc:
        raise Exception("Auth check failed") from exc


def get_auth_header():
    return dict(Authorization="Bearer " + settings.OPA_BEARER_TOKEN)


def get_allowed_result(path, input_data, key="allow"):
    try:
        if get_data_result(path, input_data)[key] is True:
            return True
        else:
            return False
    except Exception as exc:
        raise Exception("Auth check failed") from exc


def check_allowed(path, input_data):
    try:
        if get_data_result(path, input_data)["allow"] is True:
            return
        else:
            raise Exception("Unauthorized")  # TODO 401/403
    except Exception as exc:
        raise Exception("Auth check failed") from exc


def get_data_result(path, input_data):
    """

    :param path: might be "system/authz/allow" or "app/door_commander/physical_access"
    :param input_data: might be dict(action="open",user=some_user_info,door=some_door_info)
    :return:
    """
    try:
        url = settings.OPA_URL
        request_data = dict(input=input_data)
        # Normalize the URL, OPA uses problematic redirects https://github.com/open-policy-agent/opa/issues/2137
        url: str

        explain = log_explain.getEffectiveLevel() <= logging.DEBUG

        fullurl = (
                url
                + ("" if url.endswith("/") else "/")
                + "v1/data"
                + ("" if path.startswith("/") else "/")
                + path
                + ("?explain=full&pretty" if explain else "")
        )
        response = requests.post(fullurl, json=request_data, headers=get_auth_header())

        if response.status_code != 200:
            raise Exception("Auth failed")

        result:dict = response.json()
        # log.setLevel(logging.DEBUG)
        if explain:
            explanations = result.pop('explanation',None)
            for explanation in explanations:
                log.debug("OPA explanation: %s", explanation)


        log.debug("Return authorization result %s", ic.format(path, request_data, result))
        return result['result']
    except Exception as exc:
        raise Exception("Auth check failed") from exc
