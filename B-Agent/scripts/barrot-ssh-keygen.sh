#!/bin/bash
# ΔΩ.110 — Barrot SSH Key Generator
KEY_TYPE="ed25519"
EMAIL="$1"
KEYNAME="id${KEY_TYPE}barrot"
KEYPATH="$HOME/.ssh/$KEYNAME"

# Generate SSH key
ssh-keygen -t $KEY_TYPE -C "$EMAIL" -f "$KEYPATH" -N ""

# Start ssh-agent and add key
eval "$(ssh-agent -s)"
ssh-add "$KEYPATH"

# Output public key
echo "----- Barrot SSH Public Key -----"
cat "${KEYPATH}.pub"
echo "---------------------------------"
