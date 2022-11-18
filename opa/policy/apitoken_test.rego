package app.door_commander.apitoken

#import future.keywords

input_data := {
    "token_data":{
        "id": "b9f6e25a-9e10-434a-8c27-38c5675e7db0",
        "serial": 2
    },
}

signed_input_data_token = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJpZCI6ICJiOWY2ZTI1YS05ZTEwLTQzNGEtOGMyNy0zOGM1Njc1ZTdkYjAiLCAic2VyaWFsIjogMn0.sYukIM6JjwzyixJYLyh97KEyQadtWY4qovPDE8B66aI"

input_token := {
    "token":"eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJpZCI6ICJiOWY2ZTI1YS05ZTEwLTQzNGEtOGMyNy0zOGM1Njc1ZTdkYjAiLCAic2VyaWFsIjogMn0.sYukIM6JjwzyixJYLyh97KEyQadtWY4qovPDE8B66aI"
}

input_token_wrongsig := {
    "token":"eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJpZCI6ICJiOWY2ZTI1YS05ZTEwLTQzNGEtOGMyNy0zOGM1Njc1ZTdkYjAiLCAic2VyaWFsIjogMn0.XXXXXXXX"
}

# ----

test_decode_sign_token {
    token == signed_input_data_token
        with input as input_data
}

test_decode_sign_token_empty {
    not token with input as {}
}

test_decode_verify_token_decoded_token {
    token_valid with input as input_token
    payload := decoded_payload with input as input_token
    token := decoded_token with input as input_token
    payload
    token
    [_,payload,_] = token
    {"id": id, "serial": serial} := payload
    id == "b9f6e25a-9e10-434a-8c27-38c5675e7db0"
    serial == 2
}

test_decode_verify_token_decoded_token_no_input {
    not token_valid with input as {}
    not decoded_payload with input as {}
    not decoded_token with input as {}
}

test_decode_verify_token_decoded_token_wrongsig {
    not token_valid with input as input_token_wrongsig
    not decoded_payload with input as input_token_wrongsig
    not decoded_token with input as input_token_wrongsig
}

test_decode_verify_token_valid {
    token_valid with input as input_token
}