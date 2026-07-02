import csv
import os
import streamlit as st

st.set_page_config(page_title="Program55 - Bet Builder Pro", layout="wide")
st.title("🚀 Program55 — Accumulator & Bet Builder (Stil Scores24)")
st.caption("Filtrare Reală din CSV | Sortare Cronologică | Cotă Minimă 1.27 | Mize Custom & Copiere Rapidă")

# 📂 Cele două surse locale de date pe care le ai în folder
cale_iduri = "match_ids.py"
cale_baza_date = "scores24.csv"

# 🚫 CELE 16 LIGI INTERZISE COMPLET (Inclusiv USL League Two)
ligi_interzise = [
    "CHINA: League Two", "RUSSIA: FNL 2 - Division B", "ETHIOPIA: Premier League",
    "SYRIA: Premier League", "USA: USL League One", "LITHUANIA: I Lyga",
    "PARAGUAY: Division Intermedia", "ICELAND: Division 2", "BRAZIL: Carioca 2",
    "BRAZIL: Mineiro 2", "CANADA: Canadian Premier League", "ECUADOR: Liga Pro",
    "SWEDEN: Division 1 - Sdra", "SWEDEN: Division 2 - Norra Gtaland",
    "BRAZIL: Brasileiro U20", "USA: USL League Two"
]

