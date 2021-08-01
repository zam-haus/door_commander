package app.door_commander.physical_access

import data.app.door_commander.ldap

default allow = false

allow {
	input.action.open
	allow_open
}

allow {
	allow_django_superuser
}

allow_django_superuser {
	# django superusers may do everything.
	input.user.django_permissions[_] == "superuser"
}

allow_open {
	allow_admin_open
}

allow_open {
	allow_member_reopen
}

allow_open {
	allow_member_open
}

allow_member_open {
	is_member
	is_present
	opening_hours_now
	input.action.open.door.id == ["door3", "door5", "door7"][_]
}

opening_hours_now {
	is_in_opening_hours(current_time)
}

within_reopen_grace_time {
	is_in_opening_hours(current_time - time.parse_duration_ns("30m"))
}

door_was_recently_open[door] {
	current_time - time.parse_duration_ns("5m") < last_open[door]
}

is_member{
	ldap.group_by_name_members_by_uuid["members"][_] == input.user.uuid
}
WIFI_IP_ADDRESSES = {"127.0.0.1/32", "192.168.0.0/16", "::1/128"}
is_present{
    cidr := WIFI_IP_ADDRESSES[_]
    net.cidr_contains(cidr, input.request.ip)
}

allow_member_reopen {
	# if someone forgot something, they can reenter up to 30min after opening hours (assuming opening hours are not shorter than 30min)
	is_member
    is_present
    within_reopen_grace_time
    door_was_recently_open[input.action.open.door.id]
	input.action.open.door.id == ["door3", "door5", "door7"][_]
}

allow_admin_open {
	ldap.group_by_name_members_by_uuid.admins[_] == input.user.uuid
}

is_in_opening_hours(ns) {
	[hour, minute, second] := time.clock([ns, TZ])
	day := time.weekday([ns, TZ])
	hour > 10
	hour < 20
	some i
	day != ["Sunday", "Tuesday"][i]
}

TZ = "Europe/Berlin"

last_open = data.last_open

current_time := time.now_ns()
