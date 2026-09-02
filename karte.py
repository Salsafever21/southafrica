# -*- coding: utf-8 -*-
"""Erzeugt eine eigenstaendige SVG-Routenkarte (keine externen Kartendienste)."""
import json, math, os

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1000, 430
LON0, LON1 = 17.6, 27.3
LAT0, LAT1 = -32.75, -35.05          # oben, unten
K = math.cos(math.radians(-33.8))  # Breitengrad-Stauchung

def px(lon, lat):
    x = (lon - LON0) / (LON1 - LON0) * W
    y = (lat - LAT0) / (LAT1 - LAT0) * H
    return x, y

# Massstabsgetreu halten: Hoehe aus dem Seitenverhaeltnis ableiten
_H = W * ((LAT0 - LAT1) / (LON1 - LON0)) / K
H = round(_H)

STOPS = [
 ("A","Adamsgarth Guesthouse","Hout Bay, Kapstadt","4 Nächte","4.–8. Okt", -34.0333, 18.3592),
 ("B","Adara Palmiet Valley Estate","Paarl","3 Nächte","8.–11. Okt", -33.7660, 18.9580),
 ("C","Rivergate Guest Farm","Stanford, Whale Coast","3 Nächte","11.–14. Okt", -34.4295, 19.4220),
 ("D","Melozhori Game Reserve","Stormsvlei, Overberg","2 Nächte","14.–16. Okt", -34.0370, 20.0870),
 ("E","Emily Moon River Lodge","Plettenberg Bay","4 Nächte","16.–20. Okt", -34.0553, 23.3716),
 ("F","Woodall Country House","Addo, Sundays River Valley","3 Nächte","20.–23. Okt", -33.5006, 25.6838),
 ("G","Lalibela Mark's Camp","Paterson","3 Nächte","23.–26. Okt", -33.3000, 26.0600),
]
LEGS = [
 ("Flughafen Kapstadt → Hout Bay", 33, "50–60 Min", [(-33.9715,18.6021),(-34.0000,18.4200),(-34.0333,18.3592)]),
 ("Hout Bay → Paarl", 79, "1:20–1:30 h", [(-34.0333,18.3592),(-33.9249,18.4241),(-33.8869,18.6969),(-33.7660,18.9580)]),
 ("Paarl → Stanford", 158, "3:00–3:15 h", [(-33.7660,18.9580),(-34.0800,18.8500),(-34.1450,18.9500),(-34.2200,19.2000),(-34.4200,19.2400),(-34.4295,19.4220)]),
 ("Stanford → Melozhori", 91, "1:35–1:45 h", [(-34.4295,19.4220),(-34.3000,19.6000),(-34.1500,19.9000),(-34.0900,20.0000),(-34.0370,20.0870)]),
 ("Melozhori → Plettenberg Bay", 350, "5:45–6:30 h", [(-34.0370,20.0870),(-34.0200,20.4400),(-34.0900,21.2600),(-34.1800,22.1400),(-33.9600,22.4600),(-33.9900,22.7000),(-34.0400,23.0500),(-34.0553,23.3716)]),
 ("Plettenberg Bay → Addo", 290, "4:45–5:15 h", [(-34.0553,23.3716),(-33.9700,23.8800),(-34.0300,24.7700),(-33.9600,25.6000),(-33.7500,25.6500),(-33.5006,25.6838)]),
 ("Addo → Lalibela", 68, "1:15–1:25 h", [(-33.5006,25.6838),(-33.4300,25.9600),(-33.3000,26.0600)]),
 ("G → Flughafen Gqeberha", 96, "1:35–1:50 h", [(-33.3000,26.0600),(-33.6000,25.8000),(-33.9850,25.6170)]),
]
ORTE = [
 ("Kapstadt", -33.640, 18.640, "n", 0), ("Swellendam", -34.022, 20.441, "n", 2),
 ("Mossel Bay", -34.183, 22.146, "s", 1), ("George", -33.963, 22.461, "n", 1),
 ("Knysna", -34.036, 23.048, "s", 2), ("Gqeberha", -33.958, 25.600, "se", 1),
 ("Storms River", -33.977, 23.885, "s", 2), ("Oudtshoorn", -33.595, 22.201, "n", 2),
 ("Riversdale", -34.092, 21.257, "n", 2),

]

