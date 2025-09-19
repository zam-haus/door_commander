import hashlib
import ipaddress
import json
import logging
import os
import tarfile
import time
import io
import gzip
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from icecream import ic
from ldap3.core.exceptions import LDAPInvalidFilterError, LDAPCursorAttributeError, LDAPCommunicationError

from accounts.models import User
from door_commander import settings
from door_commander.opa import get_polices, get_data_result
from doors.models import Door
from opa_bundles.ldap import LdapQuerier
from web_homepage.views import serialize_model
from door_commander.opa import get_polices
from doors.models import RemoteClient

log = logging.getLogger(__name__)


def get_ldap_data():
    try:
        ldap_query_groups = get_data_result("app/door_commander/sidecar/ldap_queries/queries", None) or dict()
    except:
        # If the LDAP queries are not available, we don't want to crash the bundle generation.
        return None
    data = dict()
    with LdapQuerier() as ldap:
        ldap: LdapQuerier
        for query_group, queries in ldap_query_groups.items():
            data[query_group] = []
            for query in queries:
                match query:
                    case {"variables": variables, "attributes": attributes, "query": query_pattern}:
                        try:
                            result = ldap.query_ldap(query_pattern, variables, attributes)
                            data[query_group] += result
                        # https://ldap3.readthedocs.io/en/latest/exceptions.html
                        # if the LDAP server goes down, we want to keep the historical bundle data, and not deliver an empty bundle.
                        except LDAPCommunicationError as e:
                            log.error(f"LDAP communication error, delivering no bundle without LDAP data: {e}")
                            raise
                        # if the query is invalid, we want to log it, but still deliver the bundle.
                        except Exception as e:
                            log.error(
                                f"Failed to query LDAP, delivering bundle without LDAP data: {e}, query= {query!r} % {variables} -> {attributes}")
    return data


def get_django_user_data():
    users = {str(user.pk): dict(
        user=serialize_model(user),
        permissions=[serialize_model(p) for p in user.user_permissions.all()],
        connections=[serialize_model(c) for c in user.connections.all()],
        cards=[serialize_model(c) for c in user.cards.all()],
    ) for user in User.objects.all()}
    doors = {str(door.pk): dict(
        door=serialize_model(door),
    ) for door in Door.objects.all()}
    data = dict(users=users, doors=doors)
    return data


def get_bundle(request, filename: str):
    # ic(request, filename)
    if not (authorization := _authorize_with_bearer(request)):
        return HttpResponse('Unauthorized', status=401)

    download_filename = filename.split("/")[-1]

    match filename:

        case "door_authz.tar.gz":
            # fd = open(path_to_file, 'rb')
            hashes = dict()
            with InMemoryTarFile() as tar_file:
                tar = tar_file.tar
                _add_policies_and_data_to_bundle(hashes, tar)

                data = get_data_result("app/door_commander/sidecar/ldap_export", None)
                relpath = "sidecar/data.json"
                _add_json_to_bundle(data, hashes, relpath, tar)

            response = get_download_or_not_modified(download_filename, tar_file.fd, hashes, request)
            return response

        case "sidecar_authz.tar.gz":
            # ic(authorization)
            # Only the sidecar may access the PII data bundle, the RPis are not allowed to.
            if not isinstance(authorization, OpaSidecarTokenAuthorization):
                log.warning("Unauthorized sidecar authorization request")
                return HttpResponse('Unauthorized', status=401)
            hashes = dict()
            with InMemoryTarFile() as tar_file:
                tar = tar_file.tar
                _add_policies_and_data_to_bundle(hashes, tar)

                data = get_ldap_data()
                relpath = "ldap/data.json"
                _add_json_to_bundle(data, hashes, relpath, tar)

                data = get_django_user_data()
                relpath = "django/data.json"
                _add_json_to_bundle(data, hashes, relpath, tar)

            response = get_download_or_not_modified(download_filename, tar_file.fd, hashes, request)
            return response

        case _:
            return HttpResponseNotFound()
    # return redirect("https://betreiberverein.de/impressum/")


def _add_json_to_bundle(data, hashes, relpath, tar):
    _add_file_to_tar(tar, relpath, BytesIO(json.dumps(data).encode("utf-8")))
    hash = hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()
    hashes[relpath] = hash
    log.debug(f"Delivering {relpath}, hash={hash}")


def _add_policies_and_data_to_bundle(hashes, tar):
    path = Path(settings.OPA_BUNDLE_DIRECTORY)
    if not path.exists():
        raise Exception('Bundle directory does not exist')
    for file in path.glob("**/*.rego"):
        _add_file_to_tar_and_hash(file, hashes, path, tar)
    for file in path.glob("**/*.json"):
        _add_file_to_tar_and_hash(file, hashes, path, tar)


def _add_file_to_tar_and_hash(file, hashes, path, tar):
    fd = open(file, 'rb')
    hash = hashlib.sha256(fd.read()).hexdigest()
    fd.seek(0)
    relpath = os.path.relpath(str(file), path)
    log.debug(
        f"Delivering {file} as {relpath}, hash={hash}")
    # For rego files, only the package declaration in the file is used.
    _add_file_to_tar(tar, relpath, fd)
    hashes[relpath] = hash


