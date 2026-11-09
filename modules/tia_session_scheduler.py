"""Timezone-aware recurring schedule calculations for TIA; no exchange hours are assumed."""
from __future__ import annotations
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

def validate_weekly_rule(rule: dict) -> dict:
    if not isinstance(rule, dict): raise ValueError("schedule must be an object")
    days=rule.get("weekdays")
    if not isinstance(days,list) or not days or any(type(d) is not int or d<0 or d>6 for d in days):
        raise ValueError("weekdays must be a non-empty list, Monday=0..Sunday=6")
    try: clock=time.fromisoformat(str(rule.get("local_time")))
    except ValueError as exc: raise ValueError("local_time must be HH:MM[:SS]") from exc
    if clock.tzinfo is not None: raise ValueError("local_time must not contain an offset")
    return {"frequency":"weekly","weekdays":sorted(set(days)),"local_time":clock.isoformat(timespec="minutes")}

def next_occurrence(rule: dict, timezone_name: str, after_utc: datetime) -> datetime:
    rule=validate_weekly_rule(rule)
    try: zone=ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc: raise ValueError("unknown IANA timezone") from exc
    if after_utc.tzinfo is None: raise ValueError("after_utc must be timezone-aware")
    after_utc=after_utc.astimezone(timezone.utc)
    local=after_utc.astimezone(zone)
    target=time.fromisoformat(rule["local_time"])
    for offset in range(15):
        day=local.date()+timedelta(days=offset)
        if day.weekday() not in rule["weekdays"]: continue
        naive=datetime.combine(day,target)
        candidate=naive.replace(tzinfo=zone,fold=0)
        # Reject nonexistent spring-forward wall times instead of silently shifting.
        if candidate.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None)!=naive: continue
        value=candidate.astimezone(timezone.utc)
        if value>after_utc: return value
    raise ValueError("no valid occurrence in next 14 days; check weekday/time and DST")

def utc_iso(value: datetime) -> str:
    if value.tzinfo is None: raise ValueError("datetime must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

def preview(rule: dict, timezone_name: str, after_utc: datetime, count: int=5) -> list[str]:
    if count<1 or count>20: raise ValueError("preview count must be 1..20")
    result=[]; cursor=after_utc
    for _ in range(count):
        nxt=next_occurrence(rule,timezone_name,cursor)
        result.append(nxt.astimezone(ZoneInfo(timezone_name)).isoformat(timespec="minutes"))
        cursor=nxt
    return result
