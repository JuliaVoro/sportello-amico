"""Build the demo documents. Every person and number here is invented; the two verbali come from the
public examples the Comune links in its own form. Nothing in demo_docs/ is real personal data.

  python make_demo_docs.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter

OUT = Path(__file__).parent / "demo_docs"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
W, H = 1240, 1754  # A4 at 150 dpi


def font(size, bold=False):
    try:
        return ImageFont.truetype(BOLD if bold else FONT, size)
    except OSError:
        return ImageFont.load_default(size)


def page(lines, footer=None, stamp="FAC-SIMILE · DATI FITTIZI"):
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    y = 120
    for text, size, bold in lines:
        if text == "---":
            d.line((100, y + 10, W - 100, y + 10), fill="black", width=2)
            y += 40
            continue
        d.text((100, y), text, font=font(size, bold), fill="black")
        y += int(size * 1.6)
    if footer:
        d.text((W - 330, H - 120), footer, font=font(24), fill="black")
    d.text((100, H - 70), stamp, font=font(22, True), fill=(200, 0, 0))
    return img


def save_pdf(pages, name):
    pages[0].save(OUT / name, save_all=True, append_images=pages[1:], resolution=150)


def main():
    OUT.mkdir(exist_ok=True)

    # A — Lucia: only page 5 of 7 of the Comune's public example (art. 381)
    src = OUT / "C_verbale_esempio_art381.pdf"
    w = PdfWriter()
    w.add_page(PdfReader(src).pages[0])
    with open(OUT / "A_lucia_verbale_solo_pagina5.pdf", "wb") as f:
        w.write(f)

    # B — Giorgio: generic certificate from the family doctor (missing the R6 sentence)
    cert = [("Dott. Paolo Neri — Medico di Medicina Generale", 30, True),
            ("Via Esempio 1, 20100 Milano (indirizzo fittizio)", 24, False), ("---", 0, False),
            ("CERTIFICATO MEDICO", 40, True), ("", 24, False),
            ("Si certifica che il Sig. Giorgio Bianchi, nato il 01/01/1955,", 28, False),
            ("è seguito da questo studio per patologia cronica che limita", 28, False),
            ("la deambulazione e necessita di controlli periodici.", 28, False), ("", 24, False),
            ("Si rilascia su richiesta dell'interessato per gli usi consentiti.", 28, False), ("", 24, False),
            ("Milano, 15/09/2026", 28, False), ("Firma e timbro: ____________________", 28, False)]
    page(cert).save(OUT / "B_giorgio_certificato_generico.png")

    # B2 — Giorgio after asking the doctor: same certificate with the exact sentence
    cert_ok = cert[:5] + [
        ("Si certifica che il Sig. Giorgio Bianchi, nato il 01/01/1955,", 28, False),
        ("titolare di pass disabili rilasciato dal Comune di Milano,", 28, False),
        ("alla data odierna persistono le condizioni sanitarie che hanno", 28, True),
        ("portato al rilascio del pass disabili.", 28, True), ("", 24, False),
        ("Milano, 02/10/2026", 28, False), ("Firma e timbro: ____________________", 28, False)]
    page(cert_ok).save(OUT / "B2_giorgio_certificato_corretto.png")

    # C — complete fictitious verbale, 3 pages, art. 381, exempt from future reviews
    head = [("Centro Medico Legale di MILANO, MI", 26, False), ("", 20, False),
            ("VERBALE DI ACCERTAMENTO DELL'INVALIDITA' CIVILE,", 30, True),
            ("DELLE CONDIZIONI VISIVE E DELLA SORDITA'", 30, True),
            ("(ai sensi dell'art. 20 della Legge 3 agosto 2009 n. 102)", 24, False), ("---", 0, False)]
    p1 = head + [("Data accertamento: 10/03/2025      Tipo domanda: Invalidita' Civile", 24, False),
                 ("Nome: MARIO ROSSI (fittizio)      C.F.: FAC-SIMILE", 24, False),
                 ("Residenza: MILANO", 24, False), ("---", 0, False),
                 ("Documentazione acquisita: OMISSIS", 24, False),
                 ("Altra documentazione sanitaria: OMISSIS", 24, False)]
    p2 = head + [("Diagnosi CML: OMISSIS", 24, False), ("Codice DM 5/2/92: OMISSIS     Codice ICD9: OMISSIS", 24, False),
                 ("---", 0, False), ("Valutazione proposta dal CML: OMISSIS", 24, False), ("---", 0, False),
                 ("Ricorrono le previsioni di cui:", 26, True), ("- all'art. 381 del DPR 495/1992", 26, False),
                 ("---", 0, False), ("Disabilita' rilevate: OMISSIS", 24, False), ("---", 0, False),
                 ("ESONERO DA FUTURE VISITE DI REVISIONE PER APPLICAZIONE", 24, True),
                 ("DEL DM 2/8/2007:   SI", 24, True), ("REVISIONE: NO", 24, False)]
    p3 = head + [("Responsabile CML o suo delegato: OMISSIS", 24, False), ("", 20, False),
                 ("Firme autografe sostituite a mezzo stampa ai sensi", 24, False),
                 ("dell'art.3 comma 2 del D.lgs. n.39 del 1993", 24, False)]
    save_pdf([page(p1, "Pagina 1 di 3"), page(p2, "Pagina 2 di 3"), page(p3, "Pagina 3 di 3")],
             "C_verbale_completo_fittizio.pdf")

    # D — summary screen of the official form, filled in for Lucia's case (fictitious), "ritiro di persona"
    riep = [("8. Riepilogo  (simulazione del modulo Comune di Milano)", 32, True), ("---", 0, False),
            ("2. Dati richiedente", 26, True), ("Richiedo il pass disabili in qualità di: delegato", 24, False),
            ("3. Dati intestatario del pass disabili", 26, True),
            ("Nome: ANNA   Cognome: VERDI   Codice Fiscale: FAC-SIMILE", 24, False),
            ("Telefono: 000 0000000   Email: lucia.esempio@example.com", 24, False),
            ("Documento di identità FRONTE: carta_identita_fronte.jpg", 24, False),
            ("Documento di identità RETRO: [allegato non presente]", 24, False),
            ("Fotografia 35x45: fototessera.jpg", 24, False),
            ("4. Richiesta Pass", 26, True), ("Il/La sottoscritto/a chiede: il rilascio di un nuovo pass disabili", 24, False),
            ("5. Dichiarazioni integrative", 26, True), ("DICHIARA di conoscere e acconsentire: sì", 24, False),
            ("6. Modalità di ritiro del pass", 26, True),
            ("ritiro di persona presso gli Uffici preposti (solo su appuntamento)", 24, False),
            ("7. Targa", 26, True), ("voler richiedere l'autorizzazione per il libero transito: sì", 24, False),
            ("TARGA: AB123CD", 24, False),
            ("Piattaforma nazionale CUDE: [nessuna scelta]", 24, False)]
    page(riep).save(OUT / "D_lucia_riepilogo_modulo.png")

    print("\n".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
