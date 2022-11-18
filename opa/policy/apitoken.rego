package app.door_commander.apitoken

token_valid := io.jwt.verify_hs256(input.token, opa.runtime().env.OPA_APITOKEN_SECRET)

decoded_token := (io.jwt.decode(input.token)) {token_valid}
decoded_payload := decoded_token[1]

token = io.jwt.encode_sign(
    {
        "typ": "JWT",
        "alg": "HS256"
    },
    input.token_data,
    {
        "kty": "oct",
        "k": base64.encode(opa.runtime().env.OPA_APITOKEN_SECRET)
    })
