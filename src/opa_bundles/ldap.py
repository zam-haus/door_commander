import json
import logging

from django.conf import settings
from icecream import ic
from ldap3 import Server, ALL, SIMPLE, Connection, SUBTREE, ALL_ATTRIBUTES
from ldap3.utils.conv import escape_filter_chars

from accounts.models import UserConnection

log = logging.getLogger(__name__)


def format_search_filter(ldap_query_pattern: str, variables: dict[str, str]):
    """Formats a format string with variables that are being escaped
    E.g. pass "(entryUUID={uuid})" and dict(uuid=...)
    """
    return ldap_query_pattern.format(**{key: escape_filter_chars(value) for key, value in variables.items()})


class LdapQuerier:
    def __init__(self):
        self._server = Server(settings.LDAP_URL, get_info=ALL)
        self._conn = None

    def __enter__(self):
        self._conn: Connection = Connection(
            self._server,
            user=settings.LDAP_BIND_DN,
            password=settings.LDAP_PASSWORD,
            authentication=SIMPLE,
            auto_bind=True,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # https://ldap3.readthedocs.io/en/latest/connection.html
        # "disconnect and close the connection"
        self._conn.unbind()
        self._conn = None

    def query_ldap(self, query: str, variables: dict[str, str], attributes: list[str]) -> list[
        dict[str, str | dict[str, list[str]]]]:
        if self._conn is None:
            raise Exception('Connection was not established')
        search_filter = format_search_filter(query, variables)
        log.debug(f'Querying with search filter: {search_filter}')
        self._conn.search(
            search_base=settings.LDAP_BASE_DN,
            search_scope=SUBTREE,
            search_filter=search_filter,
            attributes=attributes or ALL_ATTRIBUTES,
        )
        # Convert the result to a list of dicts
        #ic([entry.__dict__ for entry in self._conn.entries])
        entries = [json.loads(entry.entry_to_json()) for entry in self._conn.entries]
        return entries
