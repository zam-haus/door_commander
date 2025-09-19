package app.door_commander.sidecar.ldap_export_test


import data.app.door_commander.sidecar.ldap_export.door_entry_uuid_mapping
import data.app.door_commander.sidecar.ldap_export.door_uuid_card_id_mapping



test_direct_membership if {
    # "ED9AE67F-0779-4248-AE46-0167791A73AF" : ["MayOpenNordUG"],
    # "MayOpenNordUG" : ["zugangsberechtigt_nord_ug",],
    # "entryUUID": [
          #          "dfb835dc-e8a5-103f-9f86-7d53f788cc3b"
          #        ],
          #        "memberOf": [
          #          "cn=mitglied,ou=groups,dc=betreiberverein,dc=de",
          #          "cn=zugangsberechtigt_nord_eg,ou=groups,dc=betreiberverein,dc=de",
          #          "cn=zugangsberechtigt_nord_ug,ou=groups,dc=betreiberverein,dc=de"
          #        ],

    "dfb835dc-e8a5-103f-9f86-7d53f788cc3b" in door_entry_uuid_mapping["ED9AE67F-0779-4248-AE46-0167791A73AF"] with input as {} with data.ldap as demo_ldap_data
}
test_recursive_membership if {
    # "D6545C11-CC5A-421E-9D7D-0B2F762C6282" : ["MayOpenFrontDoor"],
    #  "MayOpenFrontDoor" : ["zugangsberechtigt",],
    # "entryUUID": [
          #          "dfb835dc-e8a5-103f-9f86-7d53f788cc3b"
          #        ],
          #        "memberOf": [
          #          "cn=mitglied,ou=groups,dc=betreiberverein,dc=de",
          #          "cn=zugangsberechtigt_nord_eg,ou=groups,dc=betreiberverein,dc=de",
          #          "cn=zugangsberechtigt_nord_ug,ou=groups,dc=betreiberverein,dc=de"
          #        ],

    "dfb835dc-e8a5-103f-9f86-7d53f788cc3b" in door_entry_uuid_mapping["D6545C11-CC5A-421E-9D7D-0B2F762C6282"] with input as {} with data.ldap as demo_ldap_data
}


test_door_card_direct if {
    "0c8cb58c30dd45f4a17fd98655001f6d804c1b7dadaf146c92e3bfe48986792f" in door_uuid_card_id_mapping["ED9AE67F-0779-4248-AE46-0167791A73AF"] with input as {} with data.ldap as demo_ldap_data with data.django as demo_django_data
}
test_door_card_recursive if {
    "0c8cb58c30dd45f4a17fd98655001f6d804c1b7dadaf146c92e3bfe48986792f" in door_uuid_card_id_mapping["D6545C11-CC5A-421E-9D7D-0B2F762C6282"] with input as {} with data.ldap as demo_ldap_data with data.django as demo_django_data
}








