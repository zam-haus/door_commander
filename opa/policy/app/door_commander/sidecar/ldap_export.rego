# This file determines the data delivered to the RPi OPA client instances
package app.door_commander.sidecar.ldap_export

import data.app.door_commander.group_members.membership_recursive
import data.app.door_commander.common.door_role_mapping
import data.app.door_commander.common.role_group_mapping


# maps door UUIDs to group CNs
door_entry_uuid_mapping[door_uuid] contains group_member_uuid if { # group_member_uuid
    door_role_mapping[door_uuid]
    role_name := door_role_mapping[door_uuid][_]
    group_cn := role_group_mapping[role_name][_]
    data.ldap.groups[group_idx].attributes.cn[_] == group_cn
    group_dn := data.ldap.groups[group_idx].dn
    group_members_dn := membership_recursive[group_dn][_]
    #x:= group_members_dn
    group_members_dn == data.ldap.users[user_idx].dn
    group_member_uuid := data.ldap.users[user_idx].attributes.entryUUID[_]
}

card_id_user_uuid_mapping[card_id] contains user_uuid if {
    card_id := data.django.users[dj_uuid].cards[_].fields.secret_id
    user_uuid := data.django.users[dj_uuid].connections[_].fields.directory_key
}

door_uuid_card_id_mapping[door_uuid] contains card_id if {
    user_uuid := door_entry_uuid_mapping[door_uuid][_]
    card_id_user_uuid_mapping[card_id][_] == user_uuid
}

#keycloak_users_groups contains {"django_user_uuid":dj_uuid, "keycloak_group_claim":kc_group} if {
#    data.django.users[dj_uuid]
#    data.django.users[dj_uuid].connections[_].fields.latest_directory_data.resource_access["sesam.zam.haus"].roles[_]=kc_group
#}
#
#ldap_users_groups contains {"ldap_user_uuid":ldap_user_uuid, "ldap_group_cn":ldap_group_cn} if {
#    user_dn = data.ldap.users[user_idx].dn
#    ldap_group_dn := data.ldap.groups[group_idx].attributes.dn
#    ldap_user_uuid = data.ldap.users[user_idx].attributes.entryUUID[_]
#    user_dn in membership_recursive[ldap_group_dn]
#    ldap_group_cn := data.ldap.groups[group_idx].attributes.cn[_]
#    data.ldap.groups[group_idx].attributes.member[_] = user_dn
#}