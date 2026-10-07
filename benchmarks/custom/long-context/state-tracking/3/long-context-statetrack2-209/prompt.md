# Ledger with voids and corrections

A cash ledger starts at a balance of 50000 cents. Every ledger line has one of
these exact forms (`<id>` and `<target>` are 4-digit ids, amounts are bare
integer cents):

```
TX <id> | CREDIT amt=<cents> | memo=<word>
TX <id> | DEBIT amt=<cents> | memo=<word>
TX <id> | VOID <target> | memo=<word>
TX <id> | CORRECT <target> new=<cents> | memo=<word>
```

Lines that start with `CASH` or `FORMAT` are header lines, not records. Only
lines that start with `TX ` (with a trailing space) are records. Records are
processed in ascending TX id order.

Posting rules:

* `CREDIT` adds its amount to the balance; `DEBIT` subtracts it.
* `VOID <target>` cancels the target record entirely, as if it had never
  posted (including cancelling any correction previously applied to it).
  A VOID is a no-op unless its target is a `CREDIT` or `DEBIT` record that has
  not already been voided. In particular, voiding an already-voided record, or
  voiding a `VOID` or `CORRECT` line, does nothing.
* `CORRECT <target> new=<cents>` replaces the target's posted amount with the
  new amount. A CORRECT is a no-op unless its target is a `CREDIT` or `DEBIT`
  record that has not been voided (a correction aimed at an already-voided
  record, or at a `VOID`/`CORRECT` line, does nothing).

Some VOID and CORRECT lines in the ledger are traps: they look operative but
are no-ops under these rules. No live (non-voided) record is ever both
corrected and voided, so each live record posts exactly one final amount.

Your task: compute the final balance in cents and count the effective records
(the CREDIT/DEBIT records that are not voided).

## Ledger

