package app.door_commander.common

# maps door UUIDs to role claim names nonrecursively
door_role_mapping = {
    "D6545C11-CC5A-421E-9D7D-0B2F762C6282" : ["MayOpenFrontDoor"],
    "2AB91A7B-26D5-4429-A2B8-9EE1C4DC1FC3" : ["MayOpenFrontDoor"],
    "T-S1-10" : ["MayOpenFrontDoor"],
    "ED9AE67F-0779-4248-AE46-0167791A73AF" : ["MayOpenNordUG"],
    "0f572bcc-d9bb-4ea1-b03a-1d72cb3175db" : ["MayOpenNordUG"],
    "80a60bda-98b9-4041-ac58-f70496dc9a10" : ["MayOpenNordUG"],
    "C840743E-F562-4DAC-8AEE-0622F000DCCF" : ["MayOpenNordEG"],
    "b44db1f1-1acd-4997-819a-5634f6bc4481" : ["MayOpenNordEG"],
    "metallwerkstatt-schraubenlager": ["MayOpenMetall"],
    "9812ae76-fd9d-48dc-b492-d30cbc46880f": ["MayOpenMetall"],
    "7c715f15-c61a-4b49-830d-04ce48d9b434": ["MayOpenPrototypen"],
    "da31685a-7e94-4ed0-9527-6f24820a7d3f": ["MayOpenPrototypen"],
    "60491a3f-05dd-48b4-88cc-a0ebab057ae6": ["MayOpenDruckTextil"],
}

# maps role claim names to group CNs
role_group_mapping = {
    "MayOpenFrontDoor" : ["zugangsberechtigt",],
    "MayOpenNordUG" : ["zugangsberechtigt_nord_ug",],
    "MayOpenNordEG" : ["zugangsberechtigt_nord_eg",],
    "MayOpenMetall": ["zugangsberechtigt_metallwerkstatt",],
}
