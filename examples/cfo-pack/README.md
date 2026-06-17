# Example pack — AI CFO (domain rules on top of the reliability gate)

A worked example of layering a **domain rule-pack** on the general reliability gate. The
pack is `harness/gate/rules/cfo.json`. It adds finance-specific tripwires beyond the
general "source every figure":

- **Spend ⇒ verdict** — any spend/commitment in a deliverable must carry a reasoned CFO
  verdict block (`VERDICT: refuse|conditional|escalate` + `TRIPWIRE` + `GROUNDS` +
  `FLIPS IF:`), so an AI that can't say *no* doesn't quietly approve a bad spend.
- **Escalate-only** — M&A / equity dilution / tax strategy ⇒ `VERDICT: escalate` (no
  reasoning override — licensed-professional territory).

## Try it

```bash
# a spend recommendation with no verdict -> flagged
printf 'Recommend: upgrade to annual billing, commit $3,720/year.\n' \
  | MYINC_PROFILE=sonnet python3 ../../harness/gate/refuse.py

# add the verdict the gate asked for -> clean
printf 'Recommend: upgrade to annual billing, commit $3,720/year (vendor quote, 2026-06-16).\nVERDICT: conditional\nTRIPWIRE: spend-runway\nGROUNDS: runway 14.2 months (bookkeeping, 2026-06-16).\nFLIPS IF: runway drops below 12 months.\n' \
  | MYINC_PROFILE=sonnet python3 ../../harness/gate/refuse.py
```

## Write your own pack

A pack is a small JSON of tripwires (`fires_on` / `requires` / `severity`) plus, if you
want it enforced semantically, a verifier check. Start from `reliability.json`, add your
domain's rules, point the gate at it. The reliability layer (sourcing, no fabrication)
always applies underneath.