```
CASH LEDGER - START 50000 CENTS - ONE RECORD PER LINE
FORMAT: TX <id> | CREDIT/DEBIT amt=<cents> | VOID <target> | CORRECT <target> new=<cents>

TX 0001 | DEBIT amt=13876 | memo=rent
TX 0002 | DEBIT amt=7437 | memo=refund
TX 0003 | DEBIT amt=15447 | memo=grant
TX 0004 | CREDIT amt=5713 | memo=payroll
TX 0005 | CREDIT amt=17343 | memo=fee
TX 0006 | DEBIT amt=4238 | memo=bonus
TX 0007 | CREDIT amt=19482 | memo=rent
TX 0008 | CREDIT amt=18975 | memo=tax
TX 0009 | CREDIT amt=15996 | memo=refund
TX 0010 | CREDIT amt=19101 | memo=grant
TX 0011 | DEBIT amt=4224 | memo=fee
TX 0012 | DEBIT amt=14832 | memo=bonus
TX 0013 | CREDIT amt=16255 | memo=parts
TX 0014 | DEBIT amt=6413 | memo=fee
TX 0015 | CREDIT amt=11142 | memo=order
TX 0016 | CREDIT amt=8678 | memo=refund
TX 0017 | DEBIT amt=7827 | memo=rebate
TX 0018 | CREDIT amt=5559 | memo=bonus
TX 0019 | DEBIT amt=882 | memo=parts
TX 0020 | CREDIT amt=10448 | memo=rent
TX 0021 | DEBIT amt=13670 | memo=grant
TX 0022 | DEBIT amt=8286 | memo=bonus
TX 0023 | DEBIT amt=10904 | memo=invoice
TX 0024 | DEBIT amt=2764 | memo=invoice
TX 0025 | DEBIT amt=13985 | memo=grant
TX 0026 | CREDIT amt=4986 | memo=grant
TX 0027 | CREDIT amt=505 | memo=freight
TX 0028 | CREDIT amt=16199 | memo=payroll
TX 0029 | DEBIT amt=14350 | memo=invoice
TX 0030 | CREDIT amt=17783 | memo=freight
TX 0031 | CREDIT amt=16931 | memo=bonus
TX 0032 | DEBIT amt=11506 | memo=rent
TX 0033 | CREDIT amt=910 | memo=freight
TX 0034 | DEBIT amt=683 | memo=refund
TX 0035 | CREDIT amt=13725 | memo=bonus
TX 0036 | DEBIT amt=10272 | memo=grant
TX 0037 | DEBIT amt=18174 | memo=rent
TX 0038 | DEBIT amt=2005 | memo=rebate
TX 0039 | CREDIT amt=5408 | memo=rebate
TX 0040 | CREDIT amt=1352 | memo=freight
TX 0041 | CREDIT amt=9845 | memo=fee
TX 0042 | DEBIT amt=13275 | memo=payroll
TX 0043 | DEBIT amt=5526 | memo=invoice
TX 0044 | DEBIT amt=13676 | memo=rebate
TX 0045 | CREDIT amt=7380 | memo=order
TX 0046 | CREDIT amt=15027 | memo=order
TX 0047 | CREDIT amt=1625 | memo=grant
TX 0048 | CREDIT amt=8614 | memo=tax
TX 0049 | CREDIT amt=457 | memo=order
TX 0050 | DEBIT amt=18871 | memo=invoice
TX 0051 | CREDIT amt=2402 | memo=tax
TX 0052 | CREDIT amt=15770 | memo=rent
TX 0053 | DEBIT amt=13651 | memo=bonus
TX 0054 | DEBIT amt=19582 | memo=payroll
TX 0055 | CREDIT amt=13184 | memo=rebate
TX 0056 | DEBIT amt=15861 | memo=freight
TX 0057 | CREDIT amt=19215 | memo=order
TX 0058 | DEBIT amt=13412 | memo=freight
TX 0059 | DEBIT amt=13951 | memo=refund
TX 0060 | DEBIT amt=10920 | memo=order
TX 0061 | CREDIT amt=12444 | memo=order
TX 0062 | DEBIT amt=18239 | memo=rebate
TX 0063 | DEBIT amt=6544 | memo=invoice
TX 0064 | CREDIT amt=6249 | memo=payroll
TX 0065 | DEBIT amt=14818 | memo=payroll
TX 0066 | DEBIT amt=15822 | memo=parts
TX 0067 | DEBIT amt=1671 | memo=tax
TX 0068 | DEBIT amt=16954 | memo=fee
TX 0069 | DEBIT amt=3085 | memo=refund
TX 0070 | CREDIT amt=7158 | memo=parts
TX 0071 | DEBIT amt=17725 | memo=tax
TX 0072 | DEBIT amt=318 | memo=order
TX 0073 | CREDIT amt=3534 | memo=order
TX 0074 | CREDIT amt=8131 | memo=freight
TX 0075 | DEBIT amt=15752 | memo=refund
TX 0076 | CREDIT amt=10374 | memo=refund
TX 0077 | DEBIT amt=16054 | memo=bonus
TX 0078 | DEBIT amt=2476 | memo=invoice
TX 0079 | DEBIT amt=504 | memo=refund
TX 0080 | DEBIT amt=14455 | memo=rent
TX 0081 | DEBIT amt=1496 | memo=bonus
TX 0082 | CREDIT amt=17941 | memo=grant
TX 0083 | CREDIT amt=2312 | memo=invoice
TX 0084 | CREDIT amt=12288 | memo=rent
TX 0085 | DEBIT amt=1145 | memo=rent
TX 0086 | CREDIT amt=17040 | memo=invoice
TX 0087 | DEBIT amt=17905 | memo=rebate
TX 0088 | DEBIT amt=12197 | memo=rent
TX 0089 | CREDIT amt=5768 | memo=fee
TX 0090 | DEBIT amt=300 | memo=invoice
TX 0091 | CREDIT amt=16888 | memo=order
TX 0092 | CREDIT amt=8923 | memo=parts
TX 0093 | CREDIT amt=19248 | memo=refund
TX 0094 | DEBIT amt=18004 | memo=tax
TX 0095 | CREDIT amt=285 | memo=payroll
TX 0096 | DEBIT amt=7409 | memo=payroll
TX 0097 | CORRECT 0011 new=2019 | memo=invoice
TX 0098 | CORRECT 0042 new=6839 | memo=invoice
TX 0099 | CORRECT 0041 new=12580 | memo=order
TX 0100 | CORRECT 0026 new=4592 | memo=payroll
TX 0101 | VOID 0006 | memo=refund
TX 0102 | VOID 0062 | memo=rent
TX 0103 | VOID 0043 | memo=refund
TX 0104 | VOID 0037 | memo=rent
TX 0105 | VOID 0022 | memo=rent
TX 0106 | VOID 0010 | memo=payroll
TX 0107 | CORRECT 0006 new=1405 | memo=grant
TX 0108 | CORRECT 0101 new=9189 | memo=rent
TX 0109 | VOID 0062 | memo=refund
TX 0110 | VOID 0097 | memo=order
```

## Report

End your response with a final line of exactly this form and nothing after it:

FINAL: balance_cents=<integer> effective=<integer>

* `balance_cents` is the exact final balance as a bare integer number of cents
  (leading zeros are not significant; it may be any non-negative integer).
* `effective` is the count of non-voided CREDIT/DEBIT records, as a base-10
  integer (leading zeros are not significant).

The final line is the only part graded; anything else in your response is
ignored.
