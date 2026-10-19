# Elliott and harmonic: what the schools say, what the app does, what is still missing

## Elliott (standard textbook rules, Frost & Prechter / Elliott's own writing)
Impulse 1-2-3-4-5 (hard rules):
1. Wave 2 never retraces more than 100% of wave 1.
2. Wave 3 is never the shortest of waves 1, 3 and 5.
3. Wave 4 never enters the price territory of wave 1 (no overlap, in normal impulses).
Guidelines (soft, used for scoring, not for a yes/no):
- Wave 2 usually retraces 50-61.8% of wave 1 (deep); wave 4 usually 38.2% (shallow); alternation helps.
- Wave 3 is often 1.618 x wave 1 (extension), wave 5 often equals wave 1 or 0.618 x wave 1-3.
Corrective A-B-C: B retraces 38.2-78.6% of A; C often equals A or 1.618 x A.

## What the app does now (workspace_app.html: ewCount / paintEWauto, signals.py: elliott_bull)
- Auto count from zig-zag pivots (0.6% threshold): numbers 1-5 when the last six pivots pass the three hard rules, plus A-B-C.
- OTE boxes (62-79%) where wave 2 / 4 / A end or are expected to end (label now "OTE 62-79%").
- Signals: "Wave 3 start" needs a 45-72% retracement and a wave-2 reaction off EMA or VWAP; "Wave 5 start" similar.

## What is missing (why the owner sees no numbers)
- The three hard rules are strict: most real charts fail one of them, so the count is empty. Fix: show the best candidate as "forming" (dashed) with the rule it breaks, instead of showing nothing.
- No Fibonacci labels on the retracement zones (38.2 / 50 / 61.8 / 78.6). Fix: draw the lines with their values.
- No options to tune the zig-zag threshold (0.6%) per timeframe. Fix: a setting in the indicator menu.
- Signals and the lab do not yet score wave counts (strength of the count, rules passed). The lab has ew3 / ew5 / abc / wavec only: ew3 -0.13R (775 signals), ew5 +0.03R (106), abc +0.07R (103), wavec +0.10R (88) on 2026-10-18; none passes the gate.

## Harmonic (XABCD) - classic ratios (Carney, Scott)
- Gartley: AB 0.618, BC 0.382-0.886, CD 1.27-1.618 of XA, D at 0.786 of XA.
- Bat: D at 0.886 of XA. Butterfly: D at 1.27 (extension). Crab: D at 1.618. Cypher: D at 0.786 of XC.
- Tolerance around each ratio is a choice; the app uses modules/harmonic.py (zigzag dev 1.2%, ratio tolerance).
- Lab: key `harmonic` added 2026-10-18; first result pending the next run. Tested on synthetic candles only.

## Plan (measurable)
1. Lab: score Elliott counts by how many hard rules pass, and test "rules passed = 3" vs "2" out-of-sample, same entries.
2. Lab: harmonic per pattern name (Gartley, Bat, Butterfly, Crab, Cypher) with n >= 100 per name, or it is not evidence.
3. App: show "forming" counts and Fib labels (after the lab says it helps, not before).

## Study notes: a published Elliott indicator (TradingView, LuxAlgo, CC BY-NC-SA 4.0)
Read for the RULES only. The code is not copied into this repo: the licence is non-commercial and share-alike, so we write our own
implementation from the rules below, and credit the source in the docs.

What it does, in our words:
- Three zig-zag degrees at once (pivot lengths 4, 8 and 16 bars). Each degree gets its own count, so a small wave sits inside a bigger one.
- A motive (impulse) count is kept when the last six pivots pass: wave 3 is not the shortest of 1, 3, 5; the wave-5 end is above the wave-3 end;
  the wave-3 end is above the wave-1 end; the wave-5 end is above the wave-2 end (mirror for bearish).
- Corrective ABC after an impulse: the A, B, C pivots must pass a validity test, and the box between C and the wave-4 level shows the zone.
- Fibonacci zone under the newest impulse: 0.500, 0.618, 0.764 and 0.854 of the wave-1 range from the wave-5 end.
  The lines turn red once price breaks the outer zone (count invalid), green while it holds.
- A "possible new start" marker when price has made a new pivot beyond the previous count, and an invalidation marker when a count breaks.
- Alerts for new count, invalidation and possible new start.

What we do not have yet and is worth testing (in the lab first):
1. Multi-degree counts (3 pivot lengths) instead of one threshold. Test: does the count from a higher degree agree with the signals of a lower degree? Same entries, same stop and target.
2. Fibonacci zone of the newest impulse (0.5 to 0.854) as the location filter for trades. Test: trade only inside the zone.
3. Invalidation rule: a count that breaks is dropped, not kept. Test: does keeping broken counts hurt?

Our own rules stay the textbook ones (wave 2 not beyond the start of wave 1; wave 3 not the shortest; wave 4 not in wave 1's price zone).
Test plan goes into the lab with the same gate: n >= 100, t > 3, both halves positive. No app change until a rule passes.
