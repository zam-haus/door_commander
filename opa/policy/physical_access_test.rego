package app.door_commander.physical_access

ldap := {
	"uid=some.admin,ou=users,dc=betreiberverein,dc=de": {
		"dn": ["uid=some.admin,ou=users,dc=betreiberverein,dc=de"],
		"container": ["ou=users,dc=betreiberverein,dc=de"],
		"entryUUID": ["some.admin.uuid"],
		"objectclass": ["inetOrgPerson"],
	},
	"uid=some.member,ou=users,dc=betreiberverein,dc=de": {
		"dn": ["uid=some.member,ou=users,dc=betreiberverein,dc=de"],
		"container": ["ou=users,dc=betreiberverein,dc=de"],
		"entryUUID": ["some.member.uuid"],
		"objectclass": ["inetOrgPerson"],
	},
	"cn=admin,ou=groups,dc=betreiberverein,dc=de": {
		"dn": ["cn=admin,ou=groups,dc=betreiberverein,dc=de"],
		"container": ["ou=groups,dc=betreiberverein,dc=de"],
		"objectclass": ["groupOfUniqueNames"],
		"cn": ["admins"],
		"entryUUID": ["admins.uuid"],
		"uniquemember": ["uid=some.admin,ou=users,dc=betreiberverein,dc=de"],
	},
	"cn=mitglied,ou=groups,dc=betreiberverein,dc=de": {
		"dn": ["cn=mitglied,ou=groups,dc=betreiberverein,dc=de"],
		"container": ["ou=groups,dc=betreiberverein,dc=de"],
		"objectclass": ["groupOfUniqueNames"],
		"cn": ["members"],
		"entryUUID": ["members.uuid"],
		"uniquemember": [
			"uid=some.member,ou=users,dc=betreiberverein,dc=de",
			"cn=admin,ou=groups,dc=betreiberverein,dc=de",
		],
	},
}

test_allow_django_superuser {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {
			"uuid": "local django user",
			"username": "superuser",
			"django_permissions": ["superuser"],
		},
	}

	time_val := time.parse_ns("2006-01-02T15:04:05Z07:00", "2021-07-22T16:00:00+02:00")
	allow with data.ldap as ldap with input as input
	allow_django_superuser with data.ldap as ldap with input as input
	not allow_member_open with data.ldap as ldap with input as input
	not allow_member_reopen with data.ldap as ldap with input as input
	not allow_admin_open with data.ldap as ldap with input as input
}

test_not_allow_django_superuser {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {
			"uuid": "local django user",
			"username": "superuser",
			"django_permissions": [],
		},
	}

	not allow_django_superuser with data.ldap as ldap with input as input
}

test_allow_member_open {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {"uuid": "some.member.uuid"},
		"request": {"ip": "192.168.13.37"},
	}

	time_val := time.parse_ns("2006-01-02T15:04:05Z07:00", "2021-07-22T16:00:00+02:00")
	allow with data.ldap as ldap with input as input with current_time as time_val
	allow_member_open with data.ldap as ldap with input as input with current_time as time_val
}

test_allow_member_open_2 {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {"uuid": "some.member.uuid"},
		"request": {"ip": "127.0.0.1"},
	}

	time_val := time.parse_ns("2006-01-02T15:04:05Z07:00", "2021-07-22T16:00:00+02:00")
	allow with data.ldap as ldap with input as input with current_time as time_val
	allow_member_open with data.ldap as ldap with input as input with current_time as time_val
}
test_allow_member_open_3 {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {"uuid": "some.member.uuid"},
		"request": {"ip": "::1"},
	}

	time_val := time.parse_ns("2006-01-02T15:04:05Z07:00", "2021-07-22T16:00:00+02:00")
	allow with data.ldap as ldap with input as input with current_time as time_val
	allow_member_open with data.ldap as ldap with input as input with current_time as time_val
}

test_not_allow_member_open_1 {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {"uuid": "some.member.uuid"},
		"request": {"ip": "192.168.13.37"},
	}

    # wrong time
	time_val := time.parse_ns("2006-01-02T15:04:05Z07:00", "2021-07-22T23:59:00+02:00")
	not allow_member_open with data.ldap as ldap with input as input with current_time as time_val
}
test_not_allow_member_open_2 {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {"uuid": "some.member.uuid"},
		# wrong address
		"request": {"ip": "1.2.3.4"},
	}

	time_val := time.parse_ns("2006-01-02T15:04:05Z07:00", "2021-07-22T16:00:00+02:00")
	not allow_member_open with data.ldap as ldap with input as input with current_time as time_val
}

test_allow_admin_open {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {"uuid": "some.admin.uuid"},
	}

	time_val := time.parse_ns("2006-01-02T15:04:05Z07:00", "2021-07-22T23:59:00+02:00")
	allow with data.ldap as ldap with input as input with current_time as time_val
	allow_admin_open with data.ldap as ldap with input as input with current_time as time_val
}

test_allow_reopen {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {"uuid": "some.member.uuid"},
		"request": {"ip": "192.168.13.37"},
	}

	LAYOUT := "2006-01-02T15:04:05Z07:00"

	time_val := time.parse_ns(LAYOUT, "2021-07-22T20:28:00+02:00")
	last_open := {"door7": time_val - time.parse_duration_ns("3m")}

	allow with data.ldap as ldap with input as input with current_time as time_val with data.last_open as last_open
	allow_member_reopen with data.ldap as ldap with input as input with current_time as time_val with data.last_open as last_open
}

test_not_allow_reopen_1 {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {"uuid": "some.member.uuid"},
		"request": {"ip": "192.168.13.37"},
	}

	LAYOUT := "2006-01-02T15:04:05Z07:00"

	time_val := time.parse_ns(LAYOUT, "2021-07-22T20:28:00+02:00")
	last_open := {"door7": time_val - time.parse_duration_ns("3h")} # door was not recently open

	not allow_member_reopen with data.ldap as ldap with input as input with current_time as time_val with data.last_open as last_open
}

test_not_allow_reopen_2 {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {"uuid": "some.member.uuid"},
		"request": {"ip": "192.168.13.37"},
	}

	LAYOUT := "2006-01-02T15:04:05Z07:00"

	# too late after opening hours
	time_val := time.parse_ns(LAYOUT, "2021-07-22T20:32:00+02:00")
	last_open := {"door7": time_val - time.parse_duration_ns("3m")}

	not allow_member_reopen with data.ldap as ldap with input as input with current_time as time_val with data.last_open as last_open
}

test_not_allow_reopen_3 {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		# not allowed
		"user": {"uuid": "nope"},
		"request": {"ip": "192.168.13.37"},
	}

	LAYOUT := "2006-01-02T15:04:05Z07:00"

	time_val := time.parse_ns(LAYOUT, "2021-07-22T20:28:00+02:00")
	last_open := {"door7": time_val - time.parse_duration_ns("3m")}

	not allow_member_reopen with data.ldap as ldap with input as input with current_time as time_val with data.last_open as last_open
}

# check that there is at least one szenario where someone is disallowed by all means.
test_not_allow {
	input := {
		"action": {"open": {"door": {"id": "door7"}}},
		"user": {"uuid": "", "django_permissions": ["foobar"]},
		"request": {"ip": "192.168.13.37"},
	}

	LAYOUT := "2006-01-02T15:04:05Z07:00"

	time_val := time.parse_ns(LAYOUT, "2021-07-22T20:28:00+02:00")
	last_open := {"door7": time_val - time.parse_duration_ns("40m")}

	not allow with data.ldap as ldap with input as input with current_time as time_val with data.last_open as last_open
}
