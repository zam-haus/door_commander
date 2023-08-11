package app.door_commander.physical_access

default allow = false

allow {
	allow_open
	input.action == "open"
}

allow {
	true
	input.action == "view"
}

default show_location_hint = false
show_location_hint {
    input.user.authenticated
    not is_on_site
}


allow_open {
	allow_admin_open
}

allow_open {
	allow_member_open
}


door_role_mapping = {
    "D6545C11-CC5A-421E-9D7D-0B2F762C6282" : ["MayOpenFrontDoor"],
    "2AB91A7B-26D5-4429-A2B8-9EE1C4DC1FC3" : ["MayOpenFrontDoor"],
    "ED9AE67F-0779-4248-AE46-0167791A73AF" : ["MayOpenNordUG"],
    "C840743E-F562-4DAC-8AEE-0622F000DCCF" : ["MayOpenNordEG"],
}

allow_member_open {
    is_on_site
    member_is_authorized
}

is_on_site {
    input.user.location.locator_status[_][_] == true
    # temp workaround
    #true
}

member_is_authorized {
    connection = input.user.user_connections[_]
    connection.fields.directory = "3a01ea23-4a7f-4c64-adce-02411cd0a480" # directory id from django admin interface
    role_name = connection.fields.latest_directory_data.resource_access["sesam.zam.haus"].roles[_]
    door_id = input.door.door.fields.mqtt_id
    door_role_mapping[door_id][_] == role_name
}

allow_admin_open {
    is_django_superuser
}

default is_django_superuser = false

is_django_superuser{
    #input.user.authenticated
    input.user.user.fields.is_superuser
}
