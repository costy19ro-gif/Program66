import streamlit as st
import urllib.request
import hashlib

st.set_page_config(page_title="Program55 - Bet Builder", layout="wide")
st.title("🚀 Program55 — Accumulator & Bet Builder (Stil Scores24)")
st.caption("Preluare automată din GitHub | Sortare Cronologică | Cotă Minivă 1.27")

# 🔗 URL-ul fișierului tău text cu ID-uri în format RAW
URL_MATCH_IDS = "https://githubusercontent.com"

# 🚫 LISTA COMPLETĂ DE 16 LIGI INTERZISE DIN MOTIVE DE SIGURANȚĂ
ligi_interzise = [
    "CHINA: League Two", "RUSSIA: FNL 2 - Division B", "ETHIOPIA: Premier League",
    "SYRIA: Premier League", "USA: USL League One", "LITHUANIA: I Lyga",
    "PARAGUAY: Division Intermedia", "ICELAND: Division 2", "BRAZIL: Carioca 2",
    "BRAZIL: Mineiro 2", "CANADA: Canadian Premier League", "ECUADOR: Liga Pro",
    "SWEDEN: Division 1 - Sdra", "SWEDEN: Division 2 - Norra Gtaland",
    "BRAZIL: Brasileiro U20", "USA: USL League Two"
]

# 📥 Funcție securizată pentru descărcarea și curățarea ID-urilor brute din text (8 caractere)
@st.cache_data(ttl=300)
def descarca_lista_iduri():
    try:
        with urllib.request.urlopen(URL_MATCH_IDS) as raspuns:
            text_brut = raspuns.read().decode('utf-8')
            linii_curate = []
            caractere_inutile = ['"', "'", ",", "[", "]", "lista_match_ids", "=", ";"]
            
            for linie in text_brut.splitlines():
                id_text = linie.strip()
                for car in caractere_inutile:
                    id_text = id_text.replace(car, "")
                id_text = id_text.strip()
                
                if len(id_text) == 8:
                    linii_curate.append(id_text)
            return linii_curate
    except Exception as e:
        st.error(f"Eroare la procesarea listei de ID-uri din GitHub: {e}")
        return []

lista_match_ids = descarca_lista_iduri()

if not lista_match_ids:
    st.warning("⚠️ Lista de Match ID-uri este goală sau nu a putut fi citită.")
    st.stop()

# 🎛️ SELECTOR INTERACTIV DE PIEȚE
st.markdown("### 🎚️ Configurează piața biletului în timp real:")
tip_pariu = st.radio(
    "Alege opțiunea pe care vrei să se bazeze automat acumulatorii:",
    ["Toate Mixate (Combo)", "Doar Soliști (1X2)", "Doar Șansă Dublă (1X/X2)", "Doar Goluri (Sub/Peste)", "Opțiuni PsF (Pauză sau Final)"],
    horizontal=True
)

# Liste pentru structura pe cele 3 categorii de istoric
bilete_safe = []   # Min. 12 meciuri
bilete_mega = []   # Min. 7 meciuri
bilete_risky = []  # Min. 5 meciuri

# Echipe și ligi pentru generarea meciurilor
echipe_exemplu = [
    ("Inter Turku", "SJK", "FINLAND: Veikkausliiga"),
    ("Daejeon", "Bucheon FC 1995", "SOUTH KOREA: K League 1"),
    ("KuPS", "Ilves", "FINLAND: Veikkausliiga"),
    ("Lahti", "TPS", "FINLAND: Veikkausliiga"),
    ("Dinamo Tbilisi", "Dinamo Batumi", "GEORGIA: Erovnuli Liga"),
    ("Gold Coast Knights", "Eastern Suburbs", "AUSTRALIA: NPL Queensland"),
    ("Edgeworth E.", "Lambton J.", "AUSTRALIA: NPL Northern NSW"),
    ("Hafnarfjordur W", "Valur W", "ICELAND: Besta deild Women")
]

# Ore de disputare posibile (pentru simularea orelor reale din Excel)
ore_disputare = ["11:00", "12:30", "13:00", "13:30", "14:00", "15:30", "17:00", "18:00", "19:30", "20:00", "21:15", "22:00", "23:45"]

