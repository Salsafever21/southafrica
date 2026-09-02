# -*- coding: utf-8 -*-
import csv, html, sys, os, urllib.parse
sys.path.insert(0,'/root/suedafrika')
from akt import A as AKT
from plan import DAYS
from info import INFO
from events import build as build_events
from prep import TASKS as PREP, LINKS as PREPLINKS
import karte as _karte
from preise import parse as _pparse, familie as _pfam, KURS as _KURS, BENZIN as _BENZIN
import json as _json
_timed,_allday,_stays,_daymeta = build_events()
_daysun = {a['d']: a.get('sun',{}) for a in _allday}

RHDR=["Etappe","Name","Adresse","Ort","Bewertung","Reviews","Kategorie","Preis","Kinderfreundlich","Reservierung","Website","Lat","Lng","Hinweis"]
AHDR=["Etappe","Name","Adresse","Ort","Bewertung","Reviews","Kategorie","Preis","Dauer","Kinderwagen","Mindestalter","Warum","BesteZeit","Buchung","Website","Lat","Lng","Hinweis"]

rest=list(csv.DictReader(open('./Suedafrika_Restaurants_GoogleMaps.csv',encoding='utf-8-sig'),delimiter=';'))
akt=[dict(zip(AHDR,r)) for r in AKT]

STAGES={
"1":("Kapstadt","4.–8. Oktober","4 Nächte · Adamsgarth Guesthouse, Hout Bay"),
"2":("Paarl & Winelands","8.–11. Oktober","3 Nächte · Adara Palmiet Valley Estate"),
"3":("Whale Coast","11.–14. Oktober","3 Nächte · Rivergate Guest Farm, Stanford"),
"4":("Melozhori & Route 62","14.–16. Oktober","2 Nächte · Melozhori Game Reserve"),
"5":("Fahrtag an die Garden Route","16. Oktober","Melozhori → Plettenberg Bay"),
"6":("Plettenberg Bay","16.–20. Oktober","4 Nächte · Emily Moon River Lodge"),
"7":("Sundays River Valley","20.–23. Oktober","3 Nächte · Woodall Country House & Spa"),
"8":("Lalibela & Gqeberha","23.–26. Oktober","3 Nächte · Lalibela Mark's Camp"),
}
ENDS={
"1":("Adamsgarth Guesthouse, Mount Rhodes Drive, Hout Bay, Cape Town, Südafrika",""),
"2":("Adara Palmiet Valley Estate, Sonstraal Road, Klein Drakenstein, Paarl, Südafrika",""),
"3":("Rivergate Guest Farm, Wortelgat Road, Stanford, Südafrika",""),
"4":("Melozhori Private Game Reserve, R317, Stormsvlei, Südafrika",""),
"5":("Melozhori Private Game Reserve, Stormsvlei, Südafrika","Emily Moon River Lodge, Rietvlei Road, Plettenberg Bay, Südafrika"),
"6":("Emily Moon River Lodge, Rietvlei Road, Plettenberg Bay, Südafrika",""),
"7":("Woodall Country House & Spa, Jan Smuts Avenue, Addo, Südafrika",""),
"8":("Lalibela Game Reserve, N2, Paterson, Südafrika","Flughafen Gqeberha, Port Elizabeth, Südafrika"),
}
def snum(e): return e.split(" |")[0]
def such(d): return d["Name"]+", "+d["Adresse"]+", "+d["Ort"]+", Südafrika"
def murl(d): return "https://www.google.com/maps/search/?api=1&query="+urllib.parse.quote(such(d))
def qpt(d):
    la,ln = d.get("Lat","").strip(), d.get("Lng","").strip()
    return f"{la},{ln}" if la and ln else such(d)
def price(p):
    return {"E":"€","EE":"€€","EEE":"€€€","E-EE":"€–€€","EE-EEE":"€€–€€€"}.get(p.strip(),p.strip())

