# 2.6 event definitions (Task 2) — the fields every event carries

All times are bar `datetime` strings from the source CSV (ISO-8601 with offset; `dataset.py` records UTC range).
"Leg units" = price ÷ the leg span, so different legs are comparable.

| field | H1 `Event` | H2 `H2Event` | meaning |
|---|---|---|---|
| ratio | yes | yes | r used for the level |
| side | yes | yes | BUY / SELL |
| anchor_start / anchor_end | yes | — | the leg's pivot bars |
| pool_kind / pool_level / pool_first / pool_second | — | yes | EQH or EQL, its level and its two pivot bars |
| sweep_time | — | yes | bar that swept the pool and closed back inside |
| leg_start / leg_end | — | yes | the measured reversal leg |
| confirmation_time | yes | — | bar whose close made both anchors known (limit placed after it) |
| entry_time / entry | yes | yes | fill bar and fill price (limit, or the open on a gap through) |
| leg_range | yes | yes | span of the measured leg (price units) |
| bars_to_fill | yes | yes | bars from placing the limit to the fill |
| mfe_leg / mae_leg | yes | yes | best / worst move over 40 bars after the fill bar, leg units |
| returns_leg | yes | yes | {"5","10","20","40"}: (close − fill) × side − cost, leg units |

Counts in reports: **raw n** (all fills) ≥ **de-clustered n** (no overlapping windows per ratio) ≥ segment n (purged at split
boundaries). Touch rate (H1) = fills ÷ limits placed. Control = same side / span / horizon, entry at a random bar's open in the
same segment.
