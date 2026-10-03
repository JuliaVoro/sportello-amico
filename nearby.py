"""Find an address in Milan and the nearest Comune offices, using a local copy of the open data.

Data (see fetch_city_data.py): ds634 street numbers, ds549 registry offices, ds1299 municipio offices.
The address is matched on this server only; it is never sent to another service.
"""
import json
import math
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).parent / "city_data"

BOOKING = {
    "pass_new": "https://servizicrm.comune.milano.it/spec/passdisabili/rilascio",
    "pass_renewal": "https://servizicrm.comune.milano.it/spec/passdisabili/rinnovo",
    "id_card": "https://servizicrm.comune.milano.it/spec/appuntamenti/anagrafecie",
    "any_office": "https://servizicrm.comune.milano.it/appuntamenti/crea",
}
# the only office that handles the disability pass (service page "Pass per la sosta e la circolazione…")
PASS_OFFICE = {"name": "Unità Gestione Permessi (pass disabili)", "address": "via Sile 8", "street": "via sile", "number": "8",
               "hours": "lunedì–venerdì 10:00–12:00 e 13:30–15:00, solo su appuntamento",
               "transport": "M3 Brenta o Corvetto · bus 77, 84, 93, 95", "phone": "02 884 52909"}

STOP = {"di", "del", "della", "dello", "dei", "degli", "delle", "de", "d", "da", "al", "alla", "e", "san", "santa", "s"}
ABBREV = {"v.le": "viale", "vle": "viale", "p.za": "piazza", "p.zza": "piazza", "pza": "piazza", "p.le": "piazzale", "pzle": "piazzale",
          "c.so": "corso", "cso": "corso", "l.go": "largo", "v.": "via", "v": "via"}
STREET_TYPES = {"via", "viale", "piazza", "piazzale", "corso", "largo", "galleria", "vicolo", "strada", "alzaia", "ripa",
                "bastioni", "passaggio", "piazzetta", "rotonda", "cavalcavia", "sottopasso", "foro", "porta", "ponte"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = " ".join(ABBREV.get(w, w) for w in s.split())  # expand abbreviations before dropping punctuation
    return re.sub(r"[^a-z0-9 ]+", " ", s).strip()


def tokens(s: str) -> set[str]:
    # name words only: the street type (via, viale…) is compared separately
    return {w for w in norm(s).split() if w not in STOP and w not in STREET_TYPES and not w.isdigit()}


@lru_cache(maxsize=1)
def load():
    civici = json.loads((DATA / "civici.json").read_text())
    streets: dict[str, list] = {}
    for street, number, mun, nil, lat, lon in civici:
        streets.setdefault(street, []).append((number, mun, nil, lat, lon))
    index = {s: tokens(s) for s in streets}
    anagrafe = json.loads((DATA / "anagrafe.json").read_text())
    municipi = json.loads((DATA / "municipi.json").read_text())
    return streets, index, anagrafe, municipi


def km(a, b) -> float:
    dx = (b[1] - a[1]) * 111.32 * math.cos(math.radians(a[0]))
    dy = (b[0] - a[0]) * 110.57
    return round(math.hypot(dx, dy), 1)


def find_address(text: str) -> dict | None:
    streets, index, *_ = load()
    m = re.search(r"\b(\d+\s*[a-z]?)\b\s*$", norm(text))
    number = m.group(1).replace(" ", "") if m else ""
    want = tokens(text[: m.start()] if m else text) if m else tokens(text)
    if not want:
        return None
    best, score = None, 0.0
    for street, toks in index.items():
        if not want <= toks and not (len(want) > 2 and len(want & toks) >= len(want) - 1):
            continue
        s = len(want & toks) / len(toks | want)
        if norm(street).split()[0] in norm(text).split():  # same type: via / viale / piazza…
            s += 0.5
        if s > score:
            best, score = street, s
    if not best:
        return None
    nums = streets[best]
    exact = [n for n in nums if n[0].lower() == number]
    if not exact and number:
        digits = int(re.match(r"\d+", number).group())
        same_parity = [n for n in nums if re.match(r"\d+", n[0]) and int(re.match(r"\d+", n[0]).group()) % 2 == digits % 2] or nums
        exact = [min(same_parity, key=lambda n: abs(int(re.match(r"\d+", n[0]).group() or 0) - digits))]
    hit = (exact or nums)[0]
    return {"street": best.title(), "number": hit[0] if (exact and number) else "", "exact": bool(number) and hit[0].lower() == number,
            "municipio": hit[1], "nil": hit[2].title(), "lat": hit[3], "lon": hit[4]}


def nearby(text: str) -> dict:
    addr = find_address(text)
    if not addr:
        return {"found": False}
    _, _, anagrafe, municipi = load()
    here = (addr["lat"], addr["lon"])
    offices = []
    for o in anagrafe:
        if not o.get("LAT_Y_4326"):
            continue
        offices.append({"name": f"Anagrafe · {o['titolo'] or 'sede'}", "address": o["Indirizzo"], "hours": o.get("orari", ""),
                        "note": o.get("Note", ""), "phone": o.get("telefono", ""),
                        "km": km(here, (float(o["LAT_Y_4326"]), float(o["LONG_X_4326"])))})
    offices.sort(key=lambda o: o["km"])
    mun = next((m for m in municipi if str(m["Municipio"]).startswith(f"Municipio {addr['municipio']}")), None)
    pass_loc = find_address(f"{PASS_OFFICE['street']} {PASS_OFFICE['number']}")
    return {
        "found": True,
        "address": addr,
        "pass_office": {**PASS_OFFICE, "km": km(here, (pass_loc["lat"], pass_loc["lon"])) if pass_loc else None},
        "registry": offices[:3],
        "municipio": mun and {"name": mun["Municipio"], "address": f"{mun['Indirizzo']} {mun['Civico']}", "phone": mun.get("telefono", ""),
                              "email": mun.get("indirizzo mail istituzionale", ""), "transport": mun.get("Mezzi pubblici", ""),
                              "km": km(here, (float(mun["LAT_Y_4326"]), float(mun["LONG_X_4326"])))},
        "booking": BOOKING,
        "source": "Comune di Milano open data: ds634, ds549, ds1299",
    }


if __name__ == "__main__":
    import sys
    print(json.dumps(nearby(" ".join(sys.argv[1:]) or "via padova 118"), ensure_ascii=False, indent=1))
