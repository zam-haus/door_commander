from accounts.models import User
from door_commander.model_to_json import serialize_model
from door_commander.opa import get_allowed_result
from door_commander.request_location_info import get_location_info


def create_door_info(door):
    return dict(door=serialize_model(door))


def check_can_open_door(request, door):
    user_dict = create_request_user_info(request)
    has_permission = get_allowed_result("app/door_commander/physical_access",
                                        dict(action="open", user=user_dict, door=create_door_info(door)))
    return has_permission


def check_can_view_door(request, door):
    user_dict = create_request_user_info(request)
    has_permission = get_allowed_result("app/door_commander/physical_access",
                                        dict(action="view", user=user_dict, door=create_door_info(door)))
    return has_permission


def check_location_hint(request):
    user_dict = create_request_user_info(request)
    has_permission = get_allowed_result("app/door_commander/physical_access", dict(user=user_dict),
                                        key="show_location_hint")
    return has_permission


def create_request_user_info(request):
    permissions = [serialize_model(perm) for perm in request.user.user_permissions.all()]
    if isinstance(request.user, User):
        user = serialize_model(request.user)
        user_connections = [serialize_model(conn) for conn in request.user.connections.all()]
    else:
        user = None
        user_connections = []
    authenticated = request.user.is_authenticated
    location_info = get_location_info(request)
    # ic(user_connections, permissions, user, authenticated, location_info)
    user_dict = dict(authenticated=authenticated, user=user, user_permissions=permissions,
                     user_connections=user_connections,
                     location=location_info, )
    return user_dict
