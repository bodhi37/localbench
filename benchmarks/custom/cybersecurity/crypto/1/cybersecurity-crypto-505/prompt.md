# Single-byte XOR recovery (static analysis)

The shipped file `resources/cipher.hex` holds one line: the hex encoding of a
ciphertext. It was produced by XOR-ing the UTF-8 bytes of an ASCII plaintext
with ONE repeated key byte. Do NOT contact any network or service; analyze the
shipped file only.

## Known crib (given, no guessing needed)

The plaintext begins with exactly:

```
CTF{static-xor-101:
```

Recover the key byte as `ciphertext[0] XOR crib[0]` and confirm it decrypts
every crib position consistently. Decrypt the full ciphertext, then compute the
SHA-256 hex digest (lowercase) of the raw decrypted bytes and their length.

## Deliverable

Emit as the LAST non-empty line of your response:

```
FINAL: key=<2 lowercase hex> plaintext_sha256=<64 lowercase hex> pt_len=<int>
```
