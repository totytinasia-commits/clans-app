import streamlit as st
import json
from google.oauth2.service_account import Credentials
import gspread

st.title("Test Connessione Google Sheets")

try:
    if "gcp_service_account" not in st.secrets:
        st.error("Sezione [gcp_service_account] non trovata nei secrets di Streamlit!")
        st.stop()

    # Legge il dizionario dai secrets
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # Converte i newline letterali in veri newline di sistema
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    st.write("Email del bot:", creds_dict.get("client_email"))
    st.write("Lunghezza chiave privata:", len(creds_dict["private_key"]))

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Caricamento diretto delle credenziali
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    st.success("Credenziali caricate con successo!")

    # Connessione a Google Sheets
    client = gspread.authorize(creds)
    st.success("Autenticazione gspread completata con successo!")

except Exception as e:
    st.error("Errore riscontrato durante il test:")
    st.exception(e)
