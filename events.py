# -*- coding: utf-8 -*-
"""Gemeinsame Terminliste fuer ICS und Wochenkalender."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan import DAYS
from sun import times as suntimes, ORTE as SUNORTE

YEAR, MONTH = 2026, 10

UNTERKUNFT = {
 "1": ("Adamsgarth Guesthouse", "26 Mount Rhodes Drive, Hout Bay, Kapstadt", 4, 8, -34.0333, 18.3592),
 "2": ("Adara Palmiet Valley Estate", "Sonstraal Road, Klein Drakenstein, Paarl", 8, 11, -33.7660, 18.9580),
 "3": ("Rivergate Guest Farm", "Wortelgat Road, Stanford", 11, 14, -34.4295, 19.4220),
 "4": ("Melozhori Private Game Reserve", "R317, Stormsvlei, Overberg", 14, 16, -34.0370, 20.0870),
 "6": ("Emily Moon River Lodge", "Rietvlei Road, Plettenberg Bay", 16, 20, -34.0553, 23.3716),
 "7": ("Woodall Country House & Spa", "Woodall Farm, Jan Smuts Avenue, Addo", 20, 23, -33.5006, 25.6838),
 "8": ("Lalibela Mark's Camp", "Lalibela Game Reserve, N2, Paterson", 23, 26, -33.3000, 26.0600),
}

def clean(t):
    t = re.sub(r"<br\s*/?>", "\n", t or "")
    return re.sub(r"<[^>]+>", "", t).strip()

def daynum(dat):
    return int(re.search(r"(\d+)\.\s*Okt", dat).group(1))

def dur_minutes(art, titel, detail):
    txt = (titel or "") + " " + (detail or "")
    m = re.search(r"(\d{1,2}):(\d{2})\s*[–-]\s*(\d{1,2}):(\d{2})", titel or "")
    if m:
        a = int(m.group(1))*60+int(m.group(2)); b = int(m.group(3))*60+int(m.group(4))
        if b > a: return b - a
    m = re.search(r"realistisch\s*<?/?b?>?\s*(\d{1,2}):(\d{2})\s*[–-]\s*(\d{1,2}):(\d{2})\s*h", txt)
    if m: return int(m.group(3))*60 + int(m.group(4))
    m = re.search(r"realistisch\s*(\d{1,2})[–-](\d{1,2})\s*Min", txt)
    if m: return int(m.group(2))
    m = re.search(r"realistisch\s*<?/?b?>?\s*(\d{1,2}):(\d{2})\s*h", txt)
    if m: return int(m.group(1))*60 + int(m.group(2))
    m = re.search(r"(\d{1,3})\s*[–-]\s*(\d{1,3})\s*Min", txt)
    if m: return int(m.group(2))
    return {"fahrt":180,"buchung":90,"checkin":30,"checkout":30,"tipp":120,"frei":150}.get(art,60)

def iso(day): return f"{YEAR}-{MONTH:02d}-{day:02d}"

from prep import TASKS as PREP

def build():
    timed, allday, stays, daymeta = [], [], [], {}
    for st,(name,adr,von,bis,la,lo) in UNTERKUNFT.items():
        stays.append({"st":st,"name":name,"adr":adr,"von":iso(von),"bis":iso(bis),
                      "naechte":bis-von,"lat":la,"lng":lo})
    for (dat, st, titel, sub, typ, items) in DAYS:
        day = daynum(dat)
        _n,_la,_lo = SUNORTE.get(st, SUNORTE["1"])
        _s = suntimes(_la,_lo,iso(day)) or {}
        daymeta[iso(day)] = {"st":st,"titel":titel,"sub":sub,"typ":typ,"label":dat}
        untimed = []
        for i, it in enumerate(items):
            z, art, t, detail = it[0], it[1], it[2], it[3]
            explicit = it[4] if len(it) > 4 else None
            if not z:
                untimed.append({"id":f"d{day}i{i}","art":art,"titel":clean(t),"detail":clean(detail)})
                continue
            hh,mm = z.split(":")
            s = int(hh)*60+int(mm)
            e = min(s + (explicit or dur_minutes(art,t,detail)), 23*60+59)
            timed.append({"id":f"d{day}i{i}","d":iso(day),"s":s,"e":e,"art":art,
                          "titel":clean(t),"detail":clean(detail),"st":st})
        allday.append({"d":iso(day),"st":st,"titel":titel,"sub":sub,"typ":typ,"items":untimed,
                       "sun":{"ort":_n,"auf":_s.get("auf"),"unter":_s.get("unter"),"lat":_la,"lng":_lo}})
    return timed, allday, stays, daymeta
