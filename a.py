import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Clans Leagues Session 7 - EU ELITE",
    layout="wide",
    page_icon="🎮",
)

st.title("🏆 Clans Leagues Session 7 - EU ELITE")

# URL di Google Sheets con il parametro 'rm=minimal' per nascondere i menu e massimizzare lo spazio
sheet_embed_url = "https://docs.google.com/spreadsheets/d/1rDMEgmeHJlO0sBz-U4szt_vGAfgBbu1wDfv3yAlyCUU/edit?usp=sharing&embedded=true&rm=minimal"

st.components.v1.iframe(sheet_embed_url, height=850, scrolling=True)