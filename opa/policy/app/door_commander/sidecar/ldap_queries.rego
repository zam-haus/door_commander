package app.door_commander.sidecar.ldap_queries

### Query only users that are known to the Django application.
#queries.users contains {"query":query_pattern, "variables":variables, "attributes":attributes} if {
#    query_pattern := "(&(objectClass=inetOrgPerson)(entryUUID={uuid}))"
#    uuid := data.django.users[django_id].connections[connection_idx].fields.directory_key
#    variables := {"uuid": uuid}
#    attributes := ["entryUUID", "memberOf", "uid", "cn", "objectClass"]
#}

queries.users contains {"query":query_pattern, "variables":variables, "attributes":attributes} if {
    query_pattern := "(&(objectClass=inetOrgPerson)(entryUUID=*))"
    variables := {}
    attributes := ["entryUUID", "memberOf", "uid", "cn", "objectClass"]
}

queries.groups contains {"query":query_pattern, "variables":variables, "attributes":attributes} if {
    query_pattern := "(&(|(objectClass=groupOfNames)(objectClass=groupOfUniqueNames))(cn=*))"
    variables := {}
    attributes := ["entryUUID", "uniquemember", "memberOf", "cn", "objectClass"]
}
