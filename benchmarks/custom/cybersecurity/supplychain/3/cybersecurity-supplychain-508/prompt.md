# Minimal dependency upgrades (static supply-chain analysis)

Using ONLY the shipped files `resources/lock.json` (locked versions),
`resources/advisories.json` (each advisory: versions BELOW `fixed_in` of that
package are vulnerable), and `resources/pins.json`, compute the MINIMAL set of
package upgrades that clears every CRITICAL advisory. Do NOT fetch registries,
install, build, or contact any network; reason over the shipped files only.

## Constraints

* `pins.json` `exact` packages must keep their locked version exactly.
* `same_major: true` forbids crossing a major version (first component of
  `X.Y.Z` must not change for any package).
* An upgrade may only move a version forward (never downgrade).
* Minimal means the fewest packages; each critical advisory is cleared by
  upgrading its own package to at least `fixed_in` (same major).
* Non-critical (high/medium) advisories may be left residual; do NOT upgrade
  extra packages beyond the minimal critical-clearing set.

## Deliverable

Emit as the LAST non-empty line of your response:

```
FINAL: upgrades=<name==version,... sorted alphabetically, no spaces> residual_critical=<int> residual_high=<int>
```

`residual_*` counts advisories still applicable to the final versions. If no
upgrade were needed, write `upgrades=none`.
