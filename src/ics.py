# -*- coding: utf-8 -*-
"""Erzeugt reise.ics aus events.py – abonnierbarer Ferienkalender."""
import re, sys, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from events import build, UNTERKUNFT
from prep import TASKS as PREP, LINKS as PREPLINKS

BUILD = os.environ.get("ICS_BUILD_UTC", datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
SITE = "https://salsafever21.github.io/southafrica/"
ICON = {"fahrt":"🚗","buchung":"✅","checkin":"🔑","checkout":"🔑","tipp":"💡","warnung":"⚠️","frei":"😴"}
PREFIX = {"tipp":"Idee: "}

def esc(t):
    t = (t or "").replace("\\","\\\\").replace(";","\;").replace(",","\\,")
    return t.replace("\r\n","\n").replace("\n","\\n")

def fold(line):
    b = line.encode("utf-8"); out=[]
    while len(b) > 73:
        cut = 73
        while cut > 0 and (b[cut] & 0xC0) == 0x80: cut -= 1
        out.append(b[:cut]); b = b[cut:]
    out.append(b)
    return "\r\n ".join(x.decode("utf-8") for x in out)

def d8(iso): return iso.replace("-","")
def plus1(iso):
    d = datetime.date.fromisoformat(iso) + datetime.timedelta(days=1)
    return d.strftime("%Y%m%d")

ev=[]
def add(uid, summary, dtstart, dtend, desc="", loc="", allday=False, alarm=None):
    e=["BEGIN:VEVENT",f"UID:{uid}@southafrica.salsafever21",f"DTSTAMP:{BUILD}",f"LAST-MODIFIED:{BUILD}","SEQUENCE:0"]
    if allday:
        e += [f"DTSTART;VALUE=DATE:{dtstart}", f"DTEND;VALUE=DATE:{dtend}", "TRANSP:TRANSPARENT", "X-MICROSOFT-CDO-ALLDAYEVENT:TRUE"]
    else:
        e += [f"DTSTART;TZID=Africa/Johannesburg:{dtstart}", f"DTEND;TZID=Africa/Johannesburg:{dtend}"]
    e.append(fold("SUMMARY:"+esc(summary)))
    if desc: e.append(fold("DESCRIPTION:"+esc(desc)))
    if loc:  e.append(fold("LOCATION:"+esc(loc)))
    if alarm: e += ["BEGIN:VALARM","ACTION:DISPLAY",f"TRIGGER:-PT{alarm}M",fold("DESCRIPTION:"+esc(summary)),"END:VALARM"]
    e.append("END:VEVENT")
    ev.append("\r\n".join(e))

timed, allday, stays, daymeta = build()

for s in stays:
    add(f"stay{s['st']}", f"🛏 Etappe {s['st']} · {s['name']}", d8(s["von"]), d8(s["bis"]),
        f"{s['naechte']} Nächte\n{s['adr']}\n\n{SITE}", s["adr"], allday=True)

SKIP = {"frei"}   # Mittagsschlaf: standardmaessig nicht im Kalender

for t in timed:
    if t["art"] in SKIP: continue
    hs,he = t["s"], t["e"]
    ds = f"{d8(t['d'])}T{hs//60:02d}{hs%60:02d}00"
    de = f"{d8(t['d'])}T{he//60:02d}{he%60:02d}00"
    summ = f"{ICON[t['art']]} {PREFIX.get(t['art'],'')}{t['titel']}"
    add(t["id"], summ, ds, de, t["detail"], "", alarm=30 if t["art"] in ("buchung","fahrt") else None)

for a in allday:
    for i in a["items"]:
        if i["art"] in SKIP: continue
        summ = f"{ICON[i['art']]} {PREFIX.get(i['art'],'')}{i['titel']}"
        add(i["id"], summ, d8(a["d"]), plus1(a["d"]), i["detail"], allday=True)
    lab = {"fahrt":"🚗","ankunft":"✈️","abreise":"✈️","stand":"📍"}.get(a["typ"],"📍")
    add("day"+d8(a["d"]), f"{lab} {a['titel']}", d8(a["d"]), plus1(a["d"]),
        f"Etappe {a['st']} · {a['sub']}\n\nTagesplan: {SITE}", allday=True)

# Vorbereitung: 09:00, mit Erinnerung
for (pid, pd, ptit, pdet, purg) in PREP:
    ds = d8(pd)+"T090000"; de = d8(pd)+"T093000"
    _lk = "".join("\n" + lab + ": " + (SITE.rstrip("/")+"/"+u if not u.startswith("http") else u)
                  for (lab,u,k) in PREPLINKS.get(pid, []))
    add(pid, ("📋 " if not purg else "📌 ")+ptit, ds, de, pdet+_lk+f"\n\n{SITE}", "", alarm=5)

CAL=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Suedafrika 2026//Reisekalender//DE","CALSCALE:GREGORIAN","METHOD:PUBLISH",
 "X-WR-CALNAME:Südafrika Oktober 2026",
 f"X-WR-CALDESC:Ferienkalender – Fahrten\\, Buchungen und Tagesplan. Quelle: {SITE}",
 "X-WR-TIMEZONE:Africa/Johannesburg","REFRESH-INTERVAL;VALUE=DURATION:PT6H","X-PUBLISHED-TTL:PT6H",
 "BEGIN:VTIMEZONE","TZID:Africa/Johannesburg","BEGIN:STANDARD","DTSTART:19700101T000000",
 "TZOFFSETFROM:+0200","TZOFFSETTO:+0200","TZNAME:SAST","END:STANDARD","END:VTIMEZONE"] + ev + ["END:VCALENDAR"]

out = "\r\n".join(CAL) + "\r\n"
target = sys.argv[1] if len(sys.argv) > 1 else "./reise.ics"
open(target,"w",encoding="utf-8",newline="").write(out)
print(f"ICS: {len(ev)} Termine -> {target}")
