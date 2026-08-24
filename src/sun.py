# -*- coding: utf-8 -*-
"""Sonnenauf- und -untergang (NOAA), ohne externe Abhaengigkeiten."""
import math, datetime

def _sun(lat, lon, date, tz=2.0, zenith=90.833):
    N = date.timetuple().tm_yday
    out = {}
    for rise in (True, False):
        lngHour = lon / 15.0
        t = N + ((6 if rise else 18) - lngHour) / 24.0
        M = (0.9856 * t) - 3.289
        L = M + (1.916 * math.sin(math.radians(M))) + (0.020 * math.sin(math.radians(2*M))) + 282.634
        L %= 360
        RA = math.degrees(math.atan(0.91764 * math.tan(math.radians(L)))) % 360
        RA += (math.floor(L/90)*90) - (math.floor(RA/90)*90)
        RA /= 15.0
        sinDec = 0.39782 * math.sin(math.radians(L))
        cosDec = math.cos(math.asin(sinDec))
        cosH = (math.cos(math.radians(zenith)) - (sinDec * math.sin(math.radians(lat)))) / (cosDec * math.cos(math.radians(lat)))
        if cosH > 1 or cosH < -1: return None
        H = (360 - math.degrees(math.acos(cosH))) if rise else math.degrees(math.acos(cosH))
        H /= 15.0
        T = H + RA - (0.06571 * t) - 6.622
        UT = (T - lngHour) % 24
        local = (UT + tz) % 24
        out['rise' if rise else 'set'] = int(round(local * 60))
    return out

def times(lat, lon, iso_date, tz=2.0):
    d = datetime.date.fromisoformat(iso_date)
    r = _sun(lat, lon, d, tz)
    if not r: return None
    def f(m): return f"{m//60:02d}:{m%60:02d}"
    return {"auf": f(r['rise']), "unter": f(r['set']), "aufMin": r['rise'], "unterMin": r['set']}

ORTE = {
 "1": ("Hout Bay",         -34.0333, 18.3592),
 "2": ("Paarl",            -33.7660, 18.9580),
 "3": ("Stanford",         -34.4295, 19.4220),
 "4": ("Melozhori",        -34.0370, 20.0870),
 "5": ("Garden Route",     -34.0300, 22.5000),
 "6": ("Plettenberg Bay",  -34.0553, 23.3716),
 "7": ("Addo",             -33.5006, 25.6838),
 "8": ("Lalibela",         -33.3000, 26.0600),
}

if __name__ == "__main__":
    for iso in ["2026-10-04","2026-10-16","2026-10-24","2026-10-26"]:
        for st in ("1","6","8"):
            n,la,lo = ORTE[st]
            t = times(la,lo,iso)
            print(iso, n.ljust(16), "auf", t["auf"], " unter", t["unter"])
