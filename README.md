# Sportello Amico: pass disabili

**Track 02: Assisted procedure.** A friendly counter clerk who helps people prepare the application
for the disability parking pass (CUDE) of the Comune di Milano: easy for older people, and privacy-first.

## The problem and who has it
The online CUDE form has 10 screens. Most rejections and requests for missing documents come from a
few traps:
- a disability report (*verbale*) uploaded without all its pages;
- a GP certificate missing the exact wording required for renewal;
- iPhone photos in HEIC, a format the form does not accept;
- an irreversible delivery choice;
- a plate added without the national CUDE platform choice.

The people applying are often older, have reduced mobility, or are family members acting by delegation.

**Personas:**
- **Lucia** (58) applies for her mother, who has no SPID.
- **Giorgio** (71) renews his own permanent pass.
- **Samira** is a support administrator (*amministratrice di sostegno*).
- **Paolo** works at the pass office.

## How it works
0. **Home page** (`#home`): practical information in plain Italian.
   - What the pass allows, who can apply, what you need, timing and validity.
   - The office (via Sile 8), hours, contacts, and how to get there.
   - The extension and duplicate routes, and the difference from the European Disability Card.
   - Our privacy promises and the official sources.

   **Simulated login** (`#accesso`): the real service uses SPID, CIE or eIDAS. The demo has *no credential fields*: you pick one of three invented personas (Lucia, Giorgio, Samira). "Esci" (log out) deletes everything.
1. **The counter (chat).**
   - A clerk asks at most 3 questions, with big buttons, an optional 🎤 voice answer and 🔊 read-aloud.
   - Extension and duplicate requests are routed to a phone booking, because the online form does not handle them.
2. **The table and the envelope.**
   - Every required document is an empty sheet in the envelope.
   - When a document is photographed, Claude reads it (only the medical one) and a stamp comes down: **VA BENE**, **MANCANO PAGINE**, **MANCA LA FRASE**, **DA VERIFICARE**.
   - The clerk explains in plain Italian what to do next, prepares the **delegation form** ready to sign, and the **letter for the GP** with the exact wording.
3. **"Accompagnami nel modulo".** A replica of each real Comune screen, with the field to tap highlighted and the value to choose, based on the person's answers.
4. **"Prova generale" (dress rehearsal).** Before pressing *Inoltra*, the person shows a screenshot of the Riepilogo. Claude compares it with their situation and stamps the problems.
5. **Offices near home** (in the chat and on the home page): the person types their address. It is matched locally against **65,218 street numbers** (`ds634`), which confirms the address for registered-mail delivery and gives the municipio. The app then shows the pass office (via Sile 8, with distance and the booking link), the 2 nearest **registry offices** (`ds549`, for the ID card) and the **municipio** office (`ds1299`), each with a booking link.
6. **Office sheet** for Paolo: checks done, rules and official sources, no personal data, plus a JSON export.

## Where does Claude work when someone uses this?
| | |
|---|---|
| **Model** | `claude-opus-5-5`, adaptive thinking, effort `high`, structured JSON output, server-side refusal fallback |
| **Call 1: check the medical document** (`/api/check-medical`) | Reads the verbale or certificate (PDF or photos merged into one PDF). Decides the document type, then for each applicable rule (R4/R5 for a first pass, R6/R5 for a permanent renewal) returns *found / missing / not sure*, where it looked, and what to do. Detects missing pages from "Pagina X di Y", the art. 381 / L. 382/70 references, the exemption from future reviews, and the exact R6 sentence. |
| **Call 2: dress rehearsal** (`/api/check-summary`) | Reads the screenshot of the form's summary and compares it with the situation described: role, delivery choice, plate and CUDE platform, missing attachments. |
| **Prompts** | `server.py`: `MEDICAL_SYSTEM` and `SUMMARY_SYSTEM`. Rules in `rules.py`, R1–R12, each with its official source. |
| **What Claude decides** | Only whether the documents look complete and consistent with the Comune's published rules. |
| **What a human confirms** | The person reviews everything, signs and submits on the official site themselves. **The pass office decides.** Claude never says "you are entitled", never submits, and says when it is not sure. |

## City sources used
- Online CUDE form: rules, the 10 screens, accepted formats, and the two public sample *verbali* used in the demo
- Service page "Pass per la sosta e la circolazione di persone con disabilità"; extension and duplicate pages
- Official delegation forms (`mod-delega-3`, `mod-delega_agg-09-2024`)
- *Tipologie di procedimento* (Direzione Mobilità): 30-day legal limit, 30-day average in 2025
- disabilita.governo.it: what is national (CUDE, plate platform) and what is municipal
- Open data (refresh with `python fetch_city_data.py`): `ds634` street numbers with coordinates, `ds549` registry offices, `ds1299` municipio offices

## How to run it
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install anthropic pypdf pillow
export ANTHROPIC_API_KEY=sk-ant-...
python server.py                  # http://localhost:8765
python server.py --mock           # offline demo without AI (labelled in the UI)
python make_demo_docs.py          # rebuilds the demo documents
```
Test cases (buttons "Esempio" in the app):

| Case | Expected result |
|---|---|
| A: Lucia, verbale with only page 5 of 7 (the Comune's public sample) | MANCANO PAGINE, plus the art. 381 reference found |
| B: Giorgio, generic GP certificate | MANCA LA FRASE, plus the letter for the doctor |
| B2: GP certificate with the exact sentence | VA BENE |
| C: complete fictitious verbale, 3 pages, exempt from reviews | VA BENE |
| D: Lucia's summary screenshot | 3 problems: ID back missing, CUDE choice missing, in-person pickup |

## Privacy
See [PRIVACY.md](PRIVACY.md). In short:
- the ID cards, photo, delegation and plate never leave the browser;
- only the medical document and the summary are sent to Claude;
- nothing is stored, and the server logs no content;
- "Cancella tutto" (delete everything) is always visible.
