# RBAC audit with inheritance and deny-override (static analysis)

Decide 30 access requests using ONLY `resources/policy.json` (roles, users,
permissions) and `resources/requests.csv`. Do NOT contact any directory,
IAM service, or network; evaluate the shipped files only.

## Evaluation semantics

* A role's *closure* is itself plus every role reachable via `inherits`,
  transitively. A user with several roles unions all their closures.
* A permission rule matches a request when its `role` is in the user's closure
  AND its `action` and `resource` both equal the request's.
* **Deny-override:** if any matching rule has effect `deny`, the decision is
  `deny`, even when an `allow` also matches.
* **Default deny:** with no matching rule at all, the decision is `deny`.
* Inheritance flows downward only (child gains parent rules, never the reverse).

## Deliverable

Emit as the LAST non-empty line of your response:

```
FINAL: allowed=<int> denied=<int> r017=<allow|deny>
```

where `allowed`/`denied` cover all 30 requests and `r017` is the ruling for
request `R-017`.
