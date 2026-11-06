"""EVENT CLOCK: what is about to happen, and when (owner 2026-11-06: "wait until 08:30, an hour before, two hours before ... Silver Bullet, session opens, day / week / month starts and ends").

Pure functions (no network): `due(now, calendar_rows)` returns the heads-up alerts that are DUE now. The server job (modules/brain_cron.py) runs every 30 minutes, so a window is announced
when it starts in 0-75 minutes (once per window: the caller dedupes on `id`), a news event at 120 / 60 / 30 minutes before (+-15 min), and the opening range windows right after a session opens.
All clock times are New York time (the same clock the Workspace and the Day plan use); crypto day / week / month boundaries are UTC.

An alert is a HEADS-UP, never a trade and never a direction: news can move the market either way, the text says so."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
UTC = timezone.utc
LEAD_MIN = 75                  # a scheduled window is announced when it starts within this many minutes
NEWS_AT = (120, 60, 30)        # minutes before a high-impact event
NEWS_TOL = 15

# (id, label EN, label AR, NY hour, NY minute, duration minutes, note EN, note AR)
WINDOWS = [
    ("sb_london", "ICT Silver Bullet - London", "سيلفر بوليت لندن", 3, 0, 60, "FVG after a liquidity sweep inside this hour (03:00-04:00 NY)", "FVG بعد سحب سيولة جوه الساعة دي (03:00-04:00 نيويورك)"),
    ("sb_ny_am", "ICT Silver Bullet - NY AM", "سيلفر بوليت نيويورك صباحاً", 10, 0, 60, "the classic one: FVG after a sweep, 10:00-11:00 NY", "الكلاسيكية: FVG بعد سحب سيولة، 10:00-11:00 نيويورك"),
    ("sb_ny_pm", "ICT Silver Bullet - NY PM", "سيلفر بوليت نيويورك مساءً", 14, 0, 60, "afternoon FVG after a sweep, 14:00-15:00 NY", "FVG بعد سحب سيولة بعد الضهر، 14:00-15:00 نيويورك"),
    ("open_asia", "Asia session opens", "افتتاح آسيا", 19, 0, 30, "the Asian range starts forming: mark its high / low (London sweeps it)", "نطاق آسيا بيبدأ يتكوّن: علّم قمته وقاعه (لندن بتسحبه)"),
    ("open_london", "London session opens", "افتتاح لندن", 3, 0, 30, "first 15-30 minutes: the opening range; wait for the sweep of the Asian high / low", "أول 15-30 دقيقة: نطاق الافتتاح؛ استنى سحب قمة/قاع آسيا"),
    ("open_ny_fx", "New York opens (FX / futures)", "افتتاح نيويورك (فوركس/عقود)", 8, 0, 30, "news hour: spreads and spikes; first 15-30 minutes are the opening range", "ساعة الأخبار: سبريد وسبايكات؛ أول 15-30 دقيقة نطاق الافتتاح"),
    ("open_ny_stocks", "US stocks open", "افتتاح الأسهم الأمريكية", 9, 30, 30, "the cash open: biggest volume of the day, first 15-30 minutes set the range", "افتتاح الكاش: أكبر فوليوم في اليوم، أول 15-30 دقيقة بتحدد النطاق"),
    ("close_ny", "New York closes", "إغلاق نيويورك", 17, 0, 30, "daily close / FX day rolls: closing levels matter, thin liquidity after", "إغلاق اليوم / تبديل يوم الفوركس: مستويات الإغلاق مهمة والسيولة بتقل"),
]
OPENING_RANGES = ("open_london", "open_ny_fx", "open_ny_stocks", "open_asia")   # 15 and 30 minute marks after these

COUNTRY_ASSETS = {
    "USD": ("gold, silver, indices, BTC / ETH, EUR/USD, GBP/USD, USD/JPY", "الدهب والفضة والمؤشرات وBTC وETH واليورو والإسترليني والين"),
    "EUR": ("EUR/USD, EUR crosses, indices (DAX)", "اليورو ومؤشر داكس"), "GBP": ("GBP/USD, GBP crosses", "الإسترليني"), "JPY": ("USD/JPY, JPY crosses, Nikkei", "الين ونيكاي"),
    "AUD": ("AUD/USD", "الأسترالي"), "NZD": ("NZD/USD", "النيوزلندي"), "CAD": ("USD/CAD, oil", "الكندي والنفط"), "CHF": ("USD/CHF", "الفرنك"), "CNY": ("risk assets, metals", "الأصول الخطرة والمعادن"),
}


def _utc(now):
    if now is None:
        return datetime.now(UTC)
    if isinstance(now, (int, float)):
        return datetime.fromtimestamp(now, UTC)
    return now.astimezone(UTC) if now.tzinfo else now.replace(tzinfo=UTC)


def _next_at(now_utc: datetime, hh: int, mm: int, tz=NY) -> datetime:
    """Next time (UTC) the wall clock in `tz` shows hh:mm, today if it is still ahead or less than 5 minutes behind."""
    loc = now_utc.astimezone(tz)
    cand = loc.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if cand < loc - timedelta(minutes=5):
        cand += timedelta(days=1)
        cand = cand.replace(hour=hh, minute=mm)
    return cand.astimezone(UTC)


def _alert(id_, kind, at, now, en, ar, note_en, note_ar):
    mins = round((at - now).total_seconds() / 60)
    return {"id": id_, "kind": kind, "at": at.isoformat(), "in_min": mins, "title_en": en, "title_ar": ar, "note_en": note_en, "note_ar": note_ar}


def _boundaries(now_utc: datetime):
    """Day / week / month start and end (crypto: UTC; FX day rolls 17:00 NY, week opens Sunday 17:00 NY)."""
    out = []
    d = now_utc.date()
    # crypto day open (00:00 UTC) and month start / end
    nxt = datetime(d.year, d.month, d.day, tzinfo=UTC) + timedelta(days=1)
    out.append(("day_crypto", nxt, "Crypto daily candle opens (00:00 UTC)", "فتح شمعة اليوم للكريبتو (00:00 UTC)", "the daily open is a level price often returns to; day-open sweeps are common", "فتح اليوم مستوى السعر بيرجعله كتير؛ وسحبه شائع"))
    if nxt.day == 1:   # the month turns at this midnight: it starts and (the same moment) the previous one ends
        out.append(("month_start", nxt, "New MONTH starts (00:00 UTC)", "بداية شهر جديد (00:00 UTC)", "monthly open: watch the reaction to the previous month's high / low and the monthly open", "فتح الشهر: راقب رد الفعل على قمة/قاع الشهر السابق وفتح الشهر"))
        out.append(("month_end", nxt, "Month ENDS (00:00 UTC)", "نهاية الشهر (00:00 UTC)", "month-end flows / rebalancing can move metals and indices late in the session", "تدفقات نهاية الشهر وإعادة التوازن بتحرك المعادن والمؤشرات"))
    if nxt.weekday() == 0:
        out.append(("week_crypto", nxt, "Crypto WEEK opens (Monday 00:00 UTC)", "فتح الأسبوع للكريبتو (الإثنين 00:00 UTC)", "weekly open: the first move often sweeps the weekend range", "فتح الأسبوع: أول حركة غالباً بتسحب نطاق الويك إند"))
    # FX / metals week opens Sunday 17:00 NY
    wk = _next_at(now_utc, 17, 0)
    if wk.astimezone(NY).weekday() == 6:
        out.append(("week_fx", wk, "FX / metals WEEK opens (Sunday 17:00 NY)", "فتح أسبوع الفوركس والمعادن (الأحد 17:00 نيويورك)", "gaps and thin liquidity at the open; wait for the first 30-60 minutes", "فجوات وسيولة قليلة وقت الفتح؛ استنى أول 30-60 دقيقة"))
    return out


def due(now=None, calendar_rows=None, lead_min: int = LEAD_MIN) -> list:
    """Alerts due right now (sorted by time). `calendar_rows` = calendar_feed.fetch_calendar() rows (ts in ms, impact, country, title)."""
    nu = _utc(now)
    out = []
    for wid, en, ar, hh, mm, dur, ne, na in WINDOWS:
        at = _next_at(nu, hh, mm)
        mins = (at - nu).total_seconds() / 60
        if -5 <= mins <= lead_min:
            out.append(_alert(f"win|{wid}|{at:%Y%m%d%H%M}", "window", at, nu, en, ar, ne, na))
        if wid in OPENING_RANGES:   # the 15 / 30 minute marks after an open (the opening range is complete)
            for k in (15, 30):
                at2 = at + timedelta(minutes=k)
                m2 = (at2 - nu).total_seconds() / 60
                if -5 <= m2 <= lead_min:
                    hm2 = at2.astimezone(NY).strftime("%H:%M")
                    out.append(_alert(f"or{k}|{wid}|{at:%Y%m%d%H%M}", "opening_range", at2, nu, f"{en.replace(' opens', '').replace(' session', '')}: {k}-minute opening range sets at {hm2} NY",
                                      f"{ar.replace('افتتاح ', '')}: نطاق أول {k} دقيقة بيتحدد الساعة {hm2} نيويورك",
                                      f"after {hm2} trade the break / sweep of its high or low, not the middle", f"بعد {hm2} اتاجر كسر أو سحب قمته/قاعه مش النص"))
    for bid, at, en, ar, ne, na in _boundaries(nu):
        mins = (at - nu).total_seconds() / 60
        if -5 <= mins <= lead_min:
            out.append(_alert(f"bnd|{bid}|{at:%Y%m%d%H%M}", "boundary", at, nu, en, ar, ne, na))
    for r in calendar_rows or []:
        if str(r.get("impact", "")).title() != "High":
            continue
        at = datetime.fromtimestamp(r["ts"] / 1000, UTC)
        mins = (at - nu).total_seconds() / 60
        for t in NEWS_AT:
            if abs(mins - t) <= NEWS_TOL:
                cur = str(r.get("country", ""))
                ae, aa = COUNTRY_ASSETS.get(cur, ("the related markets", "الأسواق المرتبطة"))
                hm = at.astimezone(NY).strftime("%H:%M")
                out.append(_alert(f"news|{r.get('title')}|{cur}|{at:%Y%m%d%H%M}|{t}", "news", at, nu, f"{cur} {r.get('title')} at {hm} NY (in ~{t} min)", f"{cur} {r.get('title')} الساعة {hm} نيويورك (بعد ~{t} دقيقة)",
                                  f"high impact: it can move {ae} either way. Do not open new trades in the last 30 minutes before; wait for the first 15 minutes after. forecast {r.get('forecast') or '-'} / previous {r.get('previous') or '-'}",
                                  f"تأثير عالي: ممكن يحرك {aa} في الاتجاهين. ما تفتحش صفقات جديدة آخر 30 دقيقة قبله؛ استنى أول 15 دقيقة بعده. المتوقع {r.get('forecast') or '-'} / السابق {r.get('previous') or '-'}"))
                break
    out.sort(key=lambda a: a["at"])
    return out


def format_alert(a: dict, ar: bool = True) -> str:
    import html
    esc = html.escape
    ico = {"news": "📰", "window": "⏰", "opening_range": "📏", "boundary": "🗓"}.get(a["kind"], "⏰")
    mins = a["in_min"]
    when = (f"بعد {mins} دقيقة" if mins > 0 else "دلوقتي") if ar else (f"in {mins} min" if mins > 0 else "now")
    return f"{ico} <b>{esc(a['title_ar' if ar else 'title_en'])}</b> · {when}\n{esc(a['note_ar' if ar else 'note_en'])}\n<i>{'تنبيه مش إشارة دخول' if ar else 'A heads-up, not an entry signal'}</i>"
