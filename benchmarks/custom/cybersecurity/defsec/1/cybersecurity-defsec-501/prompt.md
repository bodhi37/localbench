# Packet-filter audit

This task folder contains a packet filter and a sample of traffic:

* `resources/firewall.rules` — the filter, one rule per line, in evaluation
  order. Lines beginning with `#` are comments. Each rule line has six
  whitespace-separated fields:

  ```
  <rule_id> <action> <proto> <src_cidr> <dst_cidr> <dst_port>
  ```

  `<action>` is `accept` or `reject`; `<proto>` is `tcp` or `udp`; `<src_cidr>`
  and `<dst_cidr>` are IPv4 CIDR blocks; `<dst_port>` is either an integer port
  number or the literal token `any`.
* `resources/flows.csv` — observed connections, with header row
  `flow_id,proto,src,dst,dport`. `flow_id` has the form `F-` followed by three
  digits.

## Filter semantics

Rules are evaluated **in file order** and the **first** rule that matches a flow
decides it; later rules are never consulted for that flow. A rule matches a flow
when **all four** conditions hold:

1. the rule's `proto` equals the flow's `proto`;
2. the flow's `src` address lies inside the rule's `src_cidr` block;
3. the flow's `dst` address lies inside the rule's `dst_cidr` block;
4. the rule's `dst_port` is `any`, or equals the flow's `dport` exactly.

If **no** rule matches a flow, the flow is rejected by the implicit default
policy; report such a flow's deciding rule as `DEFAULT`.

## Report

* `accepted` — how many of the flows in the sample are accepted.
* `accepted_id_sum` — the sum of the numeric parts of the `flow_id`s of the
  accepted flows (for example, if `F-003` and `F-012` are the accepted flows,
  the sum is 3 + 12 = 15).
* `f017_rule` — the `<rule_id>` of the rule that decides flow `F-017`, or
  `DEFAULT` if the implicit default decides it.
* `f017_action` — that flow's resulting action, `accept` or `reject`.

End your response with a final line of exactly this form and nothing after it:

FINAL: accepted=<integer> accepted_id_sum=<integer> f017_rule=<rule id or DEFAULT> f017_action=<accept|reject>

The final line is the only part graded.