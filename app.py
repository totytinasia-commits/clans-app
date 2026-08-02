import streamlit as st
import json
import tempfile
from google.oauth2.service_account import Credentials
import gspread

st.title("Test Connessione Google Sheets")

try:
    if "gcp_service_account" not in st.secrets:
        st.error("Sezione [gcp_service_account] non trovata nei secrets di Streamlit!")
        st.stop()

    # Legge il dizionario dai secrets di Streamlit
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # Corregge eventuali newline letterali se presenti
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    st.write("Email del bot:", creds_dict.get("client_email"))
    st.write("Lunghezza chiave privata:", len(creds_dict["private_key"]))

    # Scrive le credenziali in un file JSON temporaneo per bypassare il controllo di padding in memoria
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp:
        json.dump(creds_dict, temp)
        temp_path = temp.name

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Caricamento tramite file temporaneo (soluzione blindata)
    creds = Credentials.from_service_account_file(temp_path, scopes=scopes)
    st.success("Credenziali caricate con successo tramite file temporaneo!")

    # Connessione a Google Sheets
    client = gspread.authorize(creds)
    st.success("Autenticazione gspread completata con successo!")

except Exception as e:
    st.error("Errore riscontrato durante il test:")
    st.exception(e)
