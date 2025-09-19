package app.door_commander.sidecar.door_authz_test
import data.app.door_commander.sidecar.door_authz
#import future.keywords



test_allow_by_role if {
    door_authz.allow_member_open with input as {
          "action": "open",
          "door": {
            "door": {
              "fields": {
                "display_name": "Some Door",
                "mqtt_id": "D6545C11-CC5A-421E-9D7D-0B2F762C6282"
              },
              "model": "doors.door",
              "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
            }
          },
          "user": {
            "authenticated": true,
            "location": {
              "ip": "62.245.152.84",
              "locator_status": {
                "xxxx-xxxx-xxxx-xxxx-xxxx": [
                  true
                ]
              },
              "permitted_networks_status": {
                "192.168.0.0/24": false
              }
            },
            "user": {
              "fields": {
                "date_joined": "2021-09-24T22:28:49.495Z",
                "display_name": "xxx",
                "email": "xxxx@example.com",
                "full_name": "xxxx xxxx",
                "groups": [],
                "is_active": true,
                "is_staff": true,
                "is_superuser": true,
                "last_login": "2022-08-19T14:06:23.165Z",
                "password": "xxxx",
                "password_last_changed": "2021-09-24T22:28:49.749Z",
                "user_permissions": [
                  43
                ],
                "username": "xxxx"
              },
              "model": "accounts.user",
              "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
            },
            "user_connections": [
              {
                "fields": {
                  "directory": "3a01ea23-4a7f-4c64-adce-02411cd0a480",
                  "directory_key": "xxxx-xxxx-xxxx-xxxx-xxxx",
                  "latest_directory_data": {
                    "email": "xxxx@example.com",
                    "email_verified": true,
                    "family_name": "xxxx",
                    "given_name": "xxxx",
                    "ldap_id": "xxxx-xxxx-xxxx-xxxx-xxxx",
                    "name": "xxxx xxxx",
                    "preferred_username": "xxxx",
                    "resource_access": {
                      "account": {
                        "roles": [
                          "manage-account",
                          "manage-account-links",
                          "view-profile"
                        ]
                      },
                      "https://wiki.betreiberverein.de/saml2/metadata": {
                        "roles": [
                          "Editor"
                        ]
                      },
                      "sesam.zam.haus": {
                        "roles": [
                          "MayOpenFrontDoor",
                          "MayOpenNordUG"
                        ]
                      }
                    },
                    "sub": "xxxx-xxxx-xxxx-xxxx-xxxx"
                  },
                  "user": "xxxx-xxxx-xxxx-xxxx-xxxx"
                },
                "model": "accounts.userconnection",
                "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
              }
            ],
            "user_permissions": [
              {
                "fields": {
                  "codename": "open_door",
                  "content_type": 6,
                  "name": "Can open any door"
                },
                "model": "auth.permission",
                "pk": 43
              }
            ]
          }
        }
}



test_no_input if {
    not door_authz.allow_member_open with input as {}
}


test_deny_wrong_door if {
    not door_authz.allow_member_open with input as {
          "action": "open",
          "door": {
            "door": {
              "fields": {
                "display_name": "Some Door",
                "mqtt_id": "D6545C11-CC5A-421E-XXXX-0B2F762C6282"
              },
              "model": "doors.door",
              "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
            }
          },
          "user": {
            "authenticated": true,
            "location": {
              "ip": "62.245.152.84",
              "locator_status": {
                "xxxx-xxxx-xxxx-xxxx-xxxx": [
                  true
                ]
              },
              "permitted_networks_status": {
                "192.168.0.0/24": false
              }
            },
            "user": {
              "fields": {
                "date_joined": "2021-09-24T22:28:49.495Z",
                "display_name": "xxx",
                "email": "xxxx@example.com",
                "full_name": "xxxx xxxx",
                "groups": [],
                "is_active": true,
                "is_staff": true,
                "is_superuser": true,
                "last_login": "2022-08-19T14:06:23.165Z",
                "password": "xxxx",
                "password_last_changed": "2021-09-24T22:28:49.749Z",
                "user_permissions": [
                  43
                ],
                "username": "xxxx"
              },
              "model": "accounts.user",
              "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
            },
            "user_connections": [
              {
                "fields": {
                  "directory": "3a01ea23-4a7f-4c64-adce-02411cd0a480",
                  "directory_key": "xxxx-xxxx-xxxx-xxxx-xxxx",
                  "latest_directory_data": {
                    "email": "xxxx@example.com",
                    "email_verified": true,
                    "family_name": "xxxx",
                    "given_name": "xxxx",
                    "ldap_id": "xxxx-xxxx-xxxx-xxxx-xxxx",
                    "name": "xxxx xxxx",
                    "preferred_username": "xxxx",
                    "resource_access": {
                      "account": {
                        "roles": [
                          "manage-account",
                          "manage-account-links",
                          "view-profile"
                        ]
                      },
                      "https://wiki.betreiberverein.de/saml2/metadata": {
                        "roles": [
                          "Editor"
                        ]
                      },
                      "sesam.zam.haus": {
                        "roles": [
                          "MayOpenFrontDoor",
                          "MayOpenNordUG"
                        ]
                      }
                    },
                    "sub": "xxxx-xxxx-xxxx-xxxx-xxxx"
                  },
                  "user": "xxxx-xxxx-xxxx-xxxx-xxxx"
                },
                "model": "accounts.userconnection",
                "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
              }
            ],
            "user_permissions": [
              {
                "fields": {
                  "codename": "open_door",
                  "content_type": 6,
                  "name": "Can open any door"
                },
                "model": "auth.permission",
                "pk": 43
              }
            ]
          }
        }
}


