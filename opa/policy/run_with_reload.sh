#!/usr/bin/env bash
export OPA_APITOKEN_SECRET=secret
ls *.rego | entr -r opa run -s *.rego