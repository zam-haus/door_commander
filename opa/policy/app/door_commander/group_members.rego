package app.door_commander.group_members

#a := "a"
## All nodes need to be in the list of vertices as a source node
#b := graph.reachable({"a":{"b","c"}, "b":{"d"}, "c":{"d","e"}, "d":set(), "e":set()}, ["a"])
#c := graph.reachable(membership_groups, ["cn=mitglied,ou=groups,dc=betreiberverein,dc=de"])

membership_groups[group_dn] contains group_member_dn if {
    group_dn := data.ldap.groups[group_idx].dn
    group_member_dn := data.ldap.groups[group_idx].attributes.uniqueMember[member_idx]
    #group_uuid := data.
}


membership_users[user_dn] := set() if {
    user_dn := data.ldap.users[group_idx].dn
}

#membership_recursive[group_dn] := graph.reachable(membership, [group_dn]) if {
#    group_dn := data.ldap.groups[group_idx].dn
#}

membership_recursive[group_dn] contains group_member_dn if {
    group_dn := data.ldap.groups[group_idx].dn
    reachable := graph.reachable(object.union(membership_groups, membership_users), [group_dn])
    group_member_dn := reachable[group_member_idx]
}