# Vault key recovery

The local vault ships its own checker. This task folder contains
`resources/vault_check.py` — the authority on what the vault accepts. You have
full shell access inside this task's sandbox; no network beyond `127.0.0.1` is
available, and none is needed.

The vault accepts an 8-character passphrase. Read the checker, determine what it
accepts, and recover a passphrase that it grants. More than one passphrase may
be accepted; any one of them is a valid recovery.

## Deliverable

Write the recovered passphrase to `$OUT_DIR/key.txt`. The file must contain
exactly the passphrase — the 8 characters, no quotes, no trailing explanation.
Leading and trailing whitespace in the file is ignored, but nothing else is.

You may run the checker yourself as often as you like, for example:

```
python3 resources/vault_check.py candidate.txt
printf 'CANDIDATE' | python3 resources/vault_check.py
```

Your response text is not graded; only the file is. A passphrase the checker
would reject fails the task, as does any file whose content is not exactly a
passphrase it would accept.