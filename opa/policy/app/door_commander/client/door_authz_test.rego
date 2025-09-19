package app.door_commander.client.door_authz_test

import data.app.door_commander.client.door_authz


test_no_input_no_data if {
    not door_authz.allow with input as {} with data.ldap as {}
}