# Generăm și procesăm datele
for m_id in lista_match_ids:
    hash_id = int(hashlib.md5(m_id.encode('utf-8')).hexdigest(), 16)
    
    gazde, oaspeti, liga = echipe_exemplu[hash_id % len(echipe_exemplu)]
    
    if any(liga_blocata in liga for liga_blocata in ligi_interzise):
        continue
        
    home_played = 5 + (hash_id % 15)
    away_played = 5 + ((hash_id >> 2) % 15)
    
    # Atribuim o oră stabilă din listă pe baza hash-ului
    ora_meci = ore_disputare[hash_id % len(ore_disputare)]
    
    # Generare cote deterministe stabile
    cota_1 = round(1.30 + ((hash_id % 100) / 45), 2)
    cota_2 = round(1.50 + (((hash_id >> 3) % 100) / 35), 2)
    cota_x = round(3.20 + ((hash_id % 8) / 4), 2)
    
    este_meci_inchis = (hash_id % 3) == 0
    nume_meci = f"{gazde} vs {oaspeti}"
    detalii = f"{ora_meci} | {liga} (ID: {m_id})"
    
    if cota_1 < cota_2:
        favorit, cota_fav, sd, cota_sd_val, psf = "1", cota_1, "1X", max(1.16, round(cota_1 * 0.76, 2)), "PsF 1"
    else:
        favorit, cota_fav, sd, cota_sd_val, psf = "2", cota_2, "X2", max(1.18, round(cota_2 * 0.76, 2)), "PsF 2"
        
    # Logica de pariere
    if tip_pariu == "Doar Soliști (1X2)":
        pariu_ales = f"Victorie Favorit (Solist {favorit})"
        cota_aleasa = cota_fav
    elif tip_pariu == "Doar Șansă Dublă (1X/X2)":
        pariu_ales = f"Șansă Dublă {sd}"
        cota_aleasa = cota_sd_val
    elif tip_pariu == "Doar Goluri (Sub/Peste)":
        pariu_ales = "Sub 3.5 Goluri" if este_meci_inchis else "Peste 1.5 Goluri"
        cota_aleasa = 1.28 if este_meci_inchis else 1.35
    elif tip_pariu == "Opțiuni PsF (Pauză sau Final)":
        pariu_ales = "PsF X (Egal la Pauză/Final)" if este_meci_inchis else f"{psf} (Pauză sau Final)"
        cota_aleasa = 1.65 if este_meci_inchis else max(1.35, round(cota_fav * 0.82, 2))
    else:
        pariu_ales = "Sub 3.5 Goluri" if este_meci_inchis else f"{sd} & Peste 0.5 goluri R1"
        cota_aleasa = 1.28 if este_meci_inchis else round(cota_sd_val * 1.15, 2)

    # 🛑 FILTRU DUR: COTĂ MINIMĂ 1.27. Dacă selecția e sub prăg, o eliminăm din calcule!
    if cota_aleasa < 1.27:
        continue

    obiect_meci = {
        "meci": nume_meci, 
        "detalii": detalii, 
        "pariu": pariu_ales, 
        "cota": round(cota_aleasa, 2),
        "ora": ora_meci  # Folosit exclusiv pentru funcția de sortare cronologică
    }

    # Distribuiere după etape
    if home_played >= 12 and away_played >= 12:
        bilete_safe.append(obiect_meci)
    if home_played >= 7 and away_played >= 7:
        bilete_mega.append(obiect_meci)
    if home_played >= 5 and away_played >= 5:
        bilete_risky.append(obiect_meci)

# ⏳ SORTARE CRONOLOGICĂ AUTOMATĂ (După orele de disputare)
bilete_safe = sorted(bilete_safe, key=lambda x: x["ora"])
bilete_mega = sorted(bilete_mega, key=lambda x: x["ora"])
bilete_risky = sorted(bilete_risky, key=lambda x: x["ora"])

# 📊 AFISARE COLOANE SIMETRICE CA IN ACCAS BUILDER SCORES24
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🟢 Safe Accumulator")
    st.caption("Min. 12 meciuri | Ordonat cronologic | Cote ≥ 1.27")
    st.markdown("---")
    m_safe = bilete_safe[:4]
    c_safe = 1.0
    for s in m_safe: c_safe *= s["cota"]
    st.markdown(f"**Cota Totală:** <span style='color:#00cc66; font-size:22px; font-weight:bold;'>{c_safe:.2f}</span>", unsafe_allow_html=True)
    
    for s in m_safe:
        st.markdown(f"🔹 **{s['cota']:.2f}** | **{s['meci']}**<br><span style='color:gray; font-size:12px;'>➔ {s['pariu']} ({s['detalii']})</span>", unsafe_allow_html=True)
    if m_safe: st.info("💰 Miza recomandată: 20 RON")

with col2:
    st.markdown("### 🟡 Mega Accumulator")
    st.caption("Min. 7 meciuri | Ordonat cronologic | Cote ≥ 1.27")
    st.markdown("---")
    m_mega = bilete_mega[:4]
    c_mega = 1.0
    for s in m_mega: c_mega *= s["cota"]
    st.markdown(f"**Cota Totală:** <span style='color:#ffcc00; font-size:22px; font-weight:bold;'>{c_mega:.2f}</span>", unsafe_allow_html=True)
    
    for s in m_mega:
        st.markdown(f"🔸 **{s['cota']:.2f}** | **{s['meci']}**<br><span style='color:gray; font-size:12px;'>➔ {s['pariu']} ({s['detalii']})</span>", unsafe_allow_html=True)
    if m_mega: st.success("💰 Miza recomandată: 10 RON")

with col3:
    st.markdown("### 🔴 Risky Accumulator")
    st.caption("Min. 5 meciuri | Ordonat cronologic | Cote ≥ 1.27")
    st.markdown("---")
    m_risk = bilete_risky[:3]
    c_risk = 1.0
    for s in m_risk: c_risk *= s["cota"]
    st.markdown(f"**Cota Totală:** <span style='color:#ff3333; font-size:22px; font-weight:bold;'>{c_risk:.2f}</span>", unsafe_allow_html=True)
    
    for s in m_risk:
        st.markdown(f"❌ **{s['cota']:.2f}** | **{s['meci']}**<br><span style='color:gray; font-size:12px;'>➔ {s['pariu']} ({s['detalii']})</span>", unsafe_allow_html=True)
    if m_risk: st.warning("💰 Miza recomandată: 5 RON")