#For secret card IDs: head -c 32 /dev/random | xxd -p -c0
demo_django_data:={
    "doors": {
      "027116de-f78a-4e75-8c4e-28b12e974de0": {
        "door": {
          "fields": {
            "button_color": "#60b177",
            "display_name": "asdf",
            "mqtt_id": "f8d0405e-dbf4-4992-b23e-e9ad3d956497",
            "order": 42,
            "text_color": "#ffffff"
          },
          "model": "doors.door",
          "pk": "027116de-f78a-4e75-8c4e-28b12e974de0"
        }
      },
      "62be052c-bc70-4397-ab66-b3ac5fa7709a": {
        "door": {
          "fields": {
            "button_color": "#60b177",
            "display_name": "A2",
            "mqtt_id": "4f7594a6-998f-4ed2-9dd0-973527715b40",
            "order": 42,
            "text_color": "#ffffff"
          },
          "model": "doors.door",
          "pk": "62be052c-bc70-4397-ab66-b3ac5fa7709a"
        }
      },
      "d4e8db1e-5c04-43d4-b38a-152deb639e14": {
        "door": {
          "fields": {
            "button_color": "#60b177",
            "display_name": "B",
            "mqtt_id": "5a281f7f-1e25-41d6-b15b-d068b4bcfcad",
            "order": 42,
            "text_color": "#ffffff"
          },
          "model": "doors.door",
          "pk": "d4e8db1e-5c04-43d4-b38a-152deb639e14"
        }
      }
    },
    "users": {
      "5ba82218-7449-4ecc-9c97-20c428b8ee17": {
        "cards": [
          {
            "fields": {
              "created_at": "2025-06-24T18:06:44.382Z",
              "disabled": false,
              "last_used_at": "2025-06-28T20:45:39Z",
              "owner": "5ba82218-7449-4ecc-9c97-20c428b8ee17",
              "secret_id": "1",
              "updated_at": "2025-06-28T20:45:43.230Z"
            },
            "model": "cards.card",
            "pk": "e9b9b3e9-865a-4fb7-ba29-1a54c9a26dd0"
          },
          {
            "fields": {
              "created_at": "2025-06-28T20:45:50.422Z",
              "disabled": false,
              "last_used_at": "2025-06-28T20:51:48Z",
              "owner": "5ba82218-7449-4ecc-9c97-20c428b8ee17",
              "secret_id": "2",
              "updated_at": "2025-06-28T20:51:49.817Z"
            },
            "model": "cards.card",
            "pk": "6d832a55-57da-46b4-87ae-a31ef7af71af"
          }
        ],
        "connections": [],
        "permissions": [],
        "user": {
          "fields": {
            "date_joined": "2025-05-30T08:35:38.674Z",
            "display_name": "",
            "email": "",
            "full_name": "",
            "groups": [],
            "is_active": true,
            "is_staff": true,
            "is_superuser": true,
            "last_login": "2025-06-28T20:29:14.490Z",
            "password": "pbkdf2_sha256$1000000$hhE6uZ49CTpe2OjGITsk0I$hiwf2ZQK+JbwoMxIM1ivLzTG31NV5CQ9eSckIPFOlLw=",
            "password_last_changed": "2025-05-30T08:35:38.674Z",
            "user_permissions": [],
            "username": "admin"
          },
          "model": "accounts.user",
          "pk": "5ba82218-7449-4ecc-9c97-20c428b8ee17"
        }
      },
      "6234b01a-69f7-40c4-b998-2bb32ee4d90f": {
        "cards": [],
        "connections": [
          {
            "fields": {
              "directory": "3a01ea23-4a7f-4c64-adce-02411cd0a480",
              "directory_key": "9203104e-dfe2-103f-8932-0b11cff0efd2",
              "latest_directory_data": null,
              "user": "6234b01a-69f7-40c4-b998-2bb32ee4d90f"
            },
            "model": "accounts.userconnection",
            "pk": "42e8811a-a6b6-465e-b498-3570e2096cf5"
          }
        ],
        "permissions": [],
        "user": {
          "fields": {
            "date_joined": "2025-06-18T16:34:55.659Z",
            "display_name": "",
            "email": "",
            "full_name": "",
            "groups": [],
            "is_active": true,
            "is_staff": false,
            "is_superuser": false,
            "last_login": null,
            "password": "!",
            "password_last_changed": "2025-06-18T16:34:55.665Z",
            "user_permissions": [],
            "username": "JDoe"
          },
          "model": "accounts.user",
          "pk": "6234b01a-69f7-40c4-b998-2bb32ee4d90f"
        }
      },
      "9aaa538f-c97b-46dd-950c-7ed5c1de61e0": {
        "cards": [],
        "connections": [
          {
            "fields": {
              "directory": "3a01ea23-4a7f-4c64-adce-02411cd0a480",
              "directory_key": "9203f3f6-dfe2-103f-8933-0b11cff0efd2",
              "latest_directory_data": null,
              "user": "9aaa538f-c97b-46dd-950c-7ed5c1de61e0"
            },
            "model": "accounts.userconnection",
            "pk": "5c0eb36e-3688-4176-83bc-153130760d71"
          }
        ],
        "permissions": [],
        "user": {
          "fields": {
            "date_joined": "2025-06-17T16:52:25.988Z",
            "display_name": "",
            "email": "",
            "full_name": "",
            "groups": [],
            "is_active": true,
            "is_staff": false,
            "is_superuser": false,
            "last_login": null,
            "password": "!",
            "password_last_changed": "2025-06-17T16:52:26.004Z",
            "user_permissions": [],
            "username": "ASmith"
          },
          "model": "accounts.user",
          "pk": "9aaa538f-c97b-46dd-950c-7ed5c1de61e0"
        }
      },
      "ee2de350-0fec-47e2-8711-aaa32d827be8": {
        "cards": [
          {
            "fields": {
              "created_at": "2025-06-28T20:51:54.583Z",
              "disabled": false,
              "last_used_at": "2025-06-28T20:51:53Z",
              "owner": "ee2de350-0fec-47e2-8711-aaa32d827be8",
              "secret_id": "0c8cb58c30dd45f4a17fd98655001f6d804c1b7dadaf146c92e3bfe48986792f",
              "updated_at": "2025-06-28T20:51:54.593Z"
            },
            "model": "cards.card",
            "pk": "a396eb5c-998b-490f-9eae-22c52d34c46b"
          },
          {
            "fields": {
              "created_at": "2025-06-28T20:51:59.937Z",
              "disabled": false,
              "last_used_at": "2025-06-28T20:51:57Z",
              "owner": "ee2de350-0fec-47e2-8711-aaa32d827be8",
              "secret_id": "08a20dd5bc22805e9d22c9551df060cd95fef55be6466fe6a1c40dddbbb79efd",
              "updated_at": "2025-06-28T20:51:59.953Z"
            },
            "model": "cards.card",
            "pk": "d5e474b3-ad99-4a76-b65f-4d109eb490ef"
          }
        ],
        "connections": [
          {
            "fields": {
              "directory": "3a01ea23-4a7f-4c64-adce-02411cd0a480",
              "directory_key": "81499544-54e2-11f0-9c3d-3f7d8a9ff79e",
              "latest_directory_data": {},
              "user": "ee2de350-0fec-47e2-8711-aaa32d827be8"
            },
            "model": "accounts.userconnection",
            "pk": "1f586182-56e1-443e-9003-fcda41c416d1"
          },
          {
            "fields": {
              "directory": "333e9776-e0a8-4b62-8966-0b81d7ae3b48",
              "directory_key": "dfb835dc-e8a5-103f-9f86-7d53f788cc3b",
              "latest_directory_data": null,
              "user": "ee2de350-0fec-47e2-8711-aaa32d827be8"
            },
            "model": "accounts.userconnection",
            "pk": "b37f4058-cdfa-4286-9263-01a789b9ca4e"
          }
        ],
        "permissions": [
          {
            "fields": {
              "codename": "open_door",
              "content_type": 6,
              "name": "Can open any door"
            },
            "model": "auth.permission",
            "pk": 25
          }
        ],
        "user": {
          "fields": {
            "date_joined": "2025-06-15T02:15:26.543Z",
            "display_name": "User",
            "email": "mail@example.com",
            "full_name": "User",
            "groups": [],
            "is_active": true,
            "is_staff": true,
            "is_superuser": true,
            "last_login": "2025-06-28T20:51:38.259Z",
            "password": "!",
            "password_last_changed": "2025-06-15T02:15:26.543Z",
            "user_permissions": [
              25
            ],
            "username": "User"
          },
          "model": "accounts.user",
          "pk": "ee2de350-0fec-47e2-8711-aaa32d827be8"
        }
      }
    }
  }


















