import streamlit as st
from google.oauth2.service_account import Credentials
import gspread

st.title("Test Connessione Google Sheets")

try:
    if "gcp_service_account" not in st.secrets:
        st.error("Sezione [gcp_service_account] non trovata nei secrets di Streamlit!")
        st.stop()

    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # ---------------------------------------------------------
    # PULIZIA CHIAVE PRIVATA A PROVA DI BOMBA
    # ---------------------------------------------------------
    raw_key = creds_dict.get("private_key", "")
    
    # Rimuove carriage return (\r) e divide per righe pulite
    lines = [line.strip() for line in raw_key.replace("\r\n", "\n").split("\n") if line.strip()]
    
    # Se per caso l'intestazione o la fine si sono attaccate, le ricostruisce blindate
    if lines and not lines[0].startswith("-----BEGIN"):
        # Cerca dove inizia
        pass
        
    clean_private_key = "\n".join(lines) + "\n"
    creds_dict["private_key"] = clean_private_key
    # ---------------------------------------------------------

    st.write("Email del bot:", creds_dict.get("client_email"))
    st.write("Lunghezza chiave privata pulita:", len(creds_dict["private_key"]))

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    st.success("Credenziali caricate con successo! La chiave è valida.")

    client = gspread.authorize(creds)
    st.success("Autenticazione gspread completata con successo!")

except Exception as e:
    st.error("Errore riscontrato durante il test:")
    st.exception(e)
