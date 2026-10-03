"""Rules the assistant applies, taken from the Comune di Milano online form (CUDE) and service pages.

Each rule has an id, the text Claude checks against, and the official source shown to the user
and to the office. Keep this file as the single source of truth: the server prompt and the
office summary sheet are both built from it.
"""

FORM = "https://formshd.comune.milano.it/rwe2/module_preview.jsp?MODULE_TAG=PASS_DISABILI"
PAGE = "https://www.comune.milano.it/servizi/mobilita/pass-per-la-sosta-e-la-circolazione-di-persone-con-disabilita"

RULES = {
    "R1": ("Possono fare domanda: la persona con disabilità, il genitore di un figlio minorenne, un delegato, "
           "il legale rappresentante (tutore, protutore, procuratore, amministratore di sostegno) con i poteri necessari.", FORM),
    "R2": ("Allegati sempre richiesti: documento d'identità fronte/retro del titolare, fototessera recente a colori "
           "35x45 mm, documentazione sanitaria.", FORM),
    "R3": ("Se si fa domanda per un'altra persona: documento fronte/retro del richiedente e delega firmata dal "
           "delegante, oppure atto di nomina a legale rappresentante.", FORM),
    "R4": ("Primo rilascio: certificato di deambulazione sensibilmente ridotta in corso di validità rilasciato "
           "dall'ufficio medico legale dell'azienda sanitaria, oppure verbale d'invalidità o handicap con "
           "riconoscimento dello status di non vedente (L. 382/70) o con l'indicazione di capacità di deambulazione "
           "sensibilmente ridotta (art. 381 DPR 495/1992). Sono valutate anche le sentenze omologate.", FORM),
    "R5": ("Il verbale va allegato come un unico PDF con tutte le pagine della versione OMISSIS, conforme "
           "all'originale, in corso di validità, senza revoche, modifiche, alterazioni o sostituzioni.", FORM),
    "R6": ("Rinnovo di un pass ottenuto per invalidità permanente: certificato del medico curante che attesti "
           "\"alla data odierna persistono le condizioni sanitarie che hanno portato al rilascio del pass disabili\", "
           "oppure verbale con art. 381 DPR 495/92 o L. 382/70 con attestazione di non revisione o esonero da "
           "future revisioni (DM 02/08/2007).", FORM),
    "R7": ("Il pass dura quanto il diritto su cui si basa e comunque non oltre 5 anni, anche per invalidità "
           "permanenti.", FORM),
    "R8": ("La modalità di consegna (raccomandata a domicilio o ritiro su appuntamento) non si può modificare "
           "dopo la scelta.", FORM),
    "R9": ("Allegati in PDF, JPG o PNG, massimo 5 MB ciascuno. Fototessera solo JPG o PNG.", FORM),
    "R10": ("Il modulo online gestisce solo rilascio e rinnovo. Proroga (attesa visita INPS) e duplicato "
            "si chiedono prenotando una chiamata.", PAGE),
    "R11": ("Le comunicazioni sulla domanda arrivano al telefono e all'email indicati per il titolare.", FORM),
    "R12": ("La targa si può associare subito o in un secondo momento. Se si associa, va scelto se aderire o no "
            "alla Piattaforma nazionale CUDE (MIT).", FORM),
}

PHRASE_R6 = "alla data odierna persistono le condizioni sanitarie che hanno portato al rilascio del pass disabili"


def rules_for(request_type: str, permanent: bool | None) -> list[str]:
    """Which medical-document rules apply to this case."""
    if request_type == "rinnovo" and permanent:
        return ["R6", "R5"]
    return ["R4", "R5"]


def rules_text(ids: list[str]) -> str:
    return "\n".join(f"{i}: {RULES[i][0]}" for i in ids)