def get_download_or_not_modified(download_filename, fd, content_hashes, request):
    # Generate an ETAG with sha256 hash of the file content
    etag = hashlib.sha256(json.dumps(content_hashes).encode("utf-8")).hexdigest()
    etag = "W/" + json.dumps(etag)
    request_etag = request.headers.get("If-None-Match")
    if request_etag == etag:
        log.debug(f"ETag {etag} matches, returning 304 Not Modified")
        response = HttpResponse(status=304)
    else:
        response = _make_file_download_response(fd, download_filename)
        response['ETag'] = etag
    return response


class InMemoryTarFile:
    def __init__(self):
        self.fd = io.BytesIO(b"")
        self.tar = tarfile.open(name=None, mode='w:gz', fileobj=self.fd)

    def __enter__(self) -> 'InMemoryTarFile':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tar.close()
        # ic(fd, fd.tell())
        # Seek to the start of the written tarfile
        self.fd.seek(0)


def _make_file_download_response(fd, file_name, etag=None) -> FileResponse:
    response = FileResponse(fd)
    response['Content-Disposition'] = 'inline; filename=' + file_name
    return response


def _add_file_to_tar(tar, filename, fd):
    tarinfo = tarfile.TarInfo(filename)
    fd.seek(0, os.SEEK_END)
    tarinfo.size = fd.tell()
    fd.seek(0)
    tar.addfile(tarinfo, fd)


# OPA calls this with POST, so CSRF protection needs to be disabled
@csrf_exempt
def post_decision_log(request: WSGIRequest, hostname):
    # TODO update cards' last_used_at timestamp when decision log is received
    if not (authorization := _authorize_with_bearer(request)):
        return HttpResponse('Unauthorized', status=401)

    if isinstance(authorization, OpaSidecarTokenAuthorization):
        # We don't want to log decision logs from the local OPA instance,
        # we can have them in the console
        return HttpResponse("OK", status=200)

    # ic(hostname, request.headers)
    body = request.body
    if request.headers.get("Content-Encoding") == "gzip":
        body = gzip.decompress(body)
    if not request.headers.get("Content-Type") == "application/json":
        raise Exception("Unsupported Content-Type")
    body = body.decode("utf-8")
    data = json.loads(body)
    for decision in data:
        # ic(decision)
        result = decision.get("result", None)
        input = decision.get("input", None)
        path = decision.get("path", None)
        timestamp = decision.get("timestamp", None)
        log.getChild("decision_log").info(
            f"Decision logged by {hostname!r}:\n"
            f"Timestamp= {timestamp!r}\n"
            f"Path= {path!r}\n"
            f"Input= {input!r}\n"
            f"Result= {result!r}"
        )
    return HttpResponse("OK")


@dataclass
class OpaClientTokenAuthorization:
    "An OPA running on an RPi"
    pass


@dataclass
class OpaSidecarTokenAuthorization:
    "The OPA included in the docker compose file"
    pass


def _authorize_with_bearer(request: WSGIRequest):
    bearer = request.headers.get("Authorization", None)
    BEARER = "Bearer "
    if not bearer or not bearer.startswith(BEARER):
        if settings.DEBUG:
            log.info("Client authorized by debug mode, no Bearer was provided.")
            return OpaSidecarTokenAuthorization()
        return None
    token = bearer.lstrip(BEARER)
    # ic(token)
    match token:
        case "":
            # Protect against empty tokens, when the variable is not set.
            return None
        case settings.OPA_BUNDLE_SERVER_BEARER_TOKEN:
            authorized = OpaClientTokenAuthorization()
        case settings.OPA_BEARER_TOKEN:
            authorized = OpaSidecarTokenAuthorization()
        case _:
            # don't use get(token=...) since that doesn't work for encrypted fields.
            # TODO split from username:token for efficiency
            if any(x for x in RemoteClient.objects.all() if x.token == token):
                authorized = OpaClientTokenAuthorization()
            else:
                authorized = None
    log.debug(
        f"Request from {request.META['REMOTE_ADDR']} to OPA bundles / decision log API was authorized as {authorized}")
    return authorized


# OPA calls this with POST, so CSRF protection needs to be disabled
@csrf_exempt
def post_status(request: WSGIRequest, hostname: str):
    if not _authorize_with_bearer(request):
        return HttpResponse('Unauthorized', status=401)
    # ic(hostname, request.headers)
    body = request.body
    if request.headers.get("Content-Encoding") == "gzip":
        body = gzip.decompress(body)
    if not request.headers.get("Content-Type") == "application/json":
        raise Exception("Unsupported Content-Type")
    body = body.decode("utf-8")
    data = json.loads(body)
    bundles_status = data.get("bundles", None)
    # decision_logs_status = data.get("decision_logs", None)
    version = data.get("labels", dict()).get("version", None)
    # ic(bundles_status, version)
    log.getChild("status").info(
        f"On {hostname!r}:\n"
        f"bundle status: {bundles_status!r}\n"
        f"version status: {version!r}"
    )

    return HttpResponse("OK")
