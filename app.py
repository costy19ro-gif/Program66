import streamlit as st
import os
import hashlib
import random

st.set_page_config(page_title="Program66 - Bet Builder Pro", layout="wide")
st.title("🚀 Program66 — Accumulator & Bet Builder (Stil Scores24)")
st.caption("Meciuri Aleatorii per Campionat | Meciuri Unice per Bilet | Cotă Minimă 1.27 | Mize Custom & Copiere")

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

# 🎛️ SELECTOR INTERACTIV DE PIEȚE (Actualizat cu piețele noi de goluri)
st.markdown("### 🎚️ Configurează piața biletului în timp real:")
tip_pariu = st.radio(
    "Alege opțiunea pe care vrei să se bazeze automat acumulatorii:",
    [
        "Toate Mixate (Combo)", 
        "Doar Soliști (1X2)", 
        "Doar Șansă Dublă (1X/X2)", 
        "Doar Goluri (Sub/Peste)", 
        "Opțiuni PsF (Pauză sau Final)",
        "Gazdele Marchează",
        "Oaspeții Marchează",
        "Ambele Marchează (GG)"
    ],
    horizontal=True
)

# 🎲 Amestecare aleatorie a listei de ID-uri (Folosim seed pentru a nu se schimba la fiecare click pe mize)
random.seed(42)
lista_ids_aleatorii = list(lista_ids)
random.shuffle(lista_ids_aleatorii)

toate_meciurile_procesate = []
campionate_folosite = set()  # Structură pentru a asigura un singur meci per campionat/ligă

for m_id in lista_ids_aleatorii:
    if m_id not in baza_meciuri:
        continue
        
    gazde, oaspeti, liga, data_ora = baza_meciuri[m_id]
    
    # 🛑 SARI dacă liga este în lista celor interzise
    if any(liga_blocata in liga for liga_blocata in ligi_interzise):
        continue
        
    # 🛑 SARI dacă am luat deja un meci din acest campionat
    if liga in campionate_folosite:
        continue
        
    ora_meci = data_ora.split(" ") if " " in data_ora else "19:00"
    
    hash_cote = int(hashlib.md5(m_id.encode('utf-8')).hexdigest(), 16)
    cota_1 = round(1.35 + ((hash_cote % 50) / 30), 2)
    cota_2 = round(1.60 + (((hash_cote >> 2) % 50) / 25), 2)
    cota_x = round(3.20 + ((hash_cote % 10) / 4), 2)
    
    home_played = 5 + (hash_cote % 15)
    away_played = 5 + ((hash_cote >> 3) % 15)
    este_meci_inchis = (hash_cote % 3) == 0
    
    nume_meci = f"{gazde} vs {oaspeti}"
    detalii = f"{ora_meci} | {liga} (ID: {m_id})"
    
    if cota_1 < cota_2:
        favorit, cota_fav, sd, cota_sd_val, psf = "1", cota_1, "1X", max(1.16, round(cota_1 * 0.76, 2)), "PsF 1"
    else:
        favorit, cota_fav, sd, cota_sd_val, psf = "2", cota_2, "X2", max(1.18, round(cota_2 * 0.76, 2)), "PsF 2"
        
    # 📊 Alocarea tipului de pariu și a cotelor
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
    elif tip_pariu == "Gazdele Marchează":
        pariu_ales = "Gazdele Marchează (O1+)"
        cota_aleasa = round(1.25 + ((hash_cote % 20) / 100), 2)
    elif tip_pariu == "Oaspeții Marchează":
        pariu_ales = "Oaspeții Marchează (O2+)"
        cota_aleasa = round(1.30 + (((hash_cote >> 1) % 20) / 100), 2)
    elif tip_pariu == "Ambele Marchează (GG)":
        pariu_ales = "Ambele Marchează (GG)"
        cota_aleasa = round(1.65 + ((hash_cote % 35) / 100), 2)
    else:
        # Combo / Mixat default
        pariu_ales = "Ambele Marchează (GG)" if (hash_cote % 4 == 0) else ("Sub 3.5" if este_meci_inchis else f"{sd} & +0.5 R1")
        if pariu_ales == "Ambele Marchează (GG)":
            cota_aleasa = round(1.70 + ((hash_cote % 25) / 100), 2)
        else:
            cota_aleasa = 1.28 if este_meci_inchis else round(cota_sd_val * 1.15, 2)

    if cota_aleasa < 1.27:
        continue

    # Adăugăm în listă și blocăm campionatul curent
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

# Sortează meciurile filtrate cronologic înainte de generarea biletelor
toate_meciurile_procesate = sorted(toate_meciurile_procesate, key=lambda x: x["ora"])

bilete_safe = []
bilete_mega = []
bilete_risky = []
meciuri_folosite = set()

# 🟢 1. Safe Accumulator (Până la 8 meciuri unice)
for m in toate_meciurile_procesate:
    if m["h_played"] >= 10 and m["a_played"] >= 10:  
        if m["meci"] not in meciuri_folosite and len(bilete_safe) < 8:
            bilete_safe.append(m)
            meciuri_folosite.add(m["meci"])

# 🟡 2. Mega Accumulator (Meciuri unice rămase)
for m in toate_meciurile_procesate:
    if m["meci"] not in meciuri_folosite and len(bilete_mega) < 4:
        if m["h_played"] >= 7 and m["a_played"] >= 7:
            bilete_mega.append(m)
            meciuri_folosite.add(m["meci"])

# 🔴 3. Risky Accumulator (Restul de meciuri unice rămase)
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
