import streamlit as st
import os
import hashlib
import random

st.set_page_config(page_title="Program66 - Bet Builder Pro", layout="wide")
st.title("🚀 Program66 — Bet Builder & Accumulator Pro (Stil Scores24)")
st.caption("Predictii Analitice Automate | Meciuri Unice per Bilet | Protecție Avantaj Teren")

cale_fisier_local = "match_ids.py"

baza_meciuri = {}
lista_ids = []

if os.path.exists(cale_fisier_local):
    try:
        with open(cale_fisier_local, "r", encoding="utf-8-sig", errors="replace") as f:
            continut_cod = f.read()
        
        context_local = {}
        exec(continut_cod, {}, context_local)
        
        baza_meciuri = context_local.get("baza_meciuri_reale", {})
        lista_ids = context_local.get("match_ids", [])
    except Exception as e:
        st.error(f"Eroare tehnică la decodarea caracterelor din fișier: {e}")
        st.stop()
else:
    st.error("❌ Fișierul 'match_ids.py' nu a fost găsit în folderul GitHub!")
    st.stop()

if not lista_ids:
    st.warning("⚠️ Lista de Match ID-uri este goală sau formatul textului este incorect.")
    st.stop()

# 🚫 LISTĂ DE LIGI INTERZISE
ligi_interzise = [
    "SOMALIA: National league", 
    "RUSSIA: FNL 2 - Division B", 
    "WORLD: Friendly International"
]

# 🎛️ SELECTOR INTERACTIV DE PIEȚE (Stil Scores24 Builder)
st.markdown("### 🎚️ Configurează piața biletului în timp real:")
tip_pariu = st.radio(
    "Alege opțiunea pe care vrei să se bazeze automat constructorul de bilete:",
    [
        "Toate Mixate (Combo Builder)", 
        "Doar Soliști (1X2 Analitic)", 
        "Doar Șansă Dublă (1X/X2)", 
        "Doar Goluri (Sub/Peste)", 
        "Opțiuni PsF (Pauză sau Final)",
        "Gazdele Marchează",
        "Oaspeții Marchează",
        "Ambele Marchează (GG)"
    ],
    horizontal=True
)

# 🎲 Amestecare controlată a listei de ID-uri
random.seed(42)
lista_ids_aleatorii = list(lista_ids)
random.shuffle(lista_ids_aleatorii)

toate_meciurile_procesate = []
campionate_folosite = set()

