package app.door_commander.client.door_authz

import data.app.door_commander.common.door_role_mapping
import data.app.door_commander.common.role_group_mapping

default allow = false

allow if {
	allow_open
	input.action == "open"
}

allow_open if {
	allow_admin_open
}

allow_open if {
	allow_member_open
}

allow_admin_open if {
    false
}

allow_member_open if {
    false
}