def land_paths():
    g = json.load(open(os.path.join(BASE,'za10.json')))
    out = []
    for name, geom in g.items():
        polys = geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
        for poly in polys:
            for ring in poly:
                pts = [px(lon,lat) for lon,lat in ring]
                if len(pts) > 3:
                    keep=[pts[0]]
                    for q in pts[1:]:
                        if abs(q[0]-keep[-1][0])+abs(q[1]-keep[-1][1]) > 0.8: keep.append(q)
                    keep.append(pts[-1]); pts=keep
                if len(pts) < 3: continue
                # nur Ringe, die den Ausschnitt beruehren
                if all(x < -60 or x > W+60 or y < -60 or y > H+60 for x,y in pts): continue
                d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x,y in pts) + "Z"
                out.append((name, d))
    return out

def route_path(pts):
    p = [px(lon,lat) for lat,lon in pts]
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x,y in p)

def build():
    land = land_paths()
    svg = [f'<svg class="mapsvg" viewBox="0 0 {W} {H}" role="img" aria-label="Routenkarte Südafrika" preserveAspectRatio="xMidYMid meet">']
    svg.append('<rect class="m-sea" x="0" y="0" width="%d" height="%d"/>' % (W,H))
    for name, d in land:
        cls = "m-land" + (" m-land2" if name!="South Africa" else "")
        svg.append(f'<path class="{cls}" d="{d}"/>')
    # Route
    for i,(lab,km,dur,pts) in enumerate(LEGS):
        svg.append(f'<path class="m-route" d="{route_path(pts)}" data-leg="{i}"/>')
    # Orte
    for (n,lat,lon,pos,prio) in ORTE:
        x,y = px(lon,lat)
        dy = -8 if pos=="n" else (15 if pos in ("s","se") else 4)
        anchor = "middle" if pos=="s" else ("end" if pos=="w" else "start")
        dx = 0 if pos=="s" else (-8 if pos=="w" else 8)
        if pos=="n": anchor, dx = "middle", 0
        if prio: svg.append(f'<circle class="m-town p{prio}" cx="{x:.1f}" cy="{y:.1f}" r="2.4"/>')
        svg.append(f'<text class="m-townlab p{prio if prio else 1}" x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anchor}">{n}</text>')
    # Flughaefen
    for (n,lat,lon) in [("CPT",-33.9715,18.6021),("PLZ",-33.9850,25.6170)]:
        x,y = px(lon,lat)
        svg.append(f'<g class="m-air"><circle cx="{x:.1f}" cy="{y:.1f}" r="7"/>'
                   f'<text x="{x:.1f}" y="{y+3.2:.1f}" text-anchor="middle">✈</text></g>')
    # Stopps
    for (L,name,ort,n,dat,lat,lon) in STOPS:
        x,y = px(lon,lat)
        svg.append(f'<g class="m-pin" data-stop="{L}" tabindex="0" role="button" aria-label="{L} – {name}, {ort}">'
                   f'<circle class="m-pinhit" cx="{x:.1f}" cy="{y:.1f}" r="17"/>'
                   f'<circle class="m-pindot" cx="{x:.1f}" cy="{y:.1f}" r="11"/>'
                   f'<text class="m-pintxt" x="{x:.1f}" y="{y+3.9:.1f}" text-anchor="middle">{L}</text></g>')
    svg.append('</svg>')
    return "\n".join(svg)

if __name__ == "__main__":
    print(build()[:300]); print("...\nHoehe:", H, "Segmente:", len(LEGS), "Gesamt-km:", sum(l[1] for l in LEGS))