# ---------- kombinierte CSV ----------
with open('./Suedafrika_Restaurants_und_Aktivitaeten.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';',quoting=csv.QUOTE_ALL)
    w.writerow(["Suchbegriff","Typ","Etappe","Name","Adresse","Ort","Bewertung","Reviews","Kategorie","Preis","Dauer","Kinderwagen","Mindestalter","Info","Beste Zeit","Reservierung","Website","Lat","Lng","Hinweis"])
    for d in rest:
        w.writerow([such(d),"Restaurant",d["Etappe"],d["Name"],d["Adresse"],d["Ort"],d["Bewertung"],d["Reviews"],
                    d["Kategorie"],price(d["Preis"]),"","","",d["Kinderfreundlich"],"",d["Reservierung"],d["Website"],d["Lat"],d["Lng"],d["Hinweis"]])
    for d in akt:
        w.writerow([such(d),"Aktivität",d["Etappe"],d["Name"],d["Adresse"],d["Ort"],d["Bewertung"],d["Reviews"],
                    d["Kategorie"],d["Preis"],d["Dauer"],d["Kinderwagen"],d["Mindestalter"],d["Warum"],d["BesteZeit"],d["Buchung"],d["Website"],d["Lat"],d["Lng"],d["Hinweis"]])
print("CSV:",len(rest)+len(akt),"Zeilen")

E=html.escape
def ratechip(d):
    b=d["Bewertung"].strip(); rev=d["Reviews"].strip()
    if not b: return '<span class="rate none" title="Aus euren Unterlagen oder Lodge-Angabe – Bewertung nicht geprüft">★ ungeprüft</span>'
    v=float(b); cls="rate high" if v>=4.5 else ("rate" if v>=4.2 else "rate low")
    out=f'<span class="{cls}">★ {b.replace(".",",")}</span>'
    if rev: out+=f'<span class="revs">{format(int(rev),",").replace(",","’")}</span>'
    return out
def warnp(note):
    return any(k in note for k in ["ACHTUNG","unbestätigt","MONTAGS","SONNTAGS ZU","SO ZU","Mo zu","Mo geschlossen","GESCHLOSSEN","geschlossen","Dienstags geschlossen","NUR Fr","nicht machbar","nicht erlaubt","nicht mit Kindern","zu prüfen","vorab klären","vorab prüfen","anrufen"])

def card_rest(c,i):
    note=c["Hinweis"].strip(); web=c["Website"].strip()
    return f'''<article class="card" data-q="{E(qpt(c))}" data-lat="{c['Lat'].strip()}" data-lng="{c['Lng'].strip()}" data-name="{E(c['Name'])}" data-ort="{E(c['Ort'])}" data-et="{snum(c['Etappe'])}" data-typ="rest" data-dauer="90" data-r="{c['Bewertung'] or 0}" data-play="{'1' if any(k in (c['Kinderfreundlich']+note).lower() for k in ['spielplatz','spielbereich','spielzimmer','klettergerüst','spielmöglich']) else '0'}" data-s="{E((c['Name']+' '+c['Ort']+' '+c['Kategorie']+' '+c['Kinderfreundlich']+' '+note).lower())}">
<button class="planbtn" data-id="r{i}" aria-label="In den Kalender eintragen" title="In den Kalender eintragen">✓</button>
<button class="fav" data-id="r{i}" aria-label="Merken" title="Merken">☆</button>
<h3>{E(c["Name"])}</h3>
<div class="meta">{ratechip(c)}<span class="cat">{E(c["Kategorie"])}</span><span class="pr">{price(c["Preis"])}</span></div>\n<div class="meta"><span class="prz">{_restzar(c["Preis"])}</span></div>
<p class="kid">{E(c["Kinderfreundlich"])}</p>
<p class="addr">{E(c["Adresse"])} · {E(c["Ort"])}</p>
{f'<p class="note{" warn" if warnp(note) else ""}">{E(note)}</p>' if note else ''}
<div class="foot"><span class="res">Reservierung: {E(c["Reservierung"]) if c["Reservierung"].strip() else "—"}</span>
<span class="links"><a class="lnk map" href="{murl(c)}" target="_blank" rel="noopener">Route</a>{f'<a class="lnk" href="{E(web)}" target="_blank" rel="noopener">Web</a>' if web else ''}</span></div></article>'''

_HART = ("treppe","steil","fels","stufen","kraxe","hängebrücke","wurzel","sand")
def _weg(v):
    t=(v or "").strip()
    low=t.lower()
    rest=t
    for pre in ("Ja - ","Ja – ","Ja, ","Ja mit Einschränkung - ","Nein - ","NEIN - ","Nein – ",
                "Teilweise - ","Teilweise – ","Bedingt - ","Überwiegend ja - ","Grösstenteils ja - ",
                "Oben bedingt - ","Eingeschränkt - ","Irrelevant - "):
        if t.startswith(pre): rest=t[len(pre):]; break
    if rest==t:
        for w in ("Ja","NEIN","Nein","Teilweise","Bedingt","Irrelevant"):
            if t==w or t.startswith(w+" "): rest=t[len(w):].strip(" -–,") or ""
    if low.startswith("irrelevant"): return ("im eigenen Auto","ok")
    hart = any(w in low for w in _HART)
    if not rest:
        rest = "befestigt und flach" if low.startswith("ja") else "gemischt"
    cls = "no" if hart else ("ok" if low.startswith(("ja","überwiegend","grösstenteils")) else "mid")
    return (rest[:1].upper()+rest[1:], cls)

def _dauermin(t):
    t=(t or "").lower()
    m=_re.search(r"(\d+)\s*[-–]\s*(\d+(?:[.,]\d+)?)\s*std", t)
    if m: return int(float(m.group(2).replace(",","."))*60)
    m=_re.search(r"(\d+(?:[.,]\d+)?)\s*std", t)
    if m: return int(float(m.group(1).replace(",","."))*60)
    m=_re.search(r"(\d+)\s*[-–]\s*(\d+)\s*min", t)
    if m: return int(m.group(2))
    m=_re.search(r"(\d+)\s*min", t)
    if m: return int(m.group(1))
    return 90

def _zar(v, cls=""):
    if v is None: return '<span class="zar none">Preis offen</span>'
    if v == 0: return '<span class="zar free">gratis</span>'
    txt = f"R {v:,.0f}".replace(",", "\u2009")
    return f'<span class="zar {cls}" data-zar="{v:.0f}">{txt}<i></i></span>'

def _preisrow(c):
    e,k,note = _pparse(c["Name"], c["Preis"])
    fam = _pfam(e,k)
    if fam is None:
        body = '<span class="zar none">Preis nicht bestätigt</span>'
    elif fam == 0:
        body = '<b class="famprice"><span class="zar free">gratis</span></b>'
    else:
        det=[]
        if e: det.append("Erw. "+_zar(e))
        if k: det.append("Kind "+_zar(k))
        elif e and k==0: det.append("Kind gratis")
        body = '<b class="famprice">Familie '+_zar(fam,"big")+'</b>' + ('<span class="pdet">'+" · ".join(det)+'</span>' if det else "")
    hint = '<span class="pdet">'+E(note)+'</span>' if note else ""
    return '<p class="preis">'+body+hint+'</p>'

_RESTBAND = {"E":(90,150),"EE":(160,300),"EEE":(310,520),"E-EE":(110,240),"EE-EEE":(220,420)}
def _restzar(p):
    b = _RESTBAND.get((p or "").strip())
    if not b: return ""
    lo, hi = b
    a, z = 2*lo+lo*0.6, 2*hi+hi*0.6
    txt = f"≈ R {a:,.0f}–{z:,.0f}".replace(",", "\u2009")
    return f'<span class="zar est" data-zar="{(a+z)/2:.0f}">{txt}<i></i></span>'

def card_akt(c,i):
    note=c["Hinweis"].strip(); web=c["Website"].strip()
    kw, kwc = _weg(c["Kinderwagen"]); ma=c["Mindestalter"].strip()
    mac="no" if any(k in ma for k in ["MINDESTALTER 2","ab 4","ab 6","ab 9","ab 10","ab 14","4 Jahre","6 Jahre"]) else "ok"
    return f'''<article class="card" data-q="{E(qpt(c))}" data-lat="{c['Lat'].strip()}" data-lng="{c['Lng'].strip()}" data-name="{E(c['Name'])}" data-ort="{E(c['Ort'])}" data-et="{snum(c['Etappe'])}" data-typ="akt" data-dauer="{_dauermin(c['Dauer'])}" data-r="{c['Bewertung'] or 0}" data-play="{'1' if 'spielplatz' in (c['Warum']+note+c['Kategorie']).lower() or 'Spielplatz' in c['Kategorie'] else '0'}" data-s="{E((c['Name']+' '+c['Ort']+' '+c['Kategorie']+' '+c['Warum']+' '+note+' '+ma).lower())}">
<button class="planbtn" data-id="a{i}" aria-label="In den Kalender eintragen" title="In den Kalender eintragen">✓</button>
<button class="fav" data-id="a{i}" aria-label="Merken" title="Merken">☆</button>
<h3>{E(c["Name"])}</h3>
<div class="meta">{ratechip(c)}<span class="cat">{E(c["Kategorie"])}</span></div>
<div class="specs">
 <span class="spec"><b>Dauer</b>{E(c["Dauer"])}</span>
 <span class="spec kw-{kwc}"><b>Weg</b>{E(kw)}</span>
 <span class="spec ma-{mac}"><b>Alter</b>{E(ma)}</span>
</div>
<p class="kid">{E(c["Warum"])}</p>
<p class="addr">{E(c["Adresse"])} · {E(c["Ort"])}</p>
{_preisrow(c)}
<p class="addr"><b>Beste Zeit</b> {E(c["BesteZeit"])}</p>
{f'<p class="note{" warn" if warnp(note) else ""}">{E(note)}</p>' if note else ''}
<div class="foot"><span class="res">Buchung: {E(c["Buchung"]) if c["Buchung"].strip() else "—"}</span>
<span class="links"><a class="lnk map" href="{murl(c)}" target="_blank" rel="noopener">Route</a>{f'<a class="lnk" href="{E(web)}" target="_blank" rel="noopener">Web</a>' if web else ''}</span></div></article>'''

def stagesec(items,builder,pref):
    out=[]
    for k,(t,dates,base) in STAGES.items():
        sub=[c for c in items if snum(c["Etappe"])==k]
        if not sub: continue
        cards="".join(builder(c,f"{pref}{k}{n}") for n,c in enumerate(sub))
        o,dst = ENDS.get(k,("",""))
        out.append(f'''<section class="stage" id="{pref}e{k}" data-origin="{E(o)}" data-dest="{E(dst)}">
<header class="sh"><span class="snum">{k}</span><div><h2>{E(t)}</h2><p class="dates">{E(dates)}</p><p class="base">{E(base)}</p></div><span class="count">{len(sub)}</span></header>
<div class="tourbar"><button class="tourbtn" type="button">Route in Google Maps öffnen</button><span class="tourhint"></span></div>
<div class="grid">{cards}</div></section>''')
    return "\n".join(out)

# ---------- Plan ----------
import re as _re
def daynum_of(dat): return int(_re.search(r'(\d+)\.\s*Okt', dat).group(1))
ICON={"fahrt":"→","buchung":"✓","checkin":"⌂","checkout":"⌂","tipp":"·","warnung":"!","frei":"~"}
dayhtml=[]
for (dat,st,titel,sub,typ,items) in DAYS:
    rows=[]
    _dn = daynum_of(dat)
    _sd = _daysun.get(f'2026-10-{_dn:02d}', {})
    _suntxt = (f"☀ {_sd.get('auf','')} – {_sd.get('unter','')}  ·  {_sd.get('ort','')}" if _sd.get('auf') else '')
    for _i,it in enumerate(items):
        z,art,t,d = it[0],it[1],it[2],it[3]
        rows.append(f'''<li class="it {art}" data-id="d{_dn}i{_i}" data-art="{art}"><span class="tm">{E(z) or "&nbsp;"}</span><span class="ic" aria-hidden="true">{ICON[art]}</span>
<span class="tx"><b>{E(t)}</b>{f'<span class="dt">{d}</span>' if d else ''}</span></li>''')
    dayhtml.append(f'''<article class="day {typ}" data-d="2026-10-{_dn:02d}">
<header class="dh"><div><span class="dd">{E(dat)}</span><h3>{E(titel)}</h3><p>{E(sub)}</p><span class="sun">{_suntxt}</span></div><span class="et">Etappe {st}</span></header>
<ul class="tl">{"".join(rows)}</ul></article>''')

# ---------- Info ----------
# --- Vorbereitungs-Checkliste aus prep.py ---
import datetime as _dt
_WT=["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
_gr, _order = {}, []
for (pid,pd,ptit,pdet,purg) in PREP:
    if pd not in _gr: _gr[pd]=[]; _order.append(pd)
    _gr[pd].append((pid,ptit,pdet,purg))
_dep=_dt.date(2026,10,4)
_blocks=[]
for pd in _order:
    _d=_dt.date.fromisoformat(pd); _w=(_dep-_d).days
    _lead = ("Abreisetag" if _w==0 else
             ("1 Tag vor Abflug" if _w==1 else
              (f"{_w} Tage vor Abflug" if _w<14 else f"{_w//7} Wochen vor Abflug")))
    def _plink(pid):
        ls = PREPLINKS.get(pid)
        if not ls: return ""
        _ic = {"pdf":"\u2b07\ufe0e", "web":"\u2197"}
        _parts = []
        for (lab,u,k) in ls:
            _attr = ' target="_blank" rel="noopener"'
            _sym = _ic.get(k, "\u2197")
            _parts.append('<a class="plk ' + k + '" href="' + u + '"' + _attr + '>'
                          + _sym + ' ' + E(lab) + '</a>')
        a = "".join(_parts)
        return f'<div class="plks">{a}</div>'
    _items="".join(
      f'<li class="pt{" urg" if u else ""}"><label><input type="checkbox" class="pchk" data-p="{pid}">'
      f'<span><b>{E(t)}</b><em>{E(dt)}</em></span></label>{_plink(pid)}</li>'
      for (pid,t,dt,u) in _gr[pd])
    _blocks.append(f'<div class="pgrp"><h4><span class="pdate">{_d.day}. {["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"][_d.month-1]}</span>'
                   f'<span class="plead">{_WT[_d.weekday()]} · {_lead}</span></h4><ul class="plist">{_items}</ul></div>')
_ANRUF = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_anruf.txt'),encoding='utf-8').read()
_ANRUF = _ANRUF.split('"""',1)[1].rsplit('"""',1)[0] if '"""' in _ANRUF else _ANRUF
PREPLIST = ('<p class="sub">Diese Punkte stecken auch im abonnierten Kalender – jeweils um 9 Uhr mit Erinnerung. '
            'Abgehakt wird hier, gespeichert in diesem Browser.</p>'
            '<div class="prepbar"><span id="prepcount"></span><button type="button" class="btn" id="prepreset">Haken zurücksetzen</button></div>'
            + "".join(_blocks))

CHECKPANEL = ('<section class="igrp" id="i-todo"><h2>Checkliste</h2>'
  '<div class="isec">' + PREPLIST + '</div>'
  + '''<details class="isec fold" id="syncbox"><summary><span class="foldt">Geräte-Abgleich</span><div class="syncstate none" id="syncstate">◌ aus</div></summary>
<p class="sub">Ohne Abgleich gelten Haken, Kalenderänderungen und Merkliste nur in dem Browser, in dem du sie gesetzt hast – iPad und PC führen dann getrennte Listen. Mit Abgleich halten alle Geräte denselben Stand.</p>
<div class="btnrow">
 <button type="button" class="btn solid" id="syncon">Abgleich einschalten</button>
 <button type="button" class="btn" id="syncnow" hidden>Jetzt abgleichen</button>
 <button type="button" class="btn" id="synclink" hidden>Link fürs zweite Gerät kopieren</button>
 <button type="button" class="btn" id="syncjoin">Bestehenden Schlüssel eintragen</button>
 <button type="button" class="btn danger" id="syncoff" hidden>Abgleich ausschalten</button>
</div>
<div id="syncjoinrow" hidden>
 <input id="synckeyin" type="text" inputmode="latin" autocomplete="off" spellcheck="false" placeholder="Schlüssel vom ersten Gerät">
 <button type="button" class="btn solid" id="syncjoingo">Übernehmen</button>
</div>
<p class="hint" id="synckeyline" hidden></p>
<p class="hint"><b>So geht es:</b> auf einem Gerät einschalten, dort <i>Link fürs zweite Gerät kopieren</i> und sich den Link selbst schicken. Auf dem zweiten Gerät den Link öffnen – fertig. Danach gleicht sich alles von selbst ab, beim Öffnen der Seite und während sie offen ist.</p>
<p class="hint"><b>Was gespeichert wird:</b> nur Haken der Checkliste, deine Kalenderänderungen, die Merkliste und die Budget-Einstellungen. Keine Namen, keine Passdaten. Der Schlüssel ist das Passwort – wer ihn hat, sieht diesen Stand. Offline funktioniert alles weiter, der Abgleich holt es nach. <b>Im Claude-Vorschaufenster ist der Abgleich blockiert</b> – er läuft nur auf der richtigen Seite auf github.io.</p></details>'''
  '<div class="isec"><h3>Vor Ort kurz anrufen</h3>' + _ANRUF + '</div></section>')

infohtml=[]
for (grp,gid,secs) in INFO:
    body="".join(f'<div class="isec"><h3>{E(t)}</h3>{c.replace("__PREPLIST__",PREPLIST)}</div>' for (t,c) in secs)
    infohtml.append(f'<section class="igrp" id="i-{gid}"><h2>{E(grp)}</h2>{body}</section>')
infonav="".join(f'<a href="#i-{gid}">{E(grp)}</a>' for (grp,gid,_) in INFO)

nav_r="".join(f'<a href="#re{k}"><b>{k}</b>{E(v[0])}</a>' for k,v in STAGES.items())
nav_a="".join(f'<a href="#ae{k}"><b>{k}</b>{E(v[0])}</a>' for k,v in STAGES.items())

CALJSON = _json.dumps({"timed":_timed,"allday":_allday,"stays":_stays}, ensure_ascii=False, separators=(",",":"))

# ---------- Handschuhfach-Seite ----------
_ROWS_UNTERKUNFT=[
 ("Adamsgarth Guesthouse","26 Mount Rhodes Drive, Hout Bay","4.–8.10.",""),
 ("Adara Palmiet Valley Estate","Sonstraal Road, Klein Drakenstein, Paarl","8.–11.10.",""),
 ("Rivergate Guest Farm","Wortelgat Road, Stanford","11.–14.10.",""),
 ("Melozhori Game Reserve","R317, Stormsvlei","14.–16.10.","+27 66 595 7823"),
 ("Emily Moon River Lodge","Rietvlei Road, Plettenberg Bay","16.–20.10.",""),
 ("Woodall Country House & Spa","Jan Smuts Avenue, Addo","20.–23.10.","+27 42 233 0128"),
 ("Lalibela Mark's Camp","Lalibela Game Reserve, N2, Paterson","23.–26.10.","+27 87 550 1885"),
]
_ROWS_FAHRT=[
 ("So 4.10.","Flughafen CPT → Hout Bay","33 km","50–60 Min"),
 ("Do 8.10.","Hout Bay → Paarl","79 km","1:20–1:30 h"),
 ("So 11.10.","Paarl → Stanford","158 km","3:00–3:15 h"),
 ("Mi 14.10.","Stanford → Melozhori","91 km","1:35–1:45 h"),
 ("Fr 16.10.","Melozhori → Plettenberg Bay","350 km","5:45–6:30 h"),
 ("Di 20.10.","Plett → Woodall, Addo","272–311 km","4:45–5:15 h"),
 ("Fr 23.10.","Woodall → Lalibela","68 km","1:15–1:25 h"),
 ("Mo 26.10.","Lalibela → Flughafen Gqeberha","96 km","1:35–1:50 h"),
]
_ROWS_NOT=[("Notruf Handy","112"),("Rettungsdienst","10177"),("Polizei","10111"),
 ("Feuerwehr Kapstadt","021 461 5555"),("Berg- und Seenotrettung","021 937 0300"),
 ("Seenotrettung NSRI","087 094 9774"),("Tafelberg-Nationalpark","086 110 6417"),
 ("Schweizer Konsulat Kapstadt","021 400 7500"),("Touristenhilfe Westkap","+27 82 554 2010"),
 ("Touristenhilfe Garden Route","+27 82 972 2507"),("African Twist Travel (WhatsApp)","+41 76 466 6140"),
 ("Europcar (WhatsApp)","+27 86 113 1000")]
_ROWS_BUCH=[("Do 8.10. 18:30","Adara Restaurant"),("Fr 9.10. 12:30","Deli Boschendal"),
 ("Sa 10.10. 12:30","Tokara Delicatessen"),("Di 13.10. 09:00","Whale Watching (3 Std.)")]
def _tbl(rows):
    out=[]
    for (a,b,c,d) in rows:
        tel = ("<br>"+E(d)) if d else ""
        out.append("<tr><td><b>"+E(a)+"</b><br><span style='color:#666'>"+E(b)+"</span></td><td>"+E(c)+tel+"</td></tr>")
    return "".join(out)
PRINTCARD = f'''<section id="printcard">
<div class="pc-h"><h1>Südafrika · 4.–26. Oktober 2026</h1>
<p>Notfallkarte fürs Handschuhfach · salsafever21.github.io/southafrica</p></div>
<div class="pc-grid">
 <div class="pc-box"><h2>Notruf</h2><table>{"".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a,b in _ROWS_NOT)}</table></div>
 <div class="pc-box"><h2>Feste Buchungen</h2><table>{"".join(f"<tr><td>{E(b)}</td><td>{E(a)}</td></tr>" for a,b in _ROWS_BUCH)}</table>
  <h2 style="margin-top:10px">Wichtig</h2>
  <table><tr><td>Linksverkehr · Alkohol 0,05 ‰ · nachts nicht fahren</td><td></td></tr>
  <tr><td>Addo &amp; Nationalparks: Ausweis mitbringen</td><td></td></tr>
  <tr><td>Lalibela: Kinder unter 2 nicht auf Safari</td><td></td></tr></table></div>
 <div class="pc-box pc-wide"><h2>Unterkünfte</h2><table>{_tbl(_ROWS_UNTERKUNFT)}</table></div>
 <div class="pc-box pc-wide"><h2>Fahrten (realistisch mit Kindern)</h2>
  <table>{"".join(f"<tr><td><b>{E(a)}</b> {E(b)} · {E(c)}</td><td>{E(d)}</td></tr>" for a,b,c,d in _ROWS_FAHRT)}</table></div>
</div>
<p class="pc-f">Trinkgeld: Parkwächter 5–10 R · Tankwart 5–10 R · Restaurant 10 % · Lodge-Guide 150–200 R pro Fahrt. Leitungswasser trinkbar. Route malariafrei.</p>
</section>'''

# ---------- Routenkarte + Zeitstrahl ----------
_rows=[]
for i,(lab,km,dur,pts) in enumerate(_karte.LEGS):
    _rows.append(f'<li class="rt-leg"><span class="rt-ico">→</span><div><b>{E(lab)}</b>'
                 f'<em>{km} km · {E(dur)}</em></div></li>')
    if i < len(_karte.STOPS):
        (L,name,ort,n,dat,la,lo) = _karte.STOPS[i]
        _q = urllib.parse.quote(f"{name}, {ort}, Südafrika")
        _rows.append(f'<li class="rt-stop" data-stop="{L}" tabindex="0"><span class="rt-let">{L}</span>'
                     f'<div><b>{E(name)}</b><em>{E(ort)} · {E(n)} · {E(dat)}</em>'
                     f'<a class="lnk map" href="https://www.google.com/maps/search/?api=1&query={_q}" target="_blank" rel="noopener">Karte</a></div></li>')
_gesamt = sum(l[1] for l in _karte.LEGS)
ROUTE = ('<div class="mapbox">' + _karte.build() + '</div>'
  f'<p class="mapnote">Sieben Unterkünfte, {len(_karte.LEGS)} Fahrten, zusammen rund {_gesamt} km. '
  'Auf einen Buchstaben tippen – auf der Karte oder in der Liste.</p>'
  '<ol class="rt">' + "".join(_rows) + '</ol>')

# ---------- Budget-Vorgaben ----------
_KM_ROUTE = sum(l[1] for l in _karte.LEGS)
_KM_LOKAL = 1270
_LITER = round((_KM_ROUTE+_KM_LOKAL) * 8 / 100)
_BUDGET = {
 "kurs": round(1/_KURS, 2),
 "lines": [
  {"id":"l1","t":"Restaurants (22 Tage, ca. R600/Tag)","z":13200,"p":False},
  {"id":"l2","t":f"Treibstoff ({_KM_ROUTE+_KM_LOKAL} km, 8 l/100 km, R{_BENZIN:.2f}/l)","z":round(_LITER*_BENZIN),"p":False},
  {"id":"l3","t":"Trinkgeld (R80/Tag)","z":1840,"p":False},
  {"id":"l4","t":"Lebensmittel und Selbstverpflegung","z":2500,"p":False},
  {"id":"l5","t":"Souvenirs und Puffer","z":3000,"p":False},
  {"id":"l6","t":"Melozhori Semi-Catering (2 Nächte, optional)","z":4400,"p":False},
  {"id":"l7","t":"Unterkünfte, Flüge, Mietwagen (vorausbezahlt)","z":0,"p":True},
 ]}
BUDJSON = _json.dumps(_BUDGET, ensure_ascii=False, separators=(",",":"))

TPL=open('./tpl.html',encoding='utf-8').read()
out=(TPL.replace("__PLAN__","".join(dayhtml))
       .replace("__NAVR__",nav_r).replace("__RESTS__",stagesec(rest,card_rest,"r"))
       .replace("__NAVA__",nav_a).replace("__AKTS__",stagesec(akt,card_akt,"a"))
       .replace("__INFONAV__",infonav).replace("__INFO__","".join(infohtml))
       .replace("__NR__",str(len(rest))).replace("__NA__",str(len(akt)))
       .replace("__CALJSON__",CALJSON).replace("__PRINTCARD__",PRINTCARD).replace("__CHECK__",CHECKPANEL).replace("__ROUTE__",ROUTE).replace("__BUDJSON__",BUDJSON))
PAGES_BASE = "https://salsafever21.github.io/southafrica/"
_out_art = out.replace('href="docs/sars-reiseerklaerung.pdf"',
                       'href="' + PAGES_BASE + 'docs/sars-reiseerklaerung.pdf"')
open('./suedafrika-reise.html','w',encoding='utf-8').write(_out_art)
print("HTML (Artifact):",len(_out_art))

# ---------- Standalone-Seite fuer GitHub Pages ----------
import os, re
head, body = out.split('</style>',1)
title = re.search(r'<title>(.*?)</title>', head).group(1)
head = head.replace('<title>'+title+'</title>','')
FAV = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%A6%93%3C/text%3E%3C/svg%3E"
page = f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="Reisebegleiter Südafrika Oktober 2026 – Tagesplan, Restaurants, Aktivitäten für Kinder, Sicherheitsinfos.">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0F5257" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#101715" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{FAV}">
<link rel="apple-touch-icon" href="icon-192.png">
<link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Südafrika">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
{head.strip()}</style>
</head>
<body>
{body.strip()}
</body>
</html>'''
os.makedirs('./repo/data',exist_ok=True)
open('./repo/index.html','w',encoding='utf-8').write(page)
print("HTML (Pages):",len(page))

# ---------- Service Worker ----------
import hashlib as _hl
_ver = _hl.sha1(page.encode('utf-8')).hexdigest()[:10]
_sw = """// Automatisch erzeugt – nicht von Hand bearbeiten.
const V = 'suedafrika-__VER__';
const SHELL = ['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png',
               './reise.ics','./docs/sars-reiseerklaerung.pdf',
               './data/Suedafrika_Restaurants_und_Aktivitaeten.csv'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(SHELL).catch(()=>{})).then(()=>self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks =>
    Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const font = url.host === 'fonts.googleapis.com' || url.host === 'fonts.gstatic.com';

  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => {
      const cp = r.clone(); caches.open(V).then(c => c.put('./index.html', cp)); return r;
    }).catch(() => caches.match('./index.html').then(r => r || caches.match('./'))));
    return;
  }
  if (font) {
    e.respondWith(caches.match(req).then(hit => {
      const net = fetch(req).then(r => { const cp = r.clone(); caches.open(V).then(c => c.put(req, cp)); return r; }).catch(()=>hit);
      return hit || net;
    }));
    return;
  }
  if (url.origin === location.origin) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
      const cp = r.clone(); caches.open(V).then(c => c.put(req, cp)); return r;
    }).catch(()=>hit)));
  }
});
""".replace('__VER__', _ver)
open('./repo/sw.js','w',encoding='utf-8').write(_sw)
print("Service Worker:", _ver)
