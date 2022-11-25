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
        "k": replace(base64.encode(opa.runtime().env.OPA_APITOKEN_SECRET),"=","")
    })

default secret_is_present = false
secret_is_present {
    opa.runtime().env.OPA_APITOKEN_SECRET
}
# https://github.com/open-policy-agent/opa/pull/2885/commits/a643f5af2255d28cfaf034cd3134d6af3304e28f
# https://github.com/open-policy-agent/opa/issues/2870
# https://github.com/open-policy-agent/opa/pull/2885
# do not encode the secret with base64 correctly, OPA does not accept
# encode_no_pad is only available in an older version, we use string replace instead
#secret := opa.runtime().env.OPA_APITOKEN_SECRET
#secret_encoded := base64.encode_no_pad(opa.runtime().env.OPA_APITOKEN_SECRET)
