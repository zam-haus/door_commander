package app.door_commander.ldap

#opa eval -d . "data.app.door_commander.ldap"

ldap_data := {
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

test_ldap_user_by_uuid {
	result := ldap_user_by_uuid with data.ldap as ldap_data
	result == {
		"some.admin.uuid": "uid=some.admin,ou=users,dc=betreiberverein,dc=de",
		"some.member.uuid": "uid=some.member,ou=users,dc=betreiberverein,dc=de",
	}
}

test_ldap_group_by_name {
	result := ldap_group_by_name with data.ldap as ldap_data
	result == {
		"admins": "cn=admin,ou=groups,dc=betreiberverein,dc=de",
		"members": "cn=mitglied,ou=groups,dc=betreiberverein,dc=de",
	}
}

test_ldap_users {
	result := ldap_users with data.ldap as ldap_data
	result == {
		"uid=some.admin,ou=users,dc=betreiberverein,dc=de",
		"uid=some.member,ou=users,dc=betreiberverein,dc=de",
	}
}

test_ldap_groups {
	result := ldap_groups with data.ldap as ldap_data
	result == {
		"cn=admin,ou=groups,dc=betreiberverein,dc=de",
		"cn=mitglied,ou=groups,dc=betreiberverein,dc=de",
	}
}

test_ldap_group_members {
	result := ldap_group_members with data.ldap as ldap_data
	result == {
		"cn=admin,ou=groups,dc=betreiberverein,dc=de": {
			"cn=admin,ou=groups,dc=betreiberverein,dc=de",
			"uid=some.admin,ou=users,dc=betreiberverein,dc=de",
		},
		"cn=mitglied,ou=groups,dc=betreiberverein,dc=de": {
			"cn=mitglied,ou=groups,dc=betreiberverein,dc=de",
			"uid=some.member,ou=users,dc=betreiberverein,dc=de",
			"cn=admin,ou=groups,dc=betreiberverein,dc=de",
			"uid=some.admin,ou=users,dc=betreiberverein,dc=de",
		},
	}
}

test_ldap_user_groups {
	result := ldap_user_groups with data.ldap as ldap_data
	result == {
		"uid=some.admin,ou=users,dc=betreiberverein,dc=de": {
			"cn=admin,ou=groups,dc=betreiberverein,dc=de",
			"cn=mitglied,ou=groups,dc=betreiberverein,dc=de",
		},
		"uid=some.member,ou=users,dc=betreiberverein,dc=de": {"cn=mitglied,ou=groups,dc=betreiberverein,dc=de"},
	}
}

# opa eval -d . -d ldap_test.rego "data.app.door_commander.ldap.test_export"
#test_export[foo] {
#	foo := ldap_user_groups with data.ldap as ldap_data
#}
