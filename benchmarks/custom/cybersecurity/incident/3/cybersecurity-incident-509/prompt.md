# Intrusion timeline: pick the hypothesis, cite the evidence (static analysis)

Reconstruct the intrusion using ONLY `resources/timeline.csv` (60 events:
`event_id,timestamp,host,type,detail`). Do NOT probe any host, touch any
network, or detonate any payload; this is a frozen-paper exercise.

## Candidate hypotheses (exactly one is fully supported)

* **H1:** phishing email attachment -> macro payload on WS-042 -> SMB lateral
  movement WS-042 to SRV-DB-01 -> bulk HTTPS exfiltration to an external host.
* **H2:** RDP brute-force from outside -> credential dump -> DNS-tunnel
  exfiltration.
* **H3:** trojanized vendor update -> scheduled-task persistence -> cloud-sync
  exfiltration.

## Rules

* Cite the SINGLE event ID that best evidences each stage: the initial-access
  vector (`initial`), the lateral-movement step (`lateral`), and the
  exfiltration flow (`exfil`).
* Failed only / refuted leads do not count: RDP attempts never succeed, the
  vendor patch hash matches published clean, cloud sync is small and
  DLP-logged, the USB shows no writes.
* Correlation beats volume: prefer the event whose detail shows the actual
  malicious mechanism (first-ever admin path, bulk external POST) over routine
  noise on the same hosts.

## Deliverable

Emit as the LAST non-empty line of your response:

```
FINAL: hypothesis=<H1|H2|H3> initial=<E###> lateral=<E###> exfil=<E###>
```
