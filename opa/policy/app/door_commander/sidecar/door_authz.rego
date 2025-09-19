package app.door_commander.sidecar.door_authz
import data.app.door_commander.common.door_role_mapping

default allow = false

allow if {
	allow_open
	input.action == "open"
}

allow if {
	true
	input.action == "view"
}

default show_location_hint = false
show_location_hint if {
    input.user.authenticated
    not is_on_site
}


allow_open if {
	allow_admin_open
}

allow_open if {
	allow_member_open
}

allow_member_open if {
    is_on_site
    member_is_authorized
}

is_on_site if {
    input.user.location.locator_status[_][_] == true
    # temp workaround
    #true
}

member_is_authorized if {
    connection = input.user.user_connections[_]
    connection.fields.directory = "3a01ea23-4a7f-4c64-adce-02411cd0a480" # directory id from django admin interface
    role_name = connection.fields.latest_directory_data.resource_access["sesam.zam.haus"].roles[_]
    door_id = input.door.door.fields.mqtt_id
    door_role_mapping[door_id][_] == role_name
}

allow_admin_open if {
    is_django_superuser
}

default is_django_superuser = false

is_django_superuser if {
    #input.user.authenticated
    input.user.user.fields.is_superuser
}