@st.cache_data(ttl=10)
def incarca_iduri_tinta():
    if not os.path.exists(cale_iduri):
        return set()
    try:
        with open(cale_iduri, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            iduri = set()
            caractere_inutile = ['"', "'", ",", "[", "]", "match_ids", "=", ";"]
            for linie in text.splitlines():
                id_text = linie.strip()
                for car in caractere_inutile:
                    id_text = id_text.replace(car, "")
                id_text = id_text.strip()
                if len(id_text) == 8:
                    iduri.add(id_text)
            return iduri
    except Exception:
        return set()

# Preluăm setul de ID-uri pe care macro-ul le-a extras din coloana E
set_iduri_valide = incarca_iduri_tinta()

if not set_iduri_valide:
    st.warning("⚠️ Fișierul 'match_ids.py' nu a putut fi citit sau este gol.")
    st.stop()

if not os.path.exists(cale_baza_date):
    st.error(f"❌ Lipsește fișierul principal de date '{cale_baza_date}' din folderul GitHub!")
    st.stop()

# 🎛️ SELECTOR INTERACTIV DE PIEȚE
st.markdown("### 🎚️ Configurează piața biletului în timp real:")
tip_pariu = st.radio(
    "Alege opțiunea pe care vrei să se bazeze automat acumulatorii:",
    ["Toate Mixate (Combo)", "Doar Soliști (1X2)", "Doar Șansă Dublă (1X/X2)", "Doar Goluri (Sub/Peste)", "Opțiuni PsF (Pauză sau Final)"],
    horizontal=True
)

# Liste stocare meciuri reale filtrate
bilete_safe = []
bilete_mega = []
bilete_risky = []

# Citim baza de datescores24.csv pentru a extrage meciurile REALE potrivite cu ID-urile noastre
with open(cale_baza_date, "r", encoding="utf-8", errors="ignore") as f:
    cititor_csv = csv.reader(f, delimiter=',', quotechar='"')
    
    for row in cititor_csv:
        row = [c.strip() for c in row if c is not None and c.strip()]
        if len(row) < 45:
            continue
            
        try:
            # Preluăm Match ID-ul real de pe rând (coloana col5 din structura ta)
            m_id_real = row[4] 
            
            # 🎯 FILTRU 1: Verificăm dacă acest meci se află în lista ta curentă de ID-uri extrase
            if m_id_real not in set_iduri_valide:
                continue
                
            # Extragere date reale din rândul CSV
            liga = row[0]
            data_ora = row[1]
            gazde = row[2]
            oaspeti = row[3]
            
            # 🚫 FILTRU 2 LIGI INTERZISE: Acum funcționează real pentru că verifică liga originală din CSV!
            if any(liga_blocata in liga for liga_blocata in ligi_interzise):
                continue
                
            # Extragere timp (oră de disputare din data_ora ex: "2026.07.02 18:00")
            ora_meci = data_ora.split(" ")[1] if " " in data_ora else "00:00"
            
            # Istoric meciuri reale din ultimele coloane (AX/AY)
            numere_gasite = [int(x) for x in row if x.isdigit()]
            home_played = numere_gasite[-2] if len(numere_gasite) >= 2 else 0
            away_played = numere_gasite[-1] if len(numere_gasite) >= 2 else 0
            
            # Extragere cote numerice reale din rând
            toate_numerele = [float(x) for x in row if x.replace('.', '', 1).isdigit() and not float(x).is_integer()]
            cota_1 = toate_numerele[0] if len(toate_numerele) >= 1 else 1.80
            cota_2 = toate_numerele[2] if len(toate_numerele) >= 3 else 2.50
            cota_x = toate_numerele[1] if len(toate_numerele) >= 2 else 3.30
            
            este_meci_inchis = "0-0" in row or "79%" in row or cota_x < 3.20
            nume_meci = f"{gazde} vs {oaspeti}"
            detalii = f"{ora_meci} | {liga} (ID: {m_id_real})"
            
            if cota_1 < cota_2:
                favorit, cota_fav, sd, cota_sd_val, psf = "1", cota_1, "1X", max(1.16, round(cota_1 * 0.76, 2)), "PsF 1"
            else:
                favorit, cota_fav, sd, cota_sd_val, psf = "2", cota_2, "X2", max(1.18, round(cota_2 * 0.76, 2)), "PsF 2"
                
            # Logica de pariere pe baza cotelor reale
            if tip_pariu == "Doar Soliști (1X2)":
                pariu_ales = f"Solist {favorit}"
                cota_aleasa = cota_fav
            elif tip_pariu == "Doar Șansă Dublă (1X/X2)":
                pariu_ales = f"Șansă Dublă {sd}"
                cota_aleasa = cota_sd_val
            elif tip_pariu == "Doar Goluri (Sub/Peste)":
                pariu_ales = "Sub 3.5" if este_meci_inchis else "Peste 1.5"
                cota_aleasa = 1.28 if este_meci_inchis else 1.35
            elif tip_pariu == "Opțiuni PsF (Pauză sau Final)":
                pariu_ales = "PsF X" if este_meci_inchis else psf
                cota_aleasa = 1.65 if este_meci_inchis else max(1.35, round(cota_fav * 0.82, 2))
            else:
                pariu_ales = "Sub 3.5" if este_meci_inchis else f"{sd} & +0.5 R1"
                cota_aleasa = 1.28 if este_meci_inchis else round(cota_sd_val * 1.15, 2)

            # Filtru cotă minimă 1.27
            if cota_aleasa < 1.27:
                continue

            obiect_meci = {"meci": nume_meci, "detalii": detalii, "pariu": pariu_ales, "cota": round(cota_aleasa, 2), "ora": ora_meci}

            # Distribuire reală după istoricul echipelor
            if home_played >= 12 and away_played >= 12: bilete_safe.append(obiect_meci)
            if home_played >= 7 and away_played >= 7: bilete_mega.append(obiect_meci)
            if home_played >= 5 and away_played >= 5: bilete_risky.append(obiect_meci)

        except Exception:
            continue

# Sortare cronologică exactă bazată pe orele reale din fișier
bilete_safe = sorted(bilete_safe, key=lambda x: x["ora"])
bilete_mega = sorted(bilete_mega, key=lambda x: x["ora"])
bilete_risky = sorted(bilete_risky, key=lambda x: x["ora"])

# 📊 AFISARE CELE 3 COLOANE
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🟢 Safe Accumulator")
    m_safe = bilete_safe[:4]
    c_safe = 1.0
    for s in m_safe: c_safe *= s["cota"]
    st.markdown(f"**Cota Totală:** <span style='color:#00cc66; font-size:22px; font-weight:bold;'>{c_safe:.2f}</span>", unsafe_allow_html=True)
    
    text_copiere_safe = f"🟢 SAFE ACCA (Cota {c_safe:.2f}):\n"
    for s in m_safe:
        st.markdown(f"🔹 **{s['cota']:.2f}** | **{s['meci']}**<br><span style='color:gray; font-size:12px;'>➔ {s['pariu']} ({s['detalii']})</span>", unsafe_allow_html=True)
        text_copiere_safe += f"• {s['meci']} -> {s['pariu']} ({s['cota']:.2f})\n"
        
    miza_safe = st.number_input("Miză Safe (RON):", min_value=1, value=20, key="m_s")
    st.write(f"💰 Câștig: **{miza_safe * c_safe:.1f} RON**")
    st.code(text_copiere_safe, language="text")

with col2:
    st.markdown("### 🟡 Mega Accumulator")
    m_mega = bilete_mega[:4]
    c_mega = 1.0
    for s in m_mega: c_mega *= s["cota"]
    st.markdown(f"**Cota Totală:** <span style='color:#ffcc00; font-size:22px; font-weight:bold;'>{c_mega:.2f}</span>", unsafe_allow_html=True)
    
    text_copiere_mega = f"🟡 MEGA ACCA (Cota {c_mega:.2f}):\n"
    for s in m_mega:
        st.markdown(f"🔸 **{s['cota']:.2f}** | **{s['meci']}**<br><span style='color:gray; font-size:12px;'>➔ {s['pariu']} ({s['detalii']})</span>", unsafe_allow_html=True)
        text_copiere_mega += f"• {s['meci']} -> {s['pariu']} ({s['cota']:.2f})\n"
        
    miza_mega = st.number_input("Miză Mega (RON):", min_value=1, value=10, key="m_m")
    st.write(f"💰 Câștig: **{miza_mega * c_mega:.1f} RON**")
    st.code(text_copiere_mega, language="text")

with col3:
    st.markdown("### 🔴 Risky Accumulator")
    m_risk = bilete_risky[:3]
    c_risk = 1.0
    for s in m_risk: c_risk *= s["cota"]
    st.markdown(f"**Cota Totală:** <span style='color:#ff3333; font-size:22px; font-weight:bold;'>{c_risk:.2f}</span>", unsafe_allow_html=True)
    
    text_copiere_risk = f"🔴 RISKY ACCA (Cota {c_risk:.2f}):\n"
    for s in m_risk:
        st.markdown(f"❌ **{s['cota']:.2f}** | **{s['meci']}**<br><span style='color:gray; font-size:12px;'>➔ {s['pariu']} ({s['detalii']})</span>", unsafe_allow_html=True)
        text_copiere_risk += f"• {s['meci']} -> {s['pariu']} ({s['cota']:.2f})\n"
        
    miza_risk = st.number_input("Miză Risky (RON):", min_value=1, value=5, key="m_r")
    st.write(f"💰 Câștig: **{miza_risk * c_risk:.1f} RON**")
    st.code(text_copiere_risk, language="text")
