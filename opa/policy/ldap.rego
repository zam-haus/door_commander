package app.door_commander.ldap

ldap := data.ldap

ldap_user_by_uuid[uuid] = user {
	some dn
	ldap_users[dn]
	ldap_entry := ldap[dn]
	uuid := ldap_entry.entryUUID[_]
	user := dn
}

ldap_users[dn] {
	ldap_entry := ldap[dn]
	ldap_entry.objectclass[_] == "inetOrgPerson"
}

ldap_groups[dn] {
	ldap_entry := ldap[dn]
	ldap_entry.objectclass[_] == "groupOfUniqueNames"
}

ldap_group_by_name[name] = group {
	some dn
	ldap_groups[dn]
	ldap_entry := ldap[dn]
	name := ldap_entry.cn[_]
	group := dn
}

ldap_membership_graph[group_dn] = members {
	ldap_groups[group_dn]
	group := ldap[group_dn]
	members := group.uniquemember
}

# a user has no members, but is part of the graph
ldap_membership_graph[user_dn] = members {
	ldap_users[user_dn]
	members := []
}

ldap_group_members[group_dn] = members {
	ldap_groups[group_dn]
	members := graph.reachable(ldap_membership_graph, {group_dn})
}

ldap_user_groups[user_dn] = groups {
	ldap_users[user_dn]
	groups := {group_dn |
		ldap_groups[group_dn]
		user_dn == ldap_group_members[group_dn][_]
	}
}

group_by_name_members_by_uuid[name] = uuids {
	group := ldap_group_by_name[name]
	uuids = {uuid |
		user := ldap_user_by_uuid[uuid]
		user == ldap_group_members[group][_]
	}
}