demo_ldap_data := {
  "groups": [
    {
      "attributes": {
        "cn": [
          "emptygroup"
        ],
        "entryUUID": [
          "dfba0df8-e8a5-103f-9f88-7d53f788cc3b"
        ],
        "memberOf": [],
        "objectClass": [
          "groupOfUniqueNames"
        ],
        "uniqueMember": [
          "cn=empty-membership-placeholder"
        ]
      },
      "dn": "cn=emptygroup,ou=groups,dc=betreiberverein,dc=de"
    },
    {
      "attributes": {
        "cn": [
          "mitglied"
        ],
        "entryUUID": [
          "dfba8120-e8a5-103f-9f89-7d53f788cc3b"
        ],
        "memberOf": [],
        "objectClass": [
          "groupOfUniqueNames"
        ],
        "uniqueMember": [
          "uid=user1,ou=users,dc=betreiberverein,dc=de",
          "uid=user2,ou=users,dc=betreiberverein,dc=de"
        ]
      },
      "dn": "cn=mitglied,ou=groups,dc=betreiberverein,dc=de"
    },
    {
      "attributes": {
        "cn": [
          "zugangsberechtigt_nord_eg"
        ],
        "entryUUID": [
          "dfbbae38-e8a5-103f-9f8a-7d53f788cc3b"
        ],
        "memberOf": [
          "cn=zugangsberechtigt,ou=groups,dc=betreiberverein,dc=de"
        ],
        "objectClass": [
          "groupOfUniqueNames"
        ],
        "uniqueMember": [
          "uid=user1,ou=users,dc=betreiberverein,dc=de",
          "uid=user2,ou=users,dc=betreiberverein,dc=de"
        ]
      },
      "dn": "cn=zugangsberechtigt_nord_eg,ou=groups,dc=betreiberverein,dc=de"
    },
    {
      "attributes": {
        "cn": [
          "zugangsberechtigt_nord_ug"
        ],
        "entryUUID": [
          "dfbcc0ac-e8a5-103f-9f8b-7d53f788cc3b"
        ],
        "memberOf": [
          "cn=zugangsberechtigt,ou=groups,dc=betreiberverein,dc=de"
        ],
        "objectClass": [
          "groupOfUniqueNames"
        ],
        "uniqueMember": [
          "uid=user1,ou=users,dc=betreiberverein,dc=de"
        ]
      },
      "dn": "cn=zugangsberechtigt_nord_ug,ou=groups,dc=betreiberverein,dc=de"
    },
    {
      "attributes": {
        "cn": [
          "zugangsberechtigt"
        ],
        "entryUUID": [
          "dfbd7b3c-e8a5-103f-9f8c-7d53f788cc3b"
        ],
        "memberOf": [],
        "objectClass": [
          "groupOfUniqueNames"
        ],
        "uniqueMember": [
          "cn=zugangsberechtigt_nord_eg,ou=groups,dc=betreiberverein,dc=de",
          "cn=zugangsberechtigt_nord_ug,ou=groups,dc=betreiberverein,dc=de"
        ]
      },
      "dn": "cn=zugangsberechtigt,ou=groups,dc=betreiberverein,dc=de"
    }
  ],
  "users": [
    {
      "attributes": {
        "cn": [
          "Vorname1"
        ],
        "entryUUID": [
          "dfb835dc-e8a5-103f-9f86-7d53f788cc3b"
        ],
        "memberOf": [
          "cn=mitglied,ou=groups,dc=betreiberverein,dc=de",
          "cn=zugangsberechtigt_nord_eg,ou=groups,dc=betreiberverein,dc=de",
          "cn=zugangsberechtigt_nord_ug,ou=groups,dc=betreiberverein,dc=de"
        ],
        "objectClass": [
          "inetOrgPerson",
          "organizationalPerson"
        ],
        "uid": [
          "user1"
        ]
      },
      "dn": "uid=user1,ou=users,dc=betreiberverein,dc=de"
    },
    {
      "attributes": {
        "cn": [
          "Vorname2"
        ],
        "entryUUID": [
          "dfb9395a-e8a5-103f-9f87-7d53f788cc3b"
        ],
        "memberOf": [
          "cn=mitglied,ou=groups,dc=betreiberverein,dc=de",
          "cn=zugangsberechtigt_nord_eg,ou=groups,dc=betreiberverein,dc=de"
        ],
        "objectClass": [
          "inetOrgPerson",
          "organizationalPerson"
        ],
        "uid": [
          "user2"
        ]
      },
      "dn": "uid=user2,ou=users,dc=betreiberverein,dc=de"
    }
  ]
}
