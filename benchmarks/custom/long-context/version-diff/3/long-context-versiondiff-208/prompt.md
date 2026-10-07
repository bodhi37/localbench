# Specification version diff

A specification is restated in full at three versions. Each version section
starts with a header line (`SPEC v1`, `SPEC v2`, `SPEC v3`) followed by 40
clause lines, each of exactly this form:

```
C<two digits>: <eight words>
```

Only lines that start with `C` followed by two digits are clause lines; the
`SPEC` lines are section headers, not clauses. Within one version every clause
id `C01`..`C40` appears exactly once.

Clauses change between versions: some clauses were rewritten from v1 to v2,
and some (a different set) were rewritten from v2 to v3. Your task covers ONLY
the v2 -> v3 step: list the ids of the clauses whose text differs between the
`SPEC v2` section and the `SPEC v3` section. Clauses that changed from v1 to
v2 but are identical in v2 and v3 must NOT be listed. Clause comparison is
exact and case-sensitive on the full eight-word text.

## Specification

```
SPEC v1
C01: circuit onyx umbra larch fathom north fathom nickel
C02: opal thicket magnet saddle xenon onyx willow fjord
C03: jetty granite vortex vortex opal thicket yarrow heath
C04: yarrow fathom granite willow circuit quartz pumice cobalt
C05: lagoon xenon embark zephyr dorsal inlet umbra onyx
C06: juniper quartz nickel basalt fjord jetty dorsal lagoon
C07: zephyr embark saddle lagoon embark quartz opal umbra
C08: jetty fathom embark basalt dorsal umbra cobalt basalt
C09: circuit prairie cobalt north north quartz magnet cobalt
C10: fathom basalt dune dune jetty prairie embark magnet
C11: kiosk prairie meadow heath saddle embark inlet heath
C12: umbra kiosk quartz saddle ridge pumice thicket basalt
C13: fjord juniper iris onyx magnet dorsal kelp meadow
C14: circuit opal fjord cobalt cobalt basalt nickel prairie
C15: quartz xenon prairie iris umbra umbra embark pumice
C16: opal meadow opal fjord larch opal yarrow thicket
C17: fjord grove embark juniper heath magnet dorsal magnet
C18: quartz north north embark quartz quartz cobalt fathom
C19: opal north saddle embark ember inlet circuit dorsal
C20: heath larch quartz meadow inlet fathom fjord onyx
C21: quartz fjord pumice umbra heath fathom vortex kiosk
C22: harbor iris yarrow willow dorsal harbor kelp kiosk
C23: north circuit heath umbra zephyr cobalt thicket heath
C24: basalt nickel circuit saddle zephyr inlet zephyr juniper
C25: dorsal cobalt lagoon basalt umbra fathom jetty cobalt
C26: meadow dorsal prairie inlet basalt quartz dorsal umbra
C27: lagoon magnet circuit yarrow heath willow grove saddle
C28: iris opal embark grove amber meadow lagoon amber
C29: yarrow embark fathom juniper magnet larch juniper embark
C30: amber thicket cobalt grove willow ridge circuit opal
C31: kelp vortex dorsal granite zephyr willow north willow
C32: fjord onyx embark magnet thicket pumice meadow prairie
C33: amber prairie jetty dune kelp larch grove cobalt
C34: inlet ember embark kiosk jetty fathom umbra granite
C35: prairie jetty nickel grove pumice thicket inlet quartz
C36: harbor ember magnet prairie dune vortex granite onyx
C37: umbra dune dorsal iris nickel willow north zephyr
C38: larch kelp dune xenon kelp umbra lagoon xenon
C39: zephyr larch yarrow north thicket umbra inlet willow
C40: jetty ridge pumice heath basalt dorsal cobalt ember

SPEC v2
C01: circuit onyx umbra larch fathom north fathom nickel
C02: opal thicket magnet saddle xenon onyx willow fjord
C03: jetty granite vortex vortex opal thicket yarrow heath
C04: yarrow fathom granite willow circuit quartz pumice cobalt
C05: thicket heath pumice inlet meadow zephyr larch embark
C06: juniper quartz nickel basalt fjord jetty dorsal lagoon
C07: zephyr embark saddle lagoon embark quartz opal umbra
C08: jetty fathom embark basalt dorsal umbra cobalt basalt
C09: circuit prairie cobalt north north quartz magnet cobalt
C10: fathom basalt dune dune jetty prairie embark magnet
C11: kiosk prairie meadow heath saddle embark inlet heath
C12: granite ridge inlet cobalt juniper kiosk zephyr dorsal
C13: fjord juniper iris onyx magnet dorsal kelp meadow
C14: circuit opal fjord cobalt cobalt basalt nickel prairie
C15: quartz xenon prairie iris umbra umbra embark pumice
C16: opal meadow opal fjord larch opal yarrow thicket
C17: fjord grove embark juniper heath magnet dorsal magnet
C18: quartz north north embark quartz quartz cobalt fathom
C19: opal north saddle embark ember inlet circuit dorsal
C20: heath larch quartz meadow inlet fathom fjord onyx
C21: quartz fjord pumice umbra heath fathom vortex kiosk
C22: harbor iris yarrow willow dorsal harbor kelp kiosk
C23: north circuit heath umbra zephyr cobalt thicket heath
C24: basalt nickel circuit saddle zephyr inlet zephyr juniper
C25: dorsal cobalt lagoon basalt umbra fathom jetty cobalt
C26: meadow dorsal prairie inlet basalt quartz dorsal umbra
C27: fathom jetty opal inlet meadow kelp xenon cobalt
C28: iris opal embark grove amber meadow lagoon amber
C29: yarrow embark fathom juniper magnet larch juniper embark
C30: amber thicket cobalt grove willow ridge circuit opal
C31: kelp vortex dorsal granite zephyr willow north willow
C32: fjord onyx embark magnet thicket pumice meadow prairie
C33: quartz lagoon prairie heath yarrow amber xenon opal
C34: inlet ember embark kiosk jetty fathom umbra granite
C35: prairie jetty nickel grove pumice thicket inlet quartz
C36: harbor ember magnet prairie dune vortex granite onyx
C37: umbra dune dorsal iris nickel willow north zephyr
C38: larch kelp dune xenon kelp umbra lagoon xenon
C39: zephyr larch yarrow north thicket umbra inlet willow
C40: jetty ridge pumice heath basalt dorsal cobalt ember

SPEC v3
C01: circuit onyx umbra larch fathom north fathom nickel
C02: opal thicket magnet saddle xenon onyx willow fjord
C03: jetty granite vortex vortex opal thicket yarrow heath
C04: yarrow fathom granite willow circuit quartz pumice cobalt
C05: thicket heath pumice inlet meadow zephyr larch embark
C06: juniper quartz nickel basalt fjord jetty dorsal lagoon
C07: juniper kelp umbra fjord jetty magnet umbra fathom
C08: jetty fathom embark basalt dorsal umbra cobalt basalt
C09: circuit prairie cobalt north north quartz magnet cobalt
C10: fathom basalt dune dune jetty prairie embark magnet
C11: kiosk prairie meadow heath saddle embark inlet heath
C12: granite ridge inlet cobalt juniper kiosk zephyr dorsal
C13: fjord juniper iris onyx magnet dorsal kelp meadow
C14: circuit opal fjord cobalt cobalt basalt nickel prairie
C15: quartz xenon prairie iris umbra umbra embark pumice
C16: opal meadow opal fjord larch opal yarrow thicket
C17: fjord grove embark juniper heath magnet dorsal magnet
C18: quartz north north embark quartz quartz cobalt fathom
C19: larch circuit lagoon thicket thicket zephyr umbra ember
C20: heath larch quartz meadow inlet fathom fjord onyx
C21: quartz fjord pumice umbra heath fathom vortex kiosk
C22: harbor iris yarrow willow dorsal harbor kelp kiosk
C23: north circuit heath umbra zephyr cobalt thicket heath
C24: basalt nickel circuit saddle zephyr inlet zephyr juniper
C25: dorsal cobalt lagoon basalt umbra fathom jetty cobalt
C26: meadow dorsal prairie inlet basalt quartz dorsal umbra
C27: fathom jetty opal inlet meadow kelp xenon cobalt
C28: iris opal embark grove amber meadow lagoon amber
C29: yarrow embark fathom juniper magnet larch juniper embark
C30: amber thicket cobalt grove willow ridge circuit opal
C31: thicket thicket xenon onyx juniper magnet fathom yarrow
C32: fjord onyx embark magnet thicket pumice meadow prairie
C33: quartz lagoon prairie heath yarrow amber xenon opal
C34: inlet ember embark kiosk jetty fathom umbra granite
C35: prairie jetty nickel grove pumice thicket inlet quartz
C36: harbor ember magnet prairie dune vortex granite onyx
C37: umbra dune dorsal iris nickel willow north zephyr
C38: larch kelp dune xenon kelp umbra lagoon xenon
C39: zephyr larch yarrow north thicket umbra inlet willow
C40: jetty ridge pumice heath basalt dorsal cobalt ember

```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: changed=<C..>,<C..>,<C..>

* List every clause id whose v2 text differs from its v3 text, and no other id.
* Sort ascending (C07 before C19), separate with single commas, no spaces.
* Each id is the literal clause id exactly as it appears (e.g. `C07`).

The final line is the only part graded; anything else in your response is
ignored.
