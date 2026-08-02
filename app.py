import streamlit as st
import json
from google.oauth2.service_account import Credentials
import gspread

st.title("Test Connessione Google Sheets")

try:
    # 1. Recupera i secrets
    if "gcp_service_account" not in st.secrets:
        st.error("Sezione [gcp_service_account] non trovata nei secrets di Streamlit!")
        st.stop()

    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # 2. Corregge i newline della chiave privata
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    st.write("Email del bot:", creds_dict.get("client_email"))
    st.write("Lunghezza chiave privata:", len(creds_dict.get("private_key", "")))

    # 3. Definisce gli scope
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # 4. Tenta la creazione delle credenziali (qui falliva se c'era padding o PEM errato)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    st.success("Credenziali caricate con successo! La chiave è valida.")

    # 5. Tenta il collegamento a gspread (sostituisci con il nome del tuo foglio o un ID di test se vuoi)
    client = gspread.authorize(creds)
    st.success("Autenticazione gspread completata con successo!")

except Exception as e:
    st.error(Annesso errore durante il test:)
    st.exception(e)
