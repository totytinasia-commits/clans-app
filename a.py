import pandas as pd
import streamlit as st

# Configurazione della pagina per adattarla perfettamente agli schermi dei telefoni
st.set_page_config(
    page_title="Gestione Clan", page_icon="🛡️", layout="centered"
)

# Stile CSS per evitare lo zoom orizzontale esagerato e sistemare i margini mobili
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1.5rem !important;
    }
    h1 {
        font-size: 1.8rem !important;
    }
    h2 {
        font-size: 1.4rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Intitolazione dell'App
st.title("🛡️ Gestione Clan")
st.write("Benvenuto nel pannello di controllo ottimizzato per smartphone.")

# Menu di navigazione laterale o a tab
menu = st.selectbox("Seleziona Sezione", ["Home / Membri", "Tornei e Match"])

if menu == "Home / Membri":
  st.header("👥 Elenco Membri")

  # Esempio di tabella dati reattiva che si adatta allo schermo
  dati_esempio = pd.DataFrame({
      "Giocatore": ["Alpha", "Beta", "Gamma", "Delta"],
      "Ruolo": ["Capo", "Anziano", "Membro", "Membro"],
      "Trofei": [3200, 2950, 2400, 2100],
  })

  # use_container_width=True fa in modo che la tabella non esca dallo schermo del telefono
  st.dataframe(dati_esempio, use_container_width=True)

elif menu == "Tornei e Match":
  st.header("⚔️ Stato Tornei")
  st.info("Qui puoi inserire i dettagli dei prossimi match del clan.")
  # Esempio di metrica mobile
  col1, col2 = st.columns(2)
  col1.metric("Vittorie", "14", "+2")
  col2.metric("Sconfitte", "3", "-1")

# Footer
st.markdown("---")
st.caption("Ottimizzato per Mobile - Gestione Clan 2026")