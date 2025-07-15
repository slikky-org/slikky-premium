import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import openai
import locale
from io import BytesIO
import datetime
import mysql.connector
import bcrypt

from openai import OpenAI

# Use environment variables for DB credentials
DB_HOST = os.environ.get("EXTERNAL_DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("EXTERNAL_DB_PORT", 3306))
DB_NAME = os.environ.get("EXTERNAL_DB_NAME", "premium")
DB_USER = os.environ.get("EXTERNAL_DB_USER", "premium")
DB_PASSWORD = os.environ.get("EXTERNAL_DB_PASS", "Q3Y#ybA2X*2.nBr")

def check_login(email, wachtwoord):
    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor(dictionary=True)
    # Fetch the hash from the wachtwoord column in the users table
    cursor.execute("SELECT * FROM users WHERE email=%s LIMIT 1", (email,))
    user_row = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_row and 'wachtwoord' in user_row:
        hash_from_db = user_row['wachtwoord']
        if bcrypt.checkpw(wachtwoord.encode('utf-8'), hash_from_db.encode('utf-8')):
            return user_row
    return None

# --- Streamlit login ---
if "user" not in st.session_state:
    # Zet hier het pad naar je gewenste PNG of SVG logo
    logo_pad = "images/logo_slikky.svg"  # of PNG als je liever raster gebruikt

    # SVG laden
    with open(logo_pad, "r") as f:
        svg_logo = f.read()

    st.markdown(
        f"""
        <div style='display: flex; flex-direction: column; align-items: center; margin-top:60px; margin-bottom:12px;'>
            <div style="width:700px; margin-bottom:6px;">{svg_logo}</div>
            <div style="width:100%; text-align:center;">
                <span style="
                    font-family: 'Poppins', sans-serif;
                    font-size: 20px;
                    font-weight: 700;
                    color: #00b4d8;
                    text-transform: lowercase;
                    letter-spacing: 0px;">login met je mailadres en wachtwoord</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
        <style>
        .slikky-login input {
            background: #f4f6fa !important;
            border: 2px solid #e3eaf4 !important;
            border-radius: 10px !important;
            padding: 13px 16px !important;
            font-size: 18px !important;
            color: #2d4059 !important;
            font-family: 'Poppins', sans-serif !important;
            margin-bottom: 16px !important;
        }
        .slikky-login label {
            font-family: 'Poppins', sans-serif !important;
            font-size: 19px !important;
            font-weight: 700 !important;
            color: #2d4059 !important;
        }
        .slikky-login button {
            background: #00b4d8 !important;
            color: #fff !important;
            font-size: 20px !important;
            font-family: 'Nunito Sans', sans-serif !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 14px 0 !important;
            margin-top: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Loginformulier
    with st.form(key="login_form"):
        st.markdown('<div class="slikky-login">', unsafe_allow_html=True)
        email = st.text_input("E-mail")
        wachtwoord = st.text_input("Wachtwoord", type="password")
        login_btn = st.form_submit_button("Inloggen")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(
    """
    <div style="text-align:right; margin-top:-10px; margin-bottom:16px;">
      <a href="https://slikky.nl/wachtwoord-reset/" target="_blank" style="color:#00b4d8; font-family:Poppins, sans-serif; font-size:15px; text-decoration:underline;">
        wachtwoord vergeten?
      </a>
    </div>
    """,
    unsafe_allow_html=True
)


    if login_btn:
        user = check_login(email, wachtwoord)
        if user:
            st.session_state["user"] = user
            st.success(f"Ingelogd als {user['email']} ({user['rol']})")
            st.rerun()
        else:
            st.error("Ongeldige inloggegevens. Probeer opnieuw.")
    st.stop()

    # Loginformulier
    with st.form(key="login_form"):
        st.markdown('<div class="slikky-login">', unsafe_allow_html=True)
        email = st.text_input("E-mail")
        wachtwoord = st.text_input("Wachtwoord", type="password")
        login_btn = st.form_submit_button("Inloggen")
        st.markdown('</div>', unsafe_allow_html=True)

    if login_btn:
        user = check_login(email, wachtwoord)
        if user:
            st.session_state["user"] = user
            st.success(f"Ingelogd als {user['email']} ({user['rol']})")
            st.rerun()
        else:
            st.error("Ongeldige inloggegevens. Probeer opnieuw.")
    st.stop()

user = st.session_state["user"]
col1, col2 = st.columns([4, 1])
with col1:
    st.info(f"Ingelogd als: {user['email']} ({user['rol']})")
with col2:
    if st.button("Uitloggen", key="uitlog_boven"):
        st.session_state.pop("user")
        st.rerun()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project=os.getenv("OPENAI_PROJECT_ID")
)

def tel_gebruik():
    bestand = 'slikky_log.csv'
    bestaat = os.path.isfile(bestand)
    tijdstip = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
    if bestaat:
        with open(bestand, 'r') as file:
            regels = file.readlines()
            gebruik_id = len(regels)
    else:
        gebruik_id = 1
    with open(bestand, 'a') as file:
        if not bestaat:
            file.write('Datum,Tijd,Gebruik_ID,Advies_Type\n')
        file.write(f"{tijdstip.split(',')[0]},{tijdstip.split(',')[1]},{gebruik_id},{user['rol'].capitalize()}\n")

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle

# Zet de Nederlandse tijdnotatie
try:
    locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')

if st.session_state.get("reset", False):
    st.session_state.update({
        "gender": "Dhr.",
        "naam": "",
        "geboortedatum": datetime.date(2000, 1, 1),
        "zorgorganisatie": "",
        "locatie": "",
        "advies_datum": datetime.date.today(),
        "geldigheid": "4 weken",
        "geldigheid_datum": datetime.date.today(),
        "auteur": "",
        "functie": "",
        "advies": "",
        "toezicht": None,
        "allergieën": "",
        "voorkeuren": "",
        "reset": False
    })
    st.rerun()

st.image("images/logo_slikky.png", width=150)
st.markdown("### Voedingsadvies bij slikproblemen")
st.write("Voer het logopedisch advies in, geef IDDSI-niveaus en specifieke voorkeuren op.")

st.subheader("🔒 Cliëntgegevens (worden niet opgeslagen)")
col1, col2, col3 = st.columns([1, 3, 2])
client_gender = col1.selectbox("Aanhef:", ["Dhr.", "Mevr.", "X"], key="gender")
client_naam = col2.text_input("Naam van de cliënt:", key="naam")
client_geboortedatum = col3.date_input("Geboortedatum:", format="DD/MM/YYYY", min_value=datetime.date(1933, 1, 1), max_value=datetime.date.today(), key="geboortedatum")

col_org1, col_org2 = st.columns([2, 2])
zorgorganisatie = col_org1.text_input("Zorgorganisatie:", key="zorgorganisatie")
locatie = col_org2.text_input("Locatie:", key="locatie")

col4, col5 = st.columns([2, 2])
advice_datum = col4.date_input("Datum aanmaak voedingsadvies:", format="DD/MM/YYYY", key="advies_datum")
geldigheid_optie = col5.selectbox("Geldig voor:", ["4 weken", "6 weken", "8 weken", "Anders"], key="geldigheid")

if geldigheid_optie == "Anders":
    col6, _ = st.columns([2, 2])
    geldigheid_datum = col6.date_input("Kies einddatum:", format="DD/MM/YYYY", key="geldigheid_datum")
else:
    geldigheid_datum = None

col_creator1, col_creator2 = st.columns([2, 2])
aangemaakt_door = col_creator1.text_input("Aangemaakt door:", key="auteur")
functie = col_creator2.text_input("Functie:", key="functie")

# --- Rolafhankelijk: adviesveld en allergie/voorkeuren
if user and user["rol"] == "premium":
    advies = st.text_area("📄 Logopedisch advies:", key="advies")
    onder_toezicht_optie = st.radio(
        "🚨 Moet de cliënt eten onder toezicht?",
        options=["Ja", "Nee"],
        index=None,
        key="toezicht",
        help="Selecteer een van beide opties om verder te gaan."
    )
    if onder_toezicht_optie == "Ja":
        hulp_bij_eten_optie = st.radio(
            "👐 Moet de cliënt geholpen worden met eten?",
            options=["Ja", "Nee"],
            index=None,
            key="hulp_bij_eten_radio",
            help="Selecteer een van beide opties om verder te gaan."
        )
    else:
        hulp_bij_eten_optie = None
    allergieën = st.text_input("⚠️ Allergieën (optioneel, scheid met komma's):", key="allergie")
    voorkeuren = st.text_input("✅ Voedselvoorkeuren (optioneel, scheid met komma's):", key="voorkeuren")
else:
    advies = st.text_area(
        "📄 Logopedisch advies:",
        placeholder="Beschrijf hier kort het slikadvies. Noem bijv. gewenste voeding, toezicht of hulp bij eten.",
        help="Wat je hier invult — zoals toezicht of hulp — wordt automatisch verwerkt in het voedingsadvies. Uitgebreide invoer is beschikbaar in SLIKKY® Premium.",
        key="advies",
        max_chars=1250
    )
    onder_toezicht_optie = st.radio(
        "🚨 Moet de cliënt eten onder toezicht?",
        options=["Ja", "Nee"],
        index=None,
        key="toezicht",
        help="Eten onder toezicht én hulp bij eten zijn onderdeel van SLIKKY® Premium.",
        disabled=True
    )
    hulp_bij_eten_optie = None
    allergieën = st.text_input("⚠️ Allergieën (optioneel, scheid met komma's):", key="allergie", max_chars=75, help="Max. 75 tekens. Uitgebreide invoer is beschikbaar in SLIKKY® Premium.")
    voorkeuren = st.text_input("✅ Voedselvoorkeuren (optioneel, scheid met komma's):", key="voorkeuren", max_chars=75, help="Max. 75 tekens. Uitgebreide invoer is beschikbaar in SLIKKY® Premium.")

st.write("---")
st.write("👇 Kies de gewenste consistentieniveaus:")

iddsi_vast = st.selectbox("🍽️ Niveau voor voedsel:", [
    "Niveau 3: Dik vloeibaar",
    "Niveau 4: Glad gemalen",
    "Niveau 5: Fijngemalen en smeuïg",
    "Niveau 6: Zacht & klein gesneden",
    "Niveau 7A: Makkelijk te kauwen",
    "Niveau 7: Normaal"
], index=5, key="iddsi_vast")

iddsi_vloeibaar = st.selectbox("🥣 Niveau voor vloeistof:", [
    "Niveau 0: Dun vloeibaar",
    "Niveau 1: Licht vloeibaar",
    "Niveau 2: Matig vloeibaar",
    "Niveau 3: Dik vloeibaar",
    "Niveau 4: Zeer dik vloeibaar"
], key="iddsi_vloeibaar")

# --- Overlapcontrole (altijd actief)
if allergieën.strip() and voorkeuren.strip():
    allergie_lijst = [a.strip().lower() for a in allergieën.split(',')]
    voorkeur_lijst = [v.strip().lower() for v in voorkeuren.split(',')]
    overlap = set(allergie_lijst) & set(voorkeur_lijst)
    if overlap:
        overlappende_term = ', '.join(overlap)
        st.error(f"⚠️ Let op: het volgende komt zowel voor bij allergieën als bij voorkeuren: {overlappende_term}. Pas je invoer aan.")
        st.stop()

# --- Filters rol-afhankelijk
st.write("### 🔍 Voedingsmiddelenfilter (optioneel)")
if user and user["rol"] == "premium":
    toon_allergie_filter = st.checkbox("Sluit de volgende *intoleranties of allergenen* uit:")
    uitsluitingen = []
    if toon_allergie_filter:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.checkbox("Amandelen"): uitsluitingen.append("amandelen")
            if st.checkbox("Gluten"): uitsluitingen.append("gluten")
            if st.checkbox("Koemelk"): uitsluitingen.append("koemelk")
            if st.checkbox("Kippenei"): uitsluitingen.append("kippenei")
            if st.checkbox("Lactose"): uitsluitingen.append("lactose")
        with col2:
            if st.checkbox("Lupine"): uitsluitingen.append("lupine")
            if st.checkbox("Mosterd"): uitsluitingen.append("mosterd")
            if st.checkbox("Noten"): uitsluitingen.append("noten")
            if st.checkbox("Pinda’s"): uitsluitingen.append("pinda’s")
            if st.checkbox("Schaal-/schelpdieren"): uitsluitingen.append("schaal-/schelpdieren")
        with col3:
            if st.checkbox("Sesamzaad"): uitsluitingen.append("sesamzaad")
            if st.checkbox("Soja"): uitsluitingen.append("soja")
            if st.checkbox("Sulfiet"): uitsluitingen.append("sulfiet")
            if st.checkbox("Tarwe"): uitsluitingen.append("tarwe")
            if st.checkbox("Vis"): uitsluitingen.append("vis")

    toon_dieet_filter = st.checkbox("Sluit de volgende *dieet- of levensstijlgerelateerde* voedingsmiddelen uit:")
    if toon_dieet_filter:
        col4, col5, col6 = st.columns(3)
        with col4:
            if st.checkbox("Alcohol"): uitsluitingen.append("alcohol")
            if st.checkbox("E-nummers"): uitsluitingen.append("E-nummers")
            if st.checkbox("Kunstmatige zoetstoffen"): uitsluitingen.append("kunstmatige zoetstoffen")
        with col5:
            if st.checkbox("Rauw voedsel"): uitsluitingen.append("rauw voedsel")
            if st.checkbox("Suiker"): uitsluitingen.append("suiker")
            if st.checkbox("Vegetarisch"): uitsluitingen.append("vegetarisch")
        with col6:
            if st.checkbox("Veganistisch"): uitsluitingen.append("veganistisch")
            if st.checkbox("Varkensvlees"): uitsluitingen.append("varkensvlees")
            if st.checkbox("Zout / natrium"): uitsluitingen.append("zout/natrium")
            anders = st.text_input("Anders, namelijk:")
            if anders:
                uitsluitingen.append(anders)
else:
    toon_allergie_filter = st.checkbox(
        "Sluit de volgende *intoleranties of allergenen* uit:",
        disabled=True,
        help="Deze filterfunctie is onderdeel van SLIKKY® Premium."
    )
    toon_dieet_filter = st.checkbox(
        "Sluit de volgende *dieet- of levensstijlgerelateerde* voedingsmiddelen uit:",
        disabled=True,
        help="Deze filterfunctie is onderdeel van SLIKKY® Premium."
    )
    uitsluitingen = []  # mag leeg blijven

uitsluit_tekst = ", ".join(uitsluitingen) if uitsluitingen else "Geen extra uitsluitingen opgegeven."

# --- Geselecteerde uitsluitingen tonen
if uitsluitingen:
    uitsluitingen = sorted(uitsluitingen, key=lambda x: x.lower())
    kolom_lengte = (len(uitsluitingen) + 2) // 3
    kolom1 = uitsluitingen[:kolom_lengte]
    kolom2 = uitsluitingen[kolom_lengte:2*kolom_lengte]
    kolom3 = uitsluitingen[2*kolom_lengte:]

    def maak_lijst(kolom):
        if kolom:
            return "<ul>" + "".join(f"<li>{item.capitalize()}</li>" for item in kolom) + "</ul>"
        else:
            return ""

    st.markdown(
        f"""
        <div style="background-color: #e6f4ea; padding: 20px; border-radius: 10px;
                    animation: fadeIn 0.5s ease-in;">
            <h4 style="color: #1a7f37;">Geselecteerde uitsluitingen:</h4>
            <div style="display: flex;">
                <div style="flex: 1;">{maak_lijst(kolom1)}</div>
                <div style="flex: 1;">{maak_lijst(kolom2)}</div>
                <div style="flex: 1;">{maak_lijst(kolom3)}</div>
            </div>
        </div>
        <style>
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        </style>
        <div style="margin-bottom: 30px;"></div>
        """,
        unsafe_allow_html=True
    )

# === Genereer voedingsprogramma-knop ===
if st.button("🎯 Genereer Voedingsprogramma"):

    # --- Validatie afhankelijk van rol ---
    if not advies:
        st.warning("⚠️ Voer eerst een logopedisch advies in.")
    elif user and user["rol"] == "premium":
        if onder_toezicht_optie not in ["Ja", "Nee"]:
            st.warning("⚠️ Kies of de cliënt onder toezicht moet eten.")
        elif onder_toezicht_optie == "Ja" and hulp_bij_eten_optie not in ["Ja", "Nee"]:
            st.warning("⚠️ Kies of de cliënt geholpen moet worden met eten.")
        else:
            proceed = True
    else:
        proceed = True

    if 'proceed' in locals() and proceed:
        st.success("✅ Alles correct ingevuld. Hier komt je advies...")
        toezicht_tekst = "De cliënt moet eten onder toezicht." if (user and user["rol"] == "premium" and onder_toezicht_optie == "Ja") else ""
        hulp_tekst = "De cliënt moet geholpen worden met eten." if (user and user["rol"] == "premium" and hulp_bij_eten_optie == "Ja") else ""
        advies_datum = st.session_state["advies_datum"]
        geldigheid_tekst = geldigheid_datum.strftime('%d/%m/%Y') if geldigheid_datum else f"{geldigheid_optie} vanaf {advies_datum.strftime('%d/%m/%Y')}"
        uitsluit_tekst = ", ".join(uitsluitingen) if uitsluitingen else "Geen extra uitsluitingen opgegeven."

        # --- Rolafhankelijke prompt! ---
        if user and user["rol"] == "premium":
            golden_prompt = f"""Jouw PREMIUM prompt hier... (plak jouw premium prompt in dit blok)"""
        else:
            golden_prompt = f"""Je bent een AI-diëtist die voedingsprogramma's opstelt op basis van logopedisch advies.
Je houdt strikt rekening met de opgegeven IDDSI-niveaus, allergieën, voorkeuren en eventuele voedselbeperkingen.

📌 SLIKKY® Basis – Promptversie: 2.2

Toon deze regels vetgedrukt bovenaan het advies:
**Dit voedingsadvies is bedoeld voor {client_gender} {client_naam} ({client_geboortedatum}).**
**Geldig tot: {geldigheid_tekst}**
**Zorgorganisatie: {zorgorganisatie} | Locatie: {locatie}**
**Aangemaakt door: {aangemaakt_door} ({functie})**

**1. Advies en vertaling naar voedingsplan**
- Herformuleer het logopedisch advies in je eigen woorden. Vermijd letterlijke herhaling.
- Licht toe hoe dit advies zich vertaalt naar een concreet voedingsplan binnen het IDDSI-raamwerk.
- Benoem concrete gevolgen voor voedselconsistentie, toezicht tijdens eten of begeleiding.
- Vermijd dubbele of herhaalde formuleringen.
- Formuleer het advies concreet. Vermijd vaag taalgebruik.
- Gebruik duidelijke, feitelijke taal. Vermijd beeldspraak of metaforen zoals "scherpe randen" of "ruw mondgevoel".
- Alleen als in het logopedisch advies expliciet toezicht of hulp genoemd wordt, neem dat dan duidelijk en letterlijk op.
- Als er géén informatie is ingevuld over toezicht of hulp bij eten, voeg dan een algemene aanbeveling toe zoals: “Controleer altijd of {client_gender} {client_naam} onder toezicht moet eten, of hulp bij het eten behoeft.” Vermijd stellige bewoording over noodzakelijk toezicht/hulp als die info ontbreekt.
- Vat het logopedisch advies puntsgewijs samen (maximaal 5 korte bullets, geen herhaling).
- Beperk dit onderdeel tot maximaal 5 korte, begrijpelijke zinnen.

**2. Belangrijke gegevens**  
- IDDSI niveau voedsel: {iddsi_vast}  
- IDDSI niveau vloeistof: {iddsi_vloeibaar}  
- Uitsluitingen: {uitsluit_tekst}  
- Allergieën: {allergieën}  
- Voorkeuren: {voorkeuren}  
- {toezicht_tekst}  
- {hulp_tekst}

**3. Concreet voedingsprogramma**  
- Geef maximaal 3 geschikte voedingssuggesties per categorie (vast en vloeibaar).
- Noem maximaal 3 voedingsmiddelen die moeten worden vermeden en geef bij elk een korte reden (bijv. allergie, verhoogd slikrisico, structuur).
- Geef een realistisch voorbeeld dagmenu (ontbijt, lunch, diner, tussendoor).
- Vermeld waar relevant welk IDDSI-niveau van toepassing is bij onderdelen van het dagmenu (bijv. “IDDSI 6: gemalen kipfilet met jus”).
- Bied maximaal 3 alternatieven bij allergieën of voorkeuren. Gebruik daarbij waar mogelijk de opgegeven voorkeuren. Vermijd het noemen van uitgesloten stoffen (zoals zuivel of gluten) in deze alternatieven.
- Vermijd dubbele voedingsadviezen of herhaling tussen secties.

Belangrijke instructies:
- Gebruik alleen gangbare, veilig verkrijgbare producten (geen zelfbedachte of exotische ingrediënten).
- Structureer je output altijd in twee inhoudelijke secties: (1) vast voedsel, (2) vloeibaar voedsel. Voeg ook een apart kopje toe voor “Belangrijke instructies” waarin je specifieke aandachtspunten (zoals toezicht of hulp) benoemt als die zijn genoemd.
- Houd de toon professioneel, praktisch en begrijpelijk voor zorgprofessionals.
- Gebruik korte bulletpoints.
- Voeg geen verzachtende of tegenstrijdige zinnen toe als deze afwijken van het oorspronkelijke logopedisch advies (zoals "toezicht kan helpen" terwijl toezicht verplicht is).
- Sluit af met een warme, passende zin voor het zorgteam, zonder te herhalen wat al genoemd is.
- Geef daaronder **altijd** als laatste regel, losstaand onderaan het document:  
  *Bij twijfel over veiligheid of toepassing: raadpleeg een logopedist of diëtist.*
- Antwoord altijd in het Nederlands.
- Volg de nummering en structuur zoals hierboven in je gegenereerde tekst.
"""

        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een AI gespecialiseerd in voedingsadvies voor cliënten met slikproblemen."},
                    {"role": "user", "content": golden_prompt}
                ]
            )
            advies_output = response.choices[0].message.content

            st.subheader("🚨 Belangrijke waarschuwing")
            if user and user["rol"] == "premium" and onder_toezicht_optie == "Ja":
                st.markdown(
                    '<div style="background-color:#ffcccc;padding:15px;border-radius:10px;color:#990000;font-weight:bold;">🚨 Deze persoon mag alleen eten onder toezicht!</div>',
                    unsafe_allow_html=True
                )
            if user and user["rol"] == "premium" and hulp_bij_eten_optie == "Ja":
                st.markdown(
                    '<div style="background-color:#ffcccc;padding:15px;border-radius:10px;color:#990000;font-weight:bold;">⚠️ Deze persoon moet geholpen worden met eten!</div>',
                    unsafe_allow_html=True
                )

            st.subheader("📋 Voedingsadvies:")
            st.markdown(advies_output)

            # --- PDF Export rol-afhankelijk ---
            if user and user["rol"] == "premium":
                try:
                    buffer = BytesIO()
                    pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
                    elements = []
                    styles = getSampleStyleSheet()
                    styles.add(ParagraphStyle(name='Body', fontSize=11, leading=16, alignment=TA_LEFT))
                    styles.add(ParagraphStyle(name='BoldBox', fontSize=12, leading=16, alignment=TA_LEFT, textColor=colors.red))
                    styles.add(ParagraphStyle(name='BoldBody', fontSize=11, leading=16, alignment=TA_LEFT, fontName='Helvetica-Bold'))

                    try:
                        logo = Image("images/logo_slikky.png", width=3.5*cm, height=1*cm)
                        elements.append(logo)
                    except Exception as e:
                        elements.append(Paragraph("⚠️ Logo niet gevonden: " + str(e), styles['Body']))

                    elements.append(Spacer(1, 12))
                    elements.append(Paragraph("---", styles['Body']))
                    elements.append(Paragraph("Deze app slaat géén cliëntgegevens op.", styles['Body']))
                    elements.append(Paragraph("---", styles['Body']))
                    elements.append(Spacer(1, 12))

                    if onder_toezicht_optie == "Ja":
                        toezicht_box = Paragraph("\U0001F6A8 Deze persoon mag alleen eten onder toezicht!", styles["BoldBox"])
                        elements.append(toezicht_box)
                        elements.append(Spacer(1, 12))
                    if hulp_bij_eten_optie == "Ja":
                        hulp_box = Paragraph("\u26A0\ufe0f Deze persoon moet geholpen worden met eten!", styles["BoldBox"])
                        elements.append(hulp_box)
                        elements.append(Spacer(1, 12))

                    for regel in advies_output.split("\n"):
                        if regel.strip() != "":
                            if regel.strip().startswith("**") and regel.strip().endswith("**"):
                                tekst_zonder_sterren = regel.strip().strip("*")
                                elements.append(Paragraph(tekst_zonder_sterren, styles['BoldBody']))
                            else:
                                elements.append(Paragraph(regel.strip(), styles['Body']))
                            elements.append(Spacer(1, 6))

                    elements.append(Spacer(1, 60))
                    elements.append(Paragraph("SLIKKY is een officieel geregistreerd merk (Benelux, 2025)", styles['Body']))
                    elements.append(Spacer(1, 40))

                    try:
                        merkbadge = Image("images/logo_slikky.png", width=3.5*cm, height=1*cm)
                        merkbadge.hAlign = 'CENTER'
                        elements.append(merkbadge)
                    except Exception as e:
                        elements.append(Paragraph("⚠️ Merkbadge niet gevonden: " + str(e), styles['Body']))

                    def header_footer(canvas, doc):
                        canvas.saveState()
                        canvas.setFont('Helvetica', 9)
                        titel = f"Voedingsadvies voor {client_gender} {client_naam} ({client_geboortedatum.strftime('%d/%m/%Y')})"
                        canvas.drawString(2 * cm, A4[1] - 1.5 * cm, titel)
                        page_num = f"Pagina {doc.page}"
                        canvas.drawRightString(A4[0] - 2 * cm, 1.5 * cm, page_num)
                        canvas.restoreState()

                    pdf.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
                    buffer.seek(0)
                    tel_gebruik()

                    st.download_button(
                        label="💾 Opslaan als PDF",
                        data=buffer,
                        file_name=f"Slikky_voedingsadvies_{client_naam.strip().replace(' ', '_')}_{client_geboortedatum.strftime('%d-%m-%Y')}.pdf",
                        mime="application/pdf"
                    )

                except Exception as e:
                    st.error(f"❌ Er ging iets mis bij het genereren van de PDF: {e}")

            else:
                st.button("💾 Opslaan als PDF", disabled=True)
                st.markdown("⚠️ PDF-export is beschikbaar in SLIKKY® Premium.")
                st.markdown("<small>📄 Tip: gebruik <strong>Ctrl+P</strong> (of <strong>Cmd+P</strong> op Mac) om deze pagina te printen of op te slaan als PDF.</small>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Er ging iets mis bij het ophalen van het advies: {e}")

if st.button("🔁 Herstel alle velden"):
    st.session_state["reset"] = True
    st.rerun()

def footer():
    st.markdown("---")
    if user and user["rol"] == "premium":
        st.markdown("<sub><i>SLIKKY® Premium v2025.07.1</i></sub>", unsafe_allow_html=True)
    else:
        st.markdown("<sub><i>SLIKKY® Basis v2025.07.1</i></sub>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="text-align:center; margin-top:15px;">
              <a href="https://slikky.nl/premium" style="font-size:18px; color:#1a7f37; font-weight:bold;">
                🚀 Meer functies? Probeer SLIKKY® Premium &raquo;
              </a>
            </div>
            """,
            unsafe_allow_html=True
        )

footer()
st.markdown("---")
if st.button("Uitloggen", key="uitlog_onder"):
    st.session_state.pop("user")
    st.rerun()
