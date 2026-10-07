# Timeline gap analysis

A monitor keeps a single event timeline. Every record line has exactly this
form:

```
EVT <4-digit id> | ts=<YYYY-MM-DDTHH:MM> | msg=<two words>
```

Lines that start with `TIMELINE` or `FORMAT` are header lines, not records.
Only lines that start with `EVT ` (with a trailing space) are records.

The record lines below are NOT in time order. Order the events by their
timestamps (all timestamps are distinct), then consider the gaps between
consecutive events in that time order. Exactly one such gap is strictly the
longest. Find the two events that bound it: the earlier event (`from`) and the
later event (`to`), and the gap length in whole minutes.

Timestamps compare chronologically, not as file positions: the neighbour of an
event in the file is usually not its neighbour in time.

## Timeline

```
TIMELINE MONITOR EVENTS - NOT IN TIME ORDER
FORMAT: EVT <4-digit id> | ts=<YYYY-MM-DDTHH:MM> | msg=<two words>

EVT 0092 | ts=2026-01-07T19:46 | msg=filter flange
EVT 0027 | ts=2026-01-02T23:10 | msg=beacon nozzle
EVT 0063 | ts=2026-01-05T06:05 | msg=filter switch
EVT 0010 | ts=2026-01-01T14:20 | msg=rotor cable
EVT 0096 | ts=2026-01-08T03:55 | msg=flange relay
EVT 0111 | ts=2026-01-09T01:20 | msg=yarn flange
EVT 0025 | ts=2026-01-02T19:41 | msg=beacon pump
EVT 0069 | ts=2026-01-06T01:49 | msg=pump vent
EVT 0044 | ts=2026-01-04T03:59 | msg=nozzle flange
EVT 0040 | ts=2026-01-03T21:33 | msg=vent gasket
EVT 0095 | ts=2026-01-08T02:56 | msg=sensor relay
EVT 0046 | ts=2026-01-04T09:08 | msg=panel valve
EVT 0021 | ts=2026-01-02T10:42 | msg=beacon hinge
EVT 0081 | ts=2026-01-07T00:25 | msg=intake switch
EVT 0144 | ts=2026-01-11T04:43 | msg=filter winch
EVT 0074 | ts=2026-01-06T13:04 | msg=turbine gasket
EVT 0137 | ts=2026-01-10T13:12 | msg=turbine gasket
EVT 0058 | ts=2026-01-04T23:52 | msg=vent turbine
EVT 0052 | ts=2026-01-04T18:01 | msg=cable winch
EVT 0117 | ts=2026-01-09T09:46 | msg=hinge winch
EVT 0016 | ts=2026-01-02T01:51 | msg=rotor nozzle
EVT 0018 | ts=2026-01-02T05:30 | msg=yarn vent
EVT 0115 | ts=2026-01-09T06:50 | msg=valve winch
EVT 0043 | ts=2026-01-04T01:11 | msg=switch gasket
EVT 0136 | ts=2026-01-10T11:53 | msg=switch beacon
EVT 0109 | ts=2026-01-08T20:54 | msg=rotor hinge
EVT 0085 | ts=2026-01-07T06:27 | msg=nozzle turbine
EVT 0077 | ts=2026-01-06T17:03 | msg=panel filter
EVT 0009 | ts=2026-01-01T13:07 | msg=yarn nozzle
EVT 0060 | ts=2026-01-05T01:22 | msg=relay sensor
EVT 0072 | ts=2026-01-06T09:18 | msg=pump vent
EVT 0039 | ts=2026-01-03T18:51 | msg=filter cable
EVT 0041 | ts=2026-01-03T21:57 | msg=flange hinge
EVT 0108 | ts=2026-01-08T19:33 | msg=panel cable
EVT 0054 | ts=2026-01-04T18:55 | msg=valve intake
EVT 0133 | ts=2026-01-10T09:36 | msg=gasket yarn
EVT 0007 | ts=2026-01-01T09:43 | msg=rotor panel
EVT 0001 | ts=2026-01-01T00:00 | msg=cable rotor
EVT 0138 | ts=2026-01-10T14:47 | msg=flange beacon
EVT 0142 | ts=2026-01-11T00:21 | msg=valve panel
EVT 0106 | ts=2026-01-08T16:38 | msg=switch sensor
EVT 0035 | ts=2026-01-03T11:10 | msg=winch gasket
EVT 0062 | ts=2026-01-05T03:37 | msg=vent winch
EVT 0019 | ts=2026-01-02T07:08 | msg=flange nozzle
EVT 0064 | ts=2026-01-05T06:21 | msg=valve winch
EVT 0135 | ts=2026-01-10T10:25 | msg=vent hinge
EVT 0103 | ts=2026-01-08T13:13 | msg=sensor gasket
EVT 0127 | ts=2026-01-10T00:14 | msg=beacon flange
EVT 0100 | ts=2026-01-08T08:43 | msg=vent hinge
EVT 0098 | ts=2026-01-08T06:36 | msg=flange flange
EVT 0011 | ts=2026-01-01T14:42 | msg=latch gasket
EVT 0024 | ts=2026-01-02T17:19 | msg=sensor flange
EVT 0125 | ts=2026-01-09T23:17 | msg=valve valve
EVT 0107 | ts=2026-01-08T18:25 | msg=switch relay
EVT 0065 | ts=2026-01-05T08:47 | msg=cable winch
EVT 0029 | ts=2026-01-03T04:31 | msg=relay latch
EVT 0143 | ts=2026-01-11T02:06 | msg=intake pump
EVT 0028 | ts=2026-01-03T01:35 | msg=intake relay
EVT 0122 | ts=2026-01-09T18:56 | msg=valve gasket
EVT 0057 | ts=2026-01-04T22:50 | msg=pump sensor
EVT 0087 | ts=2026-01-07T11:08 | msg=flange filter
EVT 0110 | ts=2026-01-08T22:58 | msg=rotor filter
EVT 0094 | ts=2026-01-08T00:32 | msg=gasket beacon
EVT 0149 | ts=2026-01-11T12:21 | msg=gasket valve
EVT 0104 | ts=2026-01-08T13:45 | msg=vent nozzle
EVT 0014 | ts=2026-01-01T22:10 | msg=turbine winch
EVT 0128 | ts=2026-01-10T03:12 | msg=rotor intake
EVT 0147 | ts=2026-01-11T10:08 | msg=panel hinge
EVT 0101 | ts=2026-01-08T10:59 | msg=switch turbine
EVT 0033 | ts=2026-01-03T09:34 | msg=valve cable
EVT 0118 | ts=2026-01-09T12:01 | msg=relay vent
EVT 0066 | ts=2026-01-05T22:47 | msg=turbine filter
EVT 0105 | ts=2026-01-08T15:43 | msg=beacon vent
EVT 0056 | ts=2026-01-04T21:52 | msg=winch pump
EVT 0030 | ts=2026-01-03T06:36 | msg=yarn gasket
EVT 0061 | ts=2026-01-05T02:59 | msg=intake turbine
EVT 0086 | ts=2026-01-07T09:21 | msg=nozzle hinge
EVT 0038 | ts=2026-01-03T17:31 | msg=yarn relay
EVT 0145 | ts=2026-01-11T07:13 | msg=rotor cable
EVT 0055 | ts=2026-01-04T20:10 | msg=rotor sensor
EVT 0091 | ts=2026-01-07T17:02 | msg=hinge intake
EVT 0089 | ts=2026-01-07T12:22 | msg=hinge filter
EVT 0015 | ts=2026-01-02T00:26 | msg=panel turbine
EVT 0032 | ts=2026-01-03T08:01 | msg=cable flange
EVT 0090 | ts=2026-01-07T14:36 | msg=sensor cable
EVT 0102 | ts=2026-01-08T12:19 | msg=relay cable
EVT 0123 | ts=2026-01-09T20:58 | msg=switch flange
EVT 0131 | ts=2026-01-10T07:16 | msg=panel relay
EVT 0114 | ts=2026-01-09T06:27 | msg=cable vent
EVT 0068 | ts=2026-01-06T01:34 | msg=latch sensor
EVT 0148 | ts=2026-01-11T11:00 | msg=panel filter
EVT 0026 | ts=2026-01-02T21:16 | msg=vent relay
EVT 0008 | ts=2026-01-01T10:45 | msg=turbine intake
EVT 0139 | ts=2026-01-10T16:21 | msg=rotor valve
EVT 0023 | ts=2026-01-02T15:01 | msg=beacon vent
EVT 0048 | ts=2026-01-04T11:46 | msg=intake rotor
EVT 0121 | ts=2026-01-09T16:05 | msg=switch latch
EVT 0017 | ts=2026-01-02T03:22 | msg=filter winch
EVT 0012 | ts=2026-01-01T17:21 | msg=turbine intake
EVT 0129 | ts=2026-01-10T04:59 | msg=cable beacon
EVT 0037 | ts=2026-01-03T15:40 | msg=relay vent
EVT 0088 | ts=2026-01-07T11:28 | msg=panel hinge
EVT 0004 | ts=2026-01-01T06:14 | msg=filter filter
EVT 0034 | ts=2026-01-03T09:52 | msg=filter sensor
EVT 0079 | ts=2026-01-06T21:30 | msg=beacon turbine
EVT 0073 | ts=2026-01-06T10:04 | msg=yarn nozzle
EVT 0059 | ts=2026-01-05T00:33 | msg=flange gasket
EVT 0050 | ts=2026-01-04T14:08 | msg=beacon winch
EVT 0049 | ts=2026-01-04T13:22 | msg=gasket hinge
EVT 0006 | ts=2026-01-01T08:52 | msg=intake winch
EVT 0084 | ts=2026-01-07T04:00 | msg=turbine hinge
EVT 0134 | ts=2026-01-10T09:55 | msg=rotor relay
EVT 0003 | ts=2026-01-01T04:08 | msg=relay winch
EVT 0082 | ts=2026-01-07T00:51 | msg=cable winch
EVT 0141 | ts=2026-01-10T21:29 | msg=relay winch
EVT 0124 | ts=2026-01-09T21:51 | msg=rotor nozzle
EVT 0031 | ts=2026-01-03T07:10 | msg=relay cable
EVT 0002 | ts=2026-01-01T01:38 | msg=beacon gasket
EVT 0042 | ts=2026-01-04T00:42 | msg=hinge nozzle
EVT 0036 | ts=2026-01-03T12:44 | msg=sensor yarn
EVT 0067 | ts=2026-01-06T00:40 | msg=pump intake
EVT 0112 | ts=2026-01-09T02:28 | msg=pump pump
EVT 0070 | ts=2026-01-06T04:34 | msg=pump flange
EVT 0078 | ts=2026-01-06T19:44 | msg=cable cable
EVT 0126 | ts=2026-01-09T23:47 | msg=winch pump
EVT 0146 | ts=2026-01-11T07:46 | msg=relay latch
EVT 0099 | ts=2026-01-08T08:24 | msg=latch hinge
EVT 0113 | ts=2026-01-09T05:05 | msg=cable rotor
EVT 0022 | ts=2026-01-02T12:54 | msg=valve cable
EVT 0045 | ts=2026-01-04T06:18 | msg=beacon winch
EVT 0116 | ts=2026-01-09T08:45 | msg=pump pump
EVT 0150 | ts=2026-01-11T14:00 | msg=relay flange
EVT 0051 | ts=2026-01-04T15:16 | msg=filter filter
EVT 0080 | ts=2026-01-06T23:32 | msg=relay filter
EVT 0083 | ts=2026-01-07T02:59 | msg=winch yarn
EVT 0132 | ts=2026-01-10T08:04 | msg=latch hinge
EVT 0005 | ts=2026-01-01T08:02 | msg=rotor winch
EVT 0047 | ts=2026-01-04T10:15 | msg=sensor valve
EVT 0020 | ts=2026-01-02T09:43 | msg=hinge gasket
EVT 0120 | ts=2026-01-09T15:50 | msg=hinge rotor
EVT 0119 | ts=2026-01-09T13:26 | msg=switch relay
EVT 0076 | ts=2026-01-06T15:16 | msg=intake relay
EVT 0075 | ts=2026-01-06T14:17 | msg=relay hinge
EVT 0093 | ts=2026-01-07T22:30 | msg=relay hinge
EVT 0013 | ts=2026-01-01T19:48 | msg=hinge flange
EVT 0071 | ts=2026-01-06T07:26 | msg=switch nozzle
EVT 0097 | ts=2026-01-08T04:44 | msg=latch sensor
EVT 0130 | ts=2026-01-10T06:29 | msg=gasket relay
EVT 0053 | ts=2026-01-04T18:26 | msg=rotor winch
EVT 0140 | ts=2026-01-10T18:53 | msg=filter flange
```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: from=<integer> to=<integer> gap_min=<integer>

* `from` is the EVT id of the earlier bounding event, as a base-10 integer
  (leading zeros are not significant).
* `to` is the EVT id of the later bounding event, as a base-10 integer.
* `gap_min` is the later timestamp minus the earlier timestamp, in whole
  minutes, as a base-10 integer.

The final line is the only part graded; anything else in your response is
ignored.