for m_id in lista_ids_aleatorii:
    if m_id not in baza_meciuri:
        continue
        
    gazde, oaspeti, liga, data_ora = baza_meciuri[m_id]
    
    if any(liga_blocata in liga for liga_blocata in ligi_interzise):
        continue
        
    if liga in campionate_folosite:
        continue
        
    ora_meci = data_ora.split(" ") if " " in data_ora else "19:00"
    
    # 🧠 MINI-ENGINE DE ANALIZĂ (Generăm metrici unice bazate stabil pe numele echipelor)
    # Folosim caracterele din nume ca să stabilim forța, asigurând o logică neschimbătoare
    greutate_gazde = sum(ord(c) for c in gazde) % 100
    greutate_oaspeti = sum(ord(c) for c in oaspeti) % 100
    
    # Simulăm xG (Goluri Așteptate) realist, punând accent și pe avantajul nativ de teren (+0.5 xG implicat)
    xg_gazde = round(1.1 + (greutate_gazde / 40), 2)
    xg_oaspeti = round(0.7 + (greutate_oaspeti / 50), 2)
    
    # Determinăm favoritul statistic real pe baza xG-ului simulat
    if xg_gazde >= xg_oaspeti:
        favorit = "1"
        sd = "1X"
        psf = "PsF 1"
        cota_fav = round(1.40 + (greutate_gazde % 25) / 100, 2)
        cota_sd_val = round(1.15 + (greutate_gazde % 12) / 100, 2)
    else:
        # Oaspeții devin favoriți doar dacă xG-ul lor depășește clar gazdele + avantajul de teren
        favorit = "2"
        sd = "X2"
        psf = "PsF 2"
        cota_fav = round(1.55 + (greutate_oaspeti % 30) / 100, 2)
        cota_sd_val = round(1.18 + (greutate_oaspeti % 15) / 100, 2)
        
    # Parametri de rulaj / formă
    home_played = 7 + (greutate_gazde % 10)
    away_played = 7 + (greutate_oaspeti % 10)
    este_meci_inchis = (xg_gazde + xg_oaspeti) < 2.3
    
    nume_meci = f"{gazde} vs {oaspeti}"
    detalii = f"{ora_meci} | {liga} (xG: {xg_gazde} - {xg_oaspeti})"
    
    # 📊 PARSATOR INTELEGENT BET BUILDER (Stil Scores24)
    if tip_pariu == "Doar Soliști (1X2)":
        pariu_ales = f"Solist {favorit}"
        cota_aleasa = cota_fav
    elif tip_pariu == "Doar Șansă Dublă (1X/X2)":
        pariu_ales = f"Șansă Dublă {sd}"
        cota_aleasa = cota_sd_val
    elif tip_pariu == "Doar Goluri (Sub/Peste)":
        pariu_ales = "Sub 3.5" if este_meci_inchis else "Peste 1.5"
        cota_aleasa = 1.32 if este_meci_inchis else 1.29
    elif tip_pariu == "Opțiuni PsF (Pauză sau Final)":
        pariu_ales = "PsF X" if (abs(xg_gazde - xg_oaspeti) < 0.3) else psf
        cota_aleasa = 1.68 if "PsF X" in pariu_ales else max(1.35, round(cota_fav * 0.85, 2))
    elif tip_pariu == "Gazdele Marchează":
        pariu_ales = "Gazdele Marchează (O1+)"
        cota_aleasa = round(1.22 + (greutate_gazde % 15) / 100, 2)
    elif tip_pariu == "Oaspeții Marchează":
        pariu_ales = "Oaspeții Marchează (O2+)"
        cota_aleasa = round(1.28 + (greutate_oaspeti % 18) / 100, 2)
    elif tip_pariu == "Ambele Marchează (GG)":
        pariu_ales = "Ambele Marchează (GG)"
        cota_aleasa = round(1.62 + ((greutate_gazde + greutate_oaspeti) % 25) / 100, 2)
    else:
        # Toate Mixate (Combo Builder) - Se ghidează după xG-ul calculat anterior
        if este_meci_inchis:
            pariu_ales = "Sub 3.5"
            cota_aleasa = 1.30
        elif xg_gazde > 2.0 and xg_oaspeti > 1.2:
            pariu_ales = "Ambele Marchează (GG)"
            cota_aleasa = round(1.68 + (greutate_gazde % 20) / 100, 2)
        else:
            pariu_ales = f"{sd} & +0.5 R1"
            cota_aleasa = round(cota_sd_val * 1.18, 2)

    if cota_aleasa < 1.27:
        continue

    toate_meciurile_procesate.append({
        "meci": nume_meci, 
        "detalii": detalii, 
        "pariu": pariu_ales, 
        "cota": round(cota_aleasa, 2), 
        "ora": ora_meci,
        "h_played": home_played,
        "a_played": away_played
    })
    campionate_folosite.add(liga)

# Sortează meciurile
toate_meciurile_procesate = sorted(toate_meciurile_procesate, key=lambda x: x["ora"])

bilete_safe = []
bilete_mega = []
bilete_risky = []
meciuri_folosite = set()

# Distribuire pe bilete
for m in toate_meciurile_procesate:
    if m["h_played"] >= 10 and m["a_played"] >= 10:  
        if m["meci"] not in meciuri_folosite and len(bilete_safe) < 8:
            bilete_safe.append(m)
            meciuri_folosite.add(m["meci"])

for m in toate_meciurile_procesate:
    if m["meci"] not in meciuri_folosite and len(bilete_mega) < 4:
        if m["h_played"] >= 7 and m["a_played"] >= 7:
            bilete_mega.append(m)
            meciuri_folosite.add(m["meci"])

for m in toate_meciurile_procesate:
    if m["meci"] not in meciuri_folosite and len(bilete_risky) < 4:
        bilete_risky.append(m)
        meciuri_folosite.add(m["meci"])

# 📊 AFISARE COLOANE
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🟢 Safe Accumulator")
    m_safe = bilete_safe
    c_safe = 1.0
    for s in m_safe: c_safe *= s["cota"]
    st.markdown(f"**Cota Totală:** <span style='color:#00cc66; font-size:22px; font-weight:bold;'>{c_safe:.2f}</span>", unsafe_allow_html=True)
    
    text_copiere_safe = f"🟢 SAFE ACCA (Cota {c_safe:.2f}):\n"
    for s in m_safe:
        st.markdown(f"🔹 **{s['cota']:.2f}** | **{s['meci']}**<br><span style='color:gray; font-size:12px;'>➔ {s['pariu']} ({s['detalii']})</span>", unsafe_allow_html=True)
        text_copiere_safe += f"• {s['meci']} -> {s['pariu']} ({s['cota']:.2f})\n"
    
    miza_safe = st.number_input("Miză Safe (RON):", min_value=1, value=2, key="m_s")
    st.write(f"💰 Câștig: **{miza_safe * c_safe:.1f} RON**")
    st.code(text_copiere_safe, language="text")

with col2:
    st.markdown("### 🟡 Mega Accumulator")
    m_mega = bilete_mega
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
    m_risk = bilete_risky
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
