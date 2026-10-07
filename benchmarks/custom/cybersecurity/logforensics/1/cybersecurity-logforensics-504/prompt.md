# SSH auth-log forensics (static analysis)

Analyze ONLY the shipped file `resources/auth.log` (exactly 80 lines, 1-based
line numbers). Do NOT scan any network, host, or log source; treat the file as
a frozen, sanitized exhibit.

## Counting rules

* A *failed login* is any line containing the exact substring `Failed password`.
* A *success* for an IP is any line containing `Accepted password` whose
  `from <ip>` field equals that IP.
* Group failed logins by source IP (the address after `from `). The
  *brute-force IP* is the IP with the most failed logins. (There is a unique
  maximum; no tie-break is needed.)
* `first_success_line` is the 1-based line number in `resources/auth.log` of
  the first `Accepted password` line for the brute-force IP.

## Deliverable

Reason over the file, then emit as the LAST non-empty line of your response:

```
FINAL: total_failed=<int> top_ip=<ip> top_failed=<int> first_success_line=<int>
```

where `total_failed` counts every `Failed password` line in the file.
