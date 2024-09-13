import dataclasses
import logging
import uuid
from dataclasses import dataclass

from django.core.handlers.wsgi import WSGIRequest

from accounts.models import User
from apitoken.models import ApiToken
from door_commander.opa import get_data_result

log = logging.getLogger(__name__)


@dataclass
class TokenData:
    id: str
    serial: int

    @property
    def uuid(self):
        return uuid.UUID(hex=self.id)


def _validate_and_unpack_token(token: str) -> dict | None:
    result = get_data_result('app/door_commander/apitoken', dict(token=token))
    if result['token_is_valid'] is True:
        payload = result['token_payload']
        return payload
    return None


def authenticate(token: str) -> User | None:
    raw_token_data = _validate_and_unpack_token(token)
    if raw_token_data:
        token_data = TokenData(**raw_token_data)
        token_database_entry = ApiToken.objects.get(id=token_data.id)
        current_serial = token_data.serial
        if current_serial <= token_database_entry.newest_serial:
            if current_serial >= token_database_entry.oldest_serial or token_database_entry.sync_mode:
                user = token_database_entry.user
                if user.is_active and not user.is_anonymous:
                    _update_last_seen(current_serial, token_database_entry)
                    return user
            else:
                log.warning("API Token %r with serial %r is expired.", token_data.id, token_data.serial)
        else:
            log.error(
                "Validly signed token serial %r is newer than %r registered in the database for uuid %r",
                current_serial, token_database_entry.newest_serial, token_data.id
            )
    return None


def _pack_and_sign_token(raw_token_data) -> str:
    result = get_data_result('app/door_commander/apitoken', dict(token_data=raw_token_data))
    # log.debug(result)
    token: str = result.get('token')
    if not token:
        raise Exception(f"OPA did not return a signed token. Secret is present = {result.get('secret_is_present')!r}")
    return token


def renew_token(api_token: ApiToken) -> str:
    api_token.newest_serial += 1
    api_token.save()
    token_data = TokenData(id=str(api_token.id), serial=api_token.newest_serial)
    raw_token_data = dataclasses.asdict(token_data)
    token = _pack_and_sign_token(raw_token_data)
    return token


def check_permission_and_renew(request: WSGIRequest, id: str):
    requested_token = ApiToken.objects.get(id=uuid.UUID(id))
    if requested_token:
        if requested_token.user == request.user or requested_token.register_mode:
            return renew_token(requested_token)
        else:
            raise PermissionError("Unauthorized to renew another users token")
    raise PermissionError("Token does not exist")


def _update_last_seen(current_serial, token_database_entry):
    token_database_entry.oldest_serial = max(token_database_entry.oldest_serial, current_serial)
    token_database_entry.register_mode = False
    token_database_entry.sync_mode = False
    token_database_entry.save()
