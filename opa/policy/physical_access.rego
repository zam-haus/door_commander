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
}


allow_open {
	allow_admin_open
}

allow_open {
	allow_member_open
}

allow_member_open {
    false
}

allow_admin_open {
    is_django_superuser
}

default is_django_superuser = false

is_django_superuser{
    #input.user.authenticated
    input.user.user.fields.is_superuser
}