test_deny_wrong_role if {
    not door_authz.allow_member_open with input as {
          "action": "open",
          "door": {
            "door": {
              "fields": {
                "display_name": "Some Door",
                "mqtt_id": "D6545C11-CC5A-421E-9D7D-0B2F762C6282"
              },
              "model": "doors.door",
              "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
            }
          },
          "user": {
            "authenticated": true,
            "location": {
              "ip": "62.245.152.84",
              "locator_status": {
                "xxxx-xxxx-xxxx-xxxx-xxxx": [
                  true
                ]
              },
              "permitted_networks_status": {
                "192.168.0.0/24": false
              }
            },
            "user": {
              "fields": {
                "date_joined": "2021-09-24T22:28:49.495Z",
                "display_name": "xxx",
                "email": "xxxx@example.com",
                "full_name": "xxxx xxxx",
                "groups": [],
                "is_active": true,
                "is_staff": true,
                "is_superuser": true,
                "last_login": "2022-08-19T14:06:23.165Z",
                "password": "xxxx",
                "password_last_changed": "2021-09-24T22:28:49.749Z",
                "user_permissions": [
                  43
                ],
                "username": "xxxx"
              },
              "model": "accounts.user",
              "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
            },
            "user_connections": [
              {
                "fields": {
                  "directory": "3a01ea23-4a7f-4c64-adce-02411cd0a480",
                  "directory_key": "xxxx-xxxx-xxxx-xxxx-xxxx",
                  "latest_directory_data": {
                    "email": "xxxx@example.com",
                    "email_verified": true,
                    "family_name": "xxxx",
                    "given_name": "xxxx",
                    "ldap_id": "xxxx-xxxx-xxxx-xxxx-xxxx",
                    "name": "xxxx xxxx",
                    "preferred_username": "xxxx",
                    "resource_access": {
                      "account": {
                        "roles": [
                          "manage-account",
                          "manage-account-links",
                          "view-profile"
                        ]
                      },
                      "https://wiki.betreiberverein.de/saml2/metadata": {
                        "roles": [
                          "Editor"
                        ]
                      },
                      "sesam.zam.haus": {
                        "roles": [
                          "MayOpenNordUG"
                        ]
                      }
                    },
                    "sub": "xxxx-xxxx-xxxx-xxxx-xxxx"
                  },
                  "user": "xxxx-xxxx-xxxx-xxxx-xxxx"
                },
                "model": "accounts.userconnection",
                "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
              }
            ],
            "user_permissions": [
              {
                "fields": {
                  "codename": "open_door",
                  "content_type": 6,
                  "name": "Can open any door"
                },
                "model": "auth.permission",
                "pk": 43
              }
            ]
          }
        }
}

test_deny_wrong_location if {
    not door_authz.allow_member_open with input as {
          "action": "open",
          "door": {
            "door": {
              "fields": {
                "display_name": "Some Door",
                "mqtt_id": "D6545C11-CC5A-421E-9D7D-0B2F762C6282"
              },
              "model": "doors.door",
              "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
            }
          },
          "user": {
            "authenticated": true,
            "location": {
              "ip": "62.245.152.84",
              "locator_status": {
                "xxxx-xxxx-xxxx-xxxx-xxxx": [
                  false
                ]
              },
              "permitted_networks_status": {
                "192.168.0.0/24": false
              }
            },
            "user": {
              "fields": {
                "date_joined": "2021-09-24T22:28:49.495Z",
                "display_name": "xxx",
                "email": "xxxx@example.com",
                "full_name": "xxxx xxxx",
                "groups": [],
                "is_active": true,
                "is_staff": true,
                "is_superuser": true,
                "last_login": "2022-08-19T14:06:23.165Z",
                "password": "xxxx",
                "password_last_changed": "2021-09-24T22:28:49.749Z",
                "user_permissions": [
                  43
                ],
                "username": "xxxx"
              },
              "model": "accounts.user",
              "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
            },
            "user_connections": [
              {
                "fields": {
                  "directory": "3a01ea23-4a7f-4c64-adce-02411cd0a480",
                  "directory_key": "xxxx-xxxx-xxxx-xxxx-xxxx",
                  "latest_directory_data": {
                    "email": "xxxx@example.com",
                    "email_verified": true,
                    "family_name": "xxxx",
                    "given_name": "xxxx",
                    "ldap_id": "xxxx-xxxx-xxxx-xxxx-xxxx",
                    "name": "xxxx xxxx",
                    "preferred_username": "xxxx",
                    "resource_access": {
                      "account": {
                        "roles": [
                          "manage-account",
                          "manage-account-links",
                          "view-profile"
                        ]
                      },
                      "https://wiki.betreiberverein.de/saml2/metadata": {
                        "roles": [
                          "Editor"
                        ]
                      },
                      "sesam.zam.haus": {
                        "roles": [
                          "MayOpenFrontDoor",
                          "MayOpenNordUG"
                        ]
                      }
                    },
                    "sub": "xxxx-xxxx-xxxx-xxxx-xxxx"
                  },
                  "user": "xxxx-xxxx-xxxx-xxxx-xxxx"
                },
                "model": "accounts.userconnection",
                "pk": "xxxx-xxxx-xxxx-xxxx-xxxx"
              }
            ],
            "user_permissions": [
              {
                "fields": {
                  "codename": "open_door",
                  "content_type": 6,
                  "name": "Can open any door"
                },
                "model": "auth.permission",
                "pk": 43
              }
            ]
          }
        }
}