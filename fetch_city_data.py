"""Download the Comune di Milano open data used for "Uffici vicino a te" into city_data/.

Addresses are looked up locally, so a person's address never leaves our server.

  python fetch_city_data.py
"""
import json
from pathlib import Path

import requests

CKAN = "https://dati.comune.milano.it/api/3/action/"
OUT = Path(__file__).parent / "city_data"


def records(dataset_id: str, fields: list[str] | None = None) -> list[dict]:
    pkg = requests.get(CKAN + "package_show", params={"id": dataset_id}, timeout=30).json()["result"]
    res = next(r for r in pkg["resources"] if r.get("datastore_active"))
    rows, offset = [], 0
    while True:
        params = {"resource_id": res["id"], "limit": 32000, "offset": offset}
        if fields:
            params["fields"] = ",".join(fields)
        page = requests.get(CKAN + "datastore_search", params=params, timeout=120).json()["result"]["records"]
        rows += page
        if len(page) < 32000:
            return rows
        offset += 32000


def main() -> None:
    OUT.mkdir(exist_ok=True)

    # ds634: street numbers with coordinates -> compact rows [street, number, municipio, nil, lat, lon]
    civ = records("ds634-numeri-civici-coordinate",
                  ["TIPO", "DESCRITTIVO", "NUMEROCOMPLETO", "MUNICIPIO", "NIL", "LAT_WGS84", "LONG_WGS84", "STATOCIVICO"])
    compact = [[f"{r['TIPO']} {r['DESCRITTIVO']}".strip(), r["NUMEROCOMPLETO"].strip(), r["MUNICIPIO"], r["NIL"],
                float(r["LAT_WGS84"]), float(r["LONG_WGS84"])]
               for r in civ if r.get("LAT_WGS84") and r.get("STATOCIVICO") != "Soppresso"]
    (OUT / "civici.json").write_text(json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    print(f"civici: {len(compact)} addresses")

    # ds549: registry offices (anagrafe) with hours and booking rules
    (OUT / "anagrafe.json").write_text(json.dumps(records("ds549-sedi-dei-servizi-anagrafici"), ensure_ascii=False, indent=1))
    # ds1299: municipio headquarters
    (OUT / "municipi.json").write_text(json.dumps(records("ds1299-sedi-municipi-nel-comune-di-milano"), ensure_ascii=False, indent=1))
    print("anagrafe, municipi: ok")


if __name__ == "__main__":
    main()
