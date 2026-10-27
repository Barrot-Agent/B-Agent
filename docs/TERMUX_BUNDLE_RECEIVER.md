# Verified Termux bundle receiver

This receiver provides a deliberately narrow bridge between a trusted, immutable
Barrot bundle manifest in this repository and a local Termux inbox.

## What it does

- Fetches only HTTPS \`raw.githubusercontent.com\` URLs pinned to a 40-character commit SHA in
  \`Barrot-Agent/B-Agent/data/termux_bundles/<bundle-id>.json\`.
- Requires an independently supplied expected SHA-256 for the decoded bundle payload.
- Validates the manifest schema, bundle ID, filename, base64 payload, and size limits.
- Restricts the destination to a subdirectory of the current home directory.
- Creates the final filename atomically without overwriting an existing path.
- Prints a JSON receipt with the destination, payload hash, byte count, timestamp,
  and explicit \`executed=false\` / \`git_modified=false\` fields.

## What it does not do

- It does not execute bundle contents.
- It does not run queued shell commands.
- It does not pull, commit, or push Git changes.
- It does not claim that a cloud task has access to the physical phone.
- It does not replace Barrot's existing local \`TERMUX_DROP\` / \`DELIVER_BUNDLE\` actions. Those
  actions write to the filesystem of the process executing them; a cloud workspace
  is not the same filesystem as a phone.

## Invocation

Use a manifest URL pinned to the reviewed commit that contains the manifest, plus
the expected SHA-256 copied from a trusted handoff:

\`\`\`bash
python scripts/termux_bundle_receiver.py \\
  --manifest-url 'https://raw.githubusercontent.com/Barrot-Agent/B-Agent/<commit-sha>/data/termux_bundles/<bundle-id>.json' \\
  --expected-sha256 '<64-character-payload-sha256>'
\`\`\`

The default destination is \`$HOME/barrot/Barrot-Agent/.barrot/inbox\`. Use \`--destination\` to select
another subdirectory of \`$HOME\`. Review the JSON receipt and inspect the received
file before using it. Never execute an unreviewed bundle.

The committed \`probe-20261027\` manifest is a harmless JSON data file for verifying the
transport. Its contents are not a shell script and are not intended to be executed.

## Tests

\`\`\`bash
python -m pytest tests/test_termux_bundle_receiver.py -q
\`\`\`

The tests use a mocked HTTP response and do not require external network access.
