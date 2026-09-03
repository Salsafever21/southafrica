# -*- coding: utf-8 -*-
"""Preise aus akt.py in Zahlen uebersetzen. Familie = 2 Erwachsene + 1 Kind (4 J.)."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from akt import A as AKT

KURS = 0.050          # 1 ZAR in CHF, Stand 23.08.2026
BENZIN = 24.33        # R pro Liter, 95 Kueste, August 2026
ALTER = 4

# Handkorrekturen dort, wo der Text mehrdeutig ist: name -> (erw, kind, note)
OVERRIDE = {
 "La Colombe": (1695, 0, "Mittagsmenü R1'695 p.P., Kinderpreis noch offen – gebucht Di 6.10. 12:00"),
 "GOLD Restaurant": (560, 560, "14-Gänge-Menü R560 p.P., Kinderpreis auf Anfrage; Anzahlung R750 bereits bezahlt"),
 "Melozhori Game Drive": (0, 0, "1 Fahrt inklusive, weitere R500 p.P."),
 "Melozhori: Spaziergänge & E-Bikes": (0, 0, "Spaziergänge gratis, E-Bike R850/Tag"),
 "Lalibela Mark's Camp - Safari Drives": (0, 0, "im All-Inclusive enthalten"),
 "Lalibela Kinderprogramm (Tiny Trackers)": (0, 0, "im All-Inclusive enthalten"),
 "Spice Route Destination": (0, 0, "Eintritt frei, pro Aktivität zahlen"),
 "Redberry Farm": (0, 0, "Eintritt frei, pro Aktivität zahlen"),
 "Grass Roof Farm - Kids Area": (0, 0, "Kids Area 1 gratis, Area 2 R80/Kind"),
 "Cape Recife Nature Reserve": (32, 0, "R32 pro Fahrzeug"),
 "Addo Cruises & Sand Sledding": (760, 380, "Kinderpreis gilt ab 5 – für 4 J. nachfragen"),
 "Sundays River Adventures - Kurz-Bootsfahrt": (None, None, "Preis unbestätigt"),
 "Daniell Cheetah Project": (115, 60, "geschätzt, Preis nicht publiziert"),
 "Lawnwood Snake Sanctuary": (300, 150, "ab ca. R300, Kinderpreis unbestätigt"),
 "Exotic Animal World (ex Butterfly World)": (160, 160, "geschätzt R150–170 p.P."),
 "Spier Elemental Play Garden": (0, 0, "Geländezugang frei"),
 "Le Bonheur Krokodilfarm": (62, 35, "Teichtour, je nach Alter"),
 "Bugz Family Playpark": (60, 190, "Erwachsene R60, Kind 3–12 R190"),
 "Paarl Mountain Nature Reserve": (0, 0, "werktags gratis, Wochenende R30 p.P."),
 "Lady Stanford Bootsfahrt Klein River": (280, 280, "R280 p.P., Mindestumsatz R1120"),
 "Whale of a Time Play Park": (None, None, "Preis unbestätigt"),
 "KidZone Indoor Play Centre": (None, None, "Preis unbestätigt"),
 "Raptor Rescue Plett": (190, 120, ""),
 "Knysna Elephant Park": (460, 0, "unter 5 Jahren gratis"),
 "Tenikwa - Wild Cat Experience": (275, 160, ""),
 "Storms River Suspension Bridge": (367, 184, "Kind 2–11 halber Preis"),
 "Addo Elephant NP - Selbstfahrer-Safari": (492, 246, "Ausländertarif"),
 "Addo Main Camp - Wasserloch & Underground Hide": (0, 0, "im Parkeintritt enthalten"),
 "Tafelberg-Seilbahn": (475, 230, "online, Berg- und Talfahrt"),
 "Two Oceans Aquarium": (280, 130, ""),
 "Boulders Beach Pinguine": (245, 120, ""),
 "Kirstenbosch + Boomslang": (270, 0, "Kinder unter 6 gratis"),
 "Babylonstoren Farmgarten": (150, 0, "Kinder unter 18 gratis"),
 "Blue Train Park": (35, 35, "inkl. einer Zugfahrt"),
 "Sea Point Pavilion Kinderbecken": (37.5, 22, ""),
 "Imhoff Farm + Higgeldy Piggeldy Farmyard": (20, 20, "Streichelzoo, Gelände gratis"),
 "World of Birds & Monkey Park": (145, 60, ""),
 "Duiker Island Robbenfahrt (40 Min.)": (130, 70, ""),
 "Scratch Patch Simon's Town": (0, 40, "Eintritt frei, Steinbeutel ab R40"),
 "Acrobranch Garden Route - Acro-twigs": (0, 130, "nur das Kind klettert"),
 "Bontebok National Park (Selbstfahrer)": (206, 80, "Ausländertarif"),
 "Marloth Nature Reserve - Koloniesbos": (55, 35, "nur Bargeld"),
 "Viljoensdrift Bootsfahrt Breede River": (120, 50, ""),
 "Drostdy Museum Swellendam": (None, None, "Preis unbestätigt"),
 "Stony Point Pinguinkolonie": (45, 30, ""),
 "Harold Porter Botanical Garden": (30, 0, "Kinder unter 6 gratis"),
 "De Kelders Klippenpfad": (65, 45, ""),
 "Platbos Forest": (50, 20, "Ehrlichkeitskasse"),
 "Robberg Nature Reserve - Gap-Rundweg": (75, 55, ""),
 "Keurbooms River Ferry": (675, 505, ""),
 "Birds of Eden": (440, 220, ""),
 "Monkeyland": (440, 220, ""),
 "Jukani Wildlife Sanctuary": (440, 220, ""),
 "Addo Wildlife Centre": (20, 20, ""),
 "Kragga Kamma Game Park": (140, 70, "Selbstfahrer"),
 "SANCCOB Pinguin-Rehabilitation": (75, 30, "Ausländertarif"),
 "Drakenstein Lion Park": (160, 80, "Ausländertarif"),
 "Afrikaanse Taalmonument": (40, 0, ""),
 "Garden Route Botanical Garden": (15, 15, ""),
 "Bartolomeu Dias Museum": (None, None, "Eintritt unbestätigt"),
 "Vergenoegd Löw Enten-Parade": (0, 0, "Parade gratis"),
}
GRATIS_WORTE = ("gratis","GRATIS","Gratis","Kein Eintritt","kostenlos")

def parse(name, txt):
    if name in OVERRIDE:
        e,k,note = OVERRIDE[name]; return e,k,note
    t = txt or ""
    if not t.strip(): return None, None, ""
    if any(w in t for w in GRATIS_WORTE) and not re.search(r"R\s?\d", t): return 0,0,""
    m_e = re.search(r"R\s?([\d.]+)\s*Erw", t)
    m_k = re.search(r"R\s?([\d.]+)\s*Kind", t)
    m_p = re.search(r"R\s?([\d.]+)\s*p\.?P\.?", t)
    e = float(m_e.group(1)) if m_e else (float(m_p.group(1)) if m_p else None)
    k = float(m_k.group(1)) if m_k else (e if m_p else None)
    frei = re.search(r"unter\s+(\d+)\s*(?:Jahre[n]?\s*)?(?:GRATIS|gratis|Gratis)", t)
    if frei and ALTER < int(frei.group(1)): k = 0
    return e, k, ""

def familie(e,k):
    if e is None: return None
    return 2*e + (k or 0)

def chf(zar):
    return None if zar is None else round(zar*KURS, 1)

def tabelle():
    out=[]
    for row in AKT:
        etappe,name = row[0], row[1]
        preis = row[7]
        e,k,note = parse(name, preis)
        out.append({"etappe":etappe,"name":name,"roh":preis,"erw":e,"kind":k,
                    "fam":familie(e,k),"note":note})
    return out

if __name__ == "__main__":
    t=tabelle()
    ohne=[r for r in t if r["erw"] is None]
    print(f"{len(t)} Aktivitäten · ohne Preis: {len(ohne)}")
    for r in ohne: print("   ?", r["name"], "|", r["roh"][:60])
    fam=[r for r in t if r["fam"]]
    print("teuerste:")
    for r in sorted(fam,key=lambda x:-x["fam"])[:6]:
        print(f"   R{r['fam']:>7.0f}  CHF {chf(r['fam']):>6.1f}  {r['name'][:44]}")
