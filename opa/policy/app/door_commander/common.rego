package app.door_commander.common

# maps door UUIDs to role claim names nonrecursively
door_role_mapping = {
    "D6545C11-CC5A-421E-9D7D-0B2F762C6282" : ["MayOpenFrontDoor"],
    "2AB91A7B-26D5-4429-A2B8-9EE1C4DC1FC3" : ["MayOpenFrontDoor"],
    "ED9AE67F-0779-4248-AE46-0167791A73AF" : ["MayOpenNordUG"],
    "C840743E-F562-4DAC-8AEE-0622F000DCCF" : ["MayOpenNordEG"],
    "b44db1f1-1acd-4997-819a-5634f6bc4481" : ["MayOpenNordEG"],
}

# maps role claim names to group CNs
role_group_mapping = {
    "MayOpenFrontDoor" : ["zugangsberechtigt",],
    "MayOpenNordUG" : ["zugangsberechtigt_nord_ug",],
    "MayOpenNordEG" : ["zugangsberechtigt_nord_eg",],
}
