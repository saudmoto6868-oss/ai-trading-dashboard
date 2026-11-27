"""Timeframe skills for the Spot brain (owner 2026-11-27: the brain gives a verdict for any timeframe the owner picks).
A skill = a trading style with its own timeframe pair and its own brain horizon. Pure table, no network.
Scalp (15m-1H) is listed but NOT available yet: the brain's bundle only has 4H / 1D / 1W / 1M candles today."""
from __future__ import annotations

SKILLS = {
    "scalp":   {"ar": "سكالب 15م–1س", "tfs": "15m–1H", "horizon": None,
                "note": "مش متاح: محتاج داتا 15 دقيقة وساعة، والمخ لسه ماسحبهاش"},
    "day":     {"ar": "يومي 4س–1ي", "tfs": "4H–1D", "horizon": "day"},
    "swing":   {"ar": "سوينج 1ي–1أ", "tfs": "1D–1W", "horizon": "week"},
    "monthly": {"ar": "شهري 1أ–1ش", "tfs": "1W–1M", "horizon": "month"},
    "yearly":  {"ar": "سنوي", "tfs": "1M+", "horizon": "year"},
}
DEFAULT = ("day", "swing", "monthly", "yearly")


def available(skill: str) -> bool:
    return bool(SKILLS.get(skill, {}).get("horizon"))


def horizons_for(skills) -> tuple[str, ...]:
    """Brain horizons for the picked skills, in table order, unavailable skills dropped."""
    out = []
    for k in SKILLS:
        if k in set(skills or ()) and available(k):
            out.append(SKILLS[k]["horizon"])
    return tuple(out)
