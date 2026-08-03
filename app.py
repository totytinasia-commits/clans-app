import io
import os
import pandas as pd
import requests
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import time

# --- PERCORSO SICURO PER L'ICONA PNG ---
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "logo.png")

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(
    page_title="Clans Leagues Session 7", 
    page_icon=logo_path if os.path.exists(logo_path) else "🛡️", 
    layout="centered"
)

# --- STILE GRAFICO OTTIMIZZATO ---
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1.5rem !important;
        padding-top: 1.5rem !important;
    }
    .day-box {
        background-color: #1e1e1e;
        border: 1px solid #333333;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .day-title {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 10px;
        border-bottom: 1px solid #333;
        padding-bottom: 5px;
    }
    .stat-card {
        background-color: #0b0f19;
        border: 1px solid #1f293d;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        color: white;
        margin-bottom: 8px;
    }
    .stat-label {
        font-size: 0.7rem;
        color: #93c5fd;
        font-weight: bold;
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 1rem;
        font-weight: bold;
        color: #ffffff;
    }
    .legend-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 15px;
        margin-bottom: 20px;
        font-size: 0.85rem;
        color: #c9d1d9;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- HEADER CON LOGO GRAFICO ---
col_logo1, col_title, col_logo2 = st.columns([1, 3, 1])

with col_logo1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=70)
    else:
        st.markdown("<h1 style='text-align: center; margin: 0;'>🛡️</h1>", unsafe_allow_html=True)

with col_title:
    st.markdown(
        "<h2 style='text-align: center; margin: 0;'>Clans Leagues Session 7</h2>"
        "<p style='text-align: center; color: #ff4b4b; font-weight: bold; margin-top: 5px;'>EU ELITE</p>",
        unsafe_allow_html=True,
    )

with col_logo2:
    if os.path.exists(logo_path):
        st.image(logo_path, width=70)
    else:
        st.markdown("<h1 style='text-align: center; margin: 0;'>⚔️</h1>", unsafe_allow_html=True)

st.markdown("---")

# --- MENU DI NAVIGAZIONE (SIDEBAR) ---
st.sidebar.title("🧭 Navigation")
scelta_menu = st.sidebar.radio(
    "Select Section",
    [
        "SCHEDULE",
        "LEADERBOARD",
        "SYSTEM SCORE",
        "TEAM RESULT",
        "PERSONAL STATS",
        "TOTAL POINT",
    ],
)

# --- VARIABILI GLOBALI E GID ---
SHEET_ID = "1rDMEgmeHJlO0sBz-U4szt_vGAfgBbu1wDfv3yAlyCUU"
GID_LEADERBOARD = 316677537
GID_TEAM_RESULT = 547827980
GID_PERSONAL_STATS = 1111383455

url_export = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

# --- CONFIGURAZIONE GOOGLE SHEETS API & CREDENZIALI ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def ottieni_credenziali():
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    except Exception:
        pass
    
    try:
        return Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    except Exception:
        return None

def scrivi_cella_per_gid(target_gid, cella, valore):
    try:
        creds = ottieni_credenziali()
        if not creds:
            return False
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID)
        
        worksheet = None
        for ws in sheet.worksheets():
            if str(ws.id).strip() == str(target_gid).strip():
                worksheet = ws
                break
        
        if not worksheet:
            worksheet = sheet.get_worksheet(0)
            
        worksheet.update(range_name=cella, values=[[valore]], value_input_option='USER_ENTERED')
        return True
    except Exception as e:
        st.error(f"Error writing to GID {target_gid} (cell {cella}): {e}")
        return False

@st.cache_data(ttl=10)
def scarica_bytes_sheet(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def carica_google_sheet_completo(url):
    try:
        content_bytes = scarica_bytes_sheet(url)
        xls = pd.ExcelFile(io.BytesIO(content_bytes))
        return xls
    except Exception:
        return None

xls_data = carica_google_sheet_completo(url_export)

def get_df_by_gid(target_gid):
    target_title = None
    
    try:
        creds = ottieni_credenziali()
        if creds:
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SHEET_ID)
            
            target_ws = None
            for ws in sheet.worksheets():
                if str(ws.id).strip() == str(target_gid).strip():
                    target_ws = ws
                    target_title = ws.title
                    break
            
            if target_ws:
                data = target_ws.get_all_values()
                if data and len(data) > 0:
                    return pd.DataFrame(data)
    except Exception:
        pass
    
    if not target_title and xls_data is not None:
        try:
            creds = ottieni_credenziali()
            if creds:
                client = gspread.authorize(creds)
                sheet = client.open_by_key(SHEET_ID)
                target_title = next((ws.title for ws in sheet.worksheets() if str(ws.id).strip() == str(target_gid).strip()), None)
        except Exception:
            pass

    try:
        if xls_data is not None:
            sheets_list = xls_data.sheet_names
            if target_title and target_title in sheets_list:
                return pd.read_excel(xls_data, sheet_name=target_title, header=None)
            elif len(sheets_list) > 0:
                return pd.read_excel(xls_data, sheet_name=0, header=None)
    except Exception as ex:
        st.error(f"Error reading GID {target_gid}: {ex}")
            
    return None

# ==========================================
# --- SEZIONE: SCHEDULE ---
# ==========================================
if scelta_menu == "SCHEDULE":
    st.markdown("<div style='background-color: #0e1117; border: 2px solid #262730; border-radius: 12px; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("### 📅 Schedule — EU ELITE\n<p style='color: #888; font-size: 0.9rem;'>All times EST</p>", unsafe_allow_html=True)

    schedule_data = [
        {"WEEK": "WEEK 1", "DATE": "JUL 18", "TIME": "3PM", "MATCHUPS": "NRG • HTTA • POTR • ARES"},
        {"WEEK": "WEEK 2", "DATE": "JUL 25", "TIME": "3PM", "MATCHUPS": "NRG • ARES • GFY • SV"},
        {"WEEK": "WEEK 3", "DATE": "AUG 01", "TIME": "3PM", "MATCHUPS": "NRG • HTTA • GFY • Mafia"},
        {"WEEK": "WEEK 4", "DATE": "AUG 08", "TIME": "3PM", "MATCHUPS": "HTTA • POTR • GFY • SV"},
        {"WEEK": "WEEK 5", "DATE": "AUG 15", "TIME": "3PM", "MATCHUPS": "HTTA • POTR • ARES • Mafia"},
        {"WEEK": "WEEK 6", "DATE": "AUG 22", "TIME": "3PM", "MATCHUPS": "NRG • GFY • SV • Mafia"},
        {"WEEK": "WEEK 7", "DATE": "AUG 29", "TIME": "3PM", "MATCHUPS": "POTR • ARES • SV • Mafia"},
    ]

    from datetime import datetime, timezone, timedelta

    oggi = datetime(2026, 8, 3, tzinfo=timezone(timedelta(hours=2)))

    is_past_list = []
    cleaned_rows = []
    
    for item in schedule_data:
        date_str = f"{item['DATE']} 2026"
        match_date = datetime.strptime(date_str, "%b %d %Y").replace(tzinfo=timezone(timedelta(hours=2)))
        
        is_past_list.append(match_date < oggi)
        cleaned_rows.append({
            "WEEK": item["WEEK"],
            "DATE": item["DATE"],
            "TIME": item["TIME"],
            "MATCHUPS": item["MATCHUPS"]
        })

    df_schedule = pd.DataFrame(cleaned_rows)

    def color_past_rows(row):
        is_past = is_past_list[row.name]
        return ['color: #ff4b4b' if is_past else '' for _ in row.index]

    df_styled = df_schedule.style.apply(color_past_rows, axis=1)

    st.dataframe(df_styled, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# --- SEZIONE: LEADERBOARD ---
# ==========================================
elif scelta_menu == "LEADERBOARD":
    st.markdown("<div style='background-color: #0e1117; border: 2px solid #262730; border-radius: 12px; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("### 🏆 Leaderboard & Match Results - EU ELITE")

    df_leaderboard = get_df_by_gid(GID_LEADERBOARD)

    if df_leaderboard is not None:
        giornate_config = [
            ("Day 1 - 18/07/2026", 2, 3, 12, 15),
            ("Day 2 - 25/07/2026", 5, 6, 12, 15),
            ("Day 3 - 01/08/2026", 8, 9, 12, 15),
            ("Day 4 - 08/08/2026", 2, 3, 22, 25),
            ("Day 5 - 15/08/2026", 5, 6, 22, 25),
            ("Day 6 - 22/08/2026", 8, 9, 22, 25),
            ("Day 7 - 29/08/2026", 2, 3, 32, 35),
        ]

        for nome_giornata, col_team, col_score, r_start, r_end in giornate_config:
            try:
                teams = df_leaderboard.iloc[r_start:r_end+1, col_team].fillna("").tolist()
                scores = df_leaderboard.iloc[r_start:r_end+1, col_score].fillna(0).tolist()
            except Exception:
                teams = ["", "", "", ""]
                scores = [0, 0, 0, 0]

            with st.container():
                st.markdown(f"<div class='day-box'>", unsafe_allow_html=True)
                st.markdown(f"<div class='day-title'>{nome_giornata}</div>", unsafe_allow_html=True)
                
                df_day = pd.DataFrame({"Team": teams, "Score": scores})
                
                def color_first_row(row):
                    if row.name == 0:
                        return ['color: #22c55e; font-weight: bold;' for _ in row.index]
                    return ['' for _ in row.index]

                df_day_styled = df_day.style.apply(color_first_row, axis=1)

                st.dataframe(df_day_styled, use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Unable to read Leaderboard tab.")

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# --- SEZIONE: SYSTEM SCORE ---
# ==========================================
elif scelta_menu == "SYSTEM SCORE":
    st.markdown("<div style='background-color: #0e1117; border: 2px solid #262730; border-radius: 12px; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ System Score")

    system_score_data = {
        "Placement": [7, 5, 3, 1],
        "Kills": [6, 4, 2, 0],
        "Damage": [6, 4, 2, 0]
    }
    df_system_score = pd.DataFrame(system_score_data, index=["1st", "2nd", "3rd", "4th"])
    st.dataframe(df_system_score, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# --- SEZIONE: TEAM RESULT ---
# ==========================================
elif scelta_menu == "TEAM RESULT":
    st.markdown("<div style='background-color: #0e1117; border: 2px solid #262730; border-radius: 12px; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("### 📊 Team Result")

    # --- LEGENDA COLORI SOLO IN TEAM RESULT ---
    st.markdown(
        """
        <div class='legend-box'>
            <strong>🎨 COLOR LEGEND:</strong><br>
            • <span style='color: #22c55e; font-weight: bold;'>Green</span>: Podium / Standing ranking position.<br>
            • <span style='color: #3b82f6; font-weight: bold;'>Blue</span>: Highest score in a single match.<br>
            • <span style='color: #ff4b4b; font-weight: bold;'>Red</span>: Lowest score in a single match.
        </div>
        """,
        unsafe_allow_html=True
    )

    df_team_result = get_df_by_gid(GID_TEAM_RESULT)

    if df_team_result is not None:
        giornate_team_config = [
            ("Day 1 - 18/07/2026", 9, 12),
            ("Day 2 - 25/07/2026", 18, 21),
            ("Day 3 - 01/08/2026", 27, 30),
            ("Day 4 - 08/08/2026", 36, 39),
            ("Day 5 - 15/08/2026", 45, 48),
            ("Day 6 - 22/08/2026", 54, 57),
            ("Day 7 - 29/08/2026", 63, 66),
        ]

        col_team = 4
        match_cols = [9, 14, 19, 24, 29]
        col_total = 30

        for nome_giornata, r_start, r_end in giornate_team_config:
            with st.container():
                st.markdown(f"<div class='day-box'>", unsafe_allow_html=True)
                st.markdown(f"<div class='day-title'>{nome_giornata}</div>", unsafe_allow_html=True)

                try:
                    teams = df_team_result.iloc[r_start:r_end+1, col_team].fillna("").values
                    
                    match_data = {}
                    for idx, c_idx in enumerate(match_cols):
                        try:
                            match_data[f"Game {idx+1}"] = pd.to_numeric(
                                df_team_result.iloc[r_start:r_end+1, c_idx], errors="coerce"
                            ).fillna(0).values
                        except Exception:
                            match_data[f"Game {idx+1}"] = [0, 0, 0, 0]

                    try:
                        totals = pd.to_numeric(
                            df_team_result.iloc[r_start:r_end+1, col_total], errors="coerce"
                        ).fillna(0).values
                    except Exception:
                        totals = [0, 0, 0, 0]

                    df_giornata = pd.DataFrame({"Team": teams, **match_data, "Total": totals})
                    
                    df_giornata["NumericTotal"] = pd.to_numeric(df_giornata["Total"], errors="coerce").fillna(0)
                    df_sorted = df_giornata.sort_values(by="NumericTotal", ascending=False).reset_index(drop=True)

                    podio_labels = ["1° Place", "2° Place", "3° Place", "4° Place"]
                    podio_col = []
                    for i, row in df_sorted.iterrows():
                        pos_str = podio_labels[i] if i < len(podio_labels) else f"{i+1}° Place"
                        podio_col.append(f"{pos_str}: {row['Team']} ({int(row['NumericTotal'])} pts)")

                    df_giornata["Podium / Standing"] = pd.Series(podio_col)
                    df_giornata = df_giornata.drop(columns=["NumericTotal"])

                    def style_team_results(data):
                        game_cols = [c for c in data.columns if c.startswith("Game ")]
                        styles = pd.DataFrame('', index=data.index, columns=data.columns)
                        
                        for idx, row in data[game_cols].iterrows():
                            numeric_vals = pd.to_numeric(row, errors='coerce')
                            if not numeric_vals.isna().all():
                                max_val = numeric_vals.max()
                                min_val = numeric_vals.min()
                                
                                for col in game_cols:
                                    val = pd.to_numeric(data.loc[idx, col], errors='coerce')
                                    if pd.notna(val):
                                        if val == max_val:
                                            styles.loc[idx, col] = 'color: #3b82f6; font-weight: bold;'
                                        elif val == min_val:
                                            styles.loc[idx, col] = 'color: #ff4b4b;'
                        
                        if "Podium / Standing" in data.columns:
                            for idx in data.index:
                                styles.loc[idx, "Podium / Standing"] = 'color: #22c55e; font-weight: bold;'
                                
                        return styles

                    df_styled = df_giornata.style.apply(style_team_results, axis=None)

                    st.dataframe(df_styled, use_container_width=True, hide_index=True)

                except Exception as e:
                    st.error(f"Error loading {nome_giornata}: {e}")

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Unable to connect to Team Result tab.")

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# --- SEZIONE: PERSONAL STATS ---
# ==========================================
elif scelta_menu == "PERSONAL STATS":
    st.markdown("<div style='background-color: #0e1117; border: 2px solid #262730; border-radius: 12px; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("### 👤 Personal Stats Dashboard")

    rounds_config = {
        "ALL": "ALL",
        "Round 1": 1,
        "Round 2": 2,
        "Round 3": 3,
        "Round 4": 4,
        "Round 5": 5,
        "Round 6": 6,
        "Round 7": 7,
    }
    
    col1, col2 = st.columns(2)

    target_ws = None
    current_d9_val = "ALL"
    current_d21_val = ""
    extracted_players = []

    try:
        creds = ottieni_credenziali()
        if creds:
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SHEET_ID)
            target_ws = next((ws for ws in sheet.worksheets() if str(ws.id).strip() == str(GID_PERSONAL_STATS).strip()), None)
            
            if target_ws:
                d9_raw = target_ws.acell("D9").value
                if d9_raw is not None and str(d9_raw).strip() != "":
                    current_d9_val = str(d9_raw).strip()
                
                d21_raw = target_ws.acell("D21").value
                if d21_raw is not None and str(d21_raw).strip() != "":
                    current_d21_val = str(d21_raw).strip()
                
                col_c_values = target_ws.get("C12:C60")
                for row in col_c_values:
                    if row and len(row) > 0:
                        p = str(row[0]).strip()
                        if p and p.lower() not in ["nan", "none", ""]:
                            extracted_players.append(p)
                extracted_players = list(dict.fromkeys(extracted_players))
    except Exception as e:
        st.warning(f"Error reading initial Personal Stats sheet: {e}")

    if not extracted_players:
        extracted_players = ["No players available"]

    default_round_label = "ALL"
    for k, v in rounds_config.items():
        if str(v).strip().lower() == str(current_d9_val).strip().lower():
            default_round_label = k
            break

    with col1:
        selected_round_label = st.selectbox(
            "Select Round", 
            list(rounds_config.keys()), 
            index=list(rounds_config.keys()).index(default_round_label) if default_round_label in rounds_config else 0,
            key="sb_round"
        )
        selected_d9_val = rounds_config[selected_round_label]
        
        if str(selected_d9_val).strip().lower() != str(current_d9_val).strip().lower():
            scrivi_cella_per_gid(GID_PERSONAL_STATS, "D9", selected_d9_val)
            time.sleep(0.4)

    with col2:
        player_index = 0
        if current_d21_val in extracted_players:
            player_index = extracted_players.index(current_d21_val)

        selected_d21_val = st.selectbox("Select Player", extracted_players, index=player_index, key="sb_player")
        
        if str(selected_d21_val).strip().lower() != str(current_d21_val).strip().lower():
            scrivi_cella_per_gid(GID_PERSONAL_STATS, "D21", selected_d21_val)
            time.sleep(0.4)

    with st.spinner("Updating data..."):
        time.sleep(0.2)

    st.markdown("---")

    def format_val(val, is_percentage=False, decimals=2):
        try:
            if val is None or str(val).strip() == "" or str(val).strip().lower() in ["nan", "none", "#n/a", "#valore!"]:
                return "0.00%" if is_percentage else "0"
            clean_val = str(val).replace("%", "").strip().replace(",", ".")
            num = float(clean_val)
            factor = 10 ** decimals
            truncated = int(num * factor) / factor
            if is_percentage:
                return f"{truncated:.{decimals}f}%"
            elif truncated.is_integer():
                return str(int(truncated))
            else:
                return f"{truncated:.{decimals}f}"
        except Exception:
            return str(val) if val is not None and str(val).strip() != "" else ("0.00%" if is_percentage else "0")

    summary_fired, summary_hit, summary_acc, summary_kill, summary_dmg, summary_mvp, summary_death = "0", "0", "0.00%", "0", "0", "0", "0"
    faster_banana_val = "-"
    deadliest_w, deadliest_d, deadliest_a = "-", "0", "0.00%"
    weapon_rows_data = []

    try:
        if target_ws:
            f15_l15 = target_ws.get("F15:L15")
            if f15_l15 and len(f15_l15) > 0:
                row_vals = f15_l15[0]
                summary_fired = format_val(row_vals[0] if len(row_vals) > 0 else 0)
                summary_hit = format_val(row_vals[1] if len(row_vals) > 1 else 0)
                summary_acc = format_val(row_vals[2] if len(row_vals) > 2 else 0, is_percentage=True)
                summary_kill = format_val(row_vals[3] if len(row_vals) > 3 else 0)
                summary_dmg = format_val(row_vals[4] if len(row_vals) > 4 else 0)
                summary_mvp = format_val(row_vals[5] if len(row_vals) > 5 else 0)
                summary_death = format_val(row_vals[6] if len(row_vals) > 6 else 0)

            j17_l17 = target_ws.get("J17:L17")
            if j17_l17 and len(j17_l17) > 0 and len(j17_l17[0]) > 0:
                faster_banana_val = format_val(j17_l17[0][0])

            h19_l20 = target_ws.get("H19:L20")
            if h19_l20 and len(h19_l20) > 0:
                raw_w = h19_l20[0][0] if len(h19_l20[0]) > 0 else "-"
                deadliest_w = str(raw_w).strip() if raw_w and str(raw_w).strip().lower() not in ["nan", "none", ""] else "-"
                
                if len(h19_l20) > 1:
                    deadliest_d = format_val(h19_l20[1][3] if len(h19_l20[1]) > 3 else 0)
                    deadliest_a = format_val(h19_l20[1][4] if len(h19_l20[1]) > 4 else 0, is_percentage=True)

            weapons_raw = target_ws.get("F27:L67")
            if weapons_raw:
                for r_data in weapons_raw:
                    if r_data and len(r_data) > 0:
                        w_name = str(r_data[0]).strip()
                        if w_name and w_name.upper() not in ["NAN", "NONE", ""]:
                            weapon_rows_data.append({
                                "WEAPON": w_name,
                                "TOT SHOTS": format_val(r_data[1] if len(r_data) > 1 else 0, is_percentage=False),
                                "SHOT HIT": format_val(r_data[2] if len(r_data) > 2 else 0, is_percentage=False),
                                "ACC%": format_val(r_data[3] if len(r_data) > 3 else 0, is_percentage=True),
                                "DMG": format_val(r_data[4] if len(r_data) > 4 else 0, is_percentage=False),
                                "HEADSHOT": format_val(r_data[5] if len(r_data) > 5 else 0, is_percentage=False),
                                "MAX DISTANCE": format_val(r_data[6] if len(r_data) > 6 else 0, is_percentage=False)
                            })
    except Exception as e:
        st.warning(f"Error reading dashboard data: {e}")

    st.markdown("<h4 style='color: #93c5fd; font-size: 1rem;'>MATCH SUMMARY</h4>", unsafe_allow_html=True)
    c_grid1, c_grid2, c_grid3 = st.columns(3)
    
    with c_grid1:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>FIRED</div><div class='stat-value'>{summary_fired}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>ACCURACY</div><div class='stat-value'>{summary_acc}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>DMG</div><div class='stat-value'>{summary_dmg}</div></div>", unsafe_allow_html=True)
    with c_grid2:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>SHOT HIT</div><div class='stat-value'>{summary_hit}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>KILL</div><div class='stat-value'>{summary_kill}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>MVP</div><div class='stat-value'>{summary_mvp}</div></div>", unsafe_allow_html=True)
    with c_grid3:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>DEATH</div><div class='stat-value'>{summary_death}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>FASTER BANANA</div><div class='stat-value'>{faster_banana_val}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h4 style='color: #93c5fd; font-size: 1rem;'>DEADLIEST WEAPON</h4>", unsafe_allow_html=True)
    dw_col1, dw_col2, dw_col3 = st.columns(3)
    with dw_col1:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>WEAPON</div><div class='stat-value' style='font-size: 0.85rem;'>{deadliest_w}</div></div>", unsafe_allow_html=True)
    with dw_col2:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>DMG</div><div class='stat-value'>{deadliest_d}</div></div>", unsafe_allow_html=True)
    with dw_col3:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>ACC%</div><div class='stat-value'>{deadliest_a}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h4 style='color: #93c5fd; text-align: center;'>WEAPON PERFORMANCE</h4>", unsafe_allow_html=True)
    
    if weapon_rows_data:
        df_weapons_final = pd.DataFrame(weapon_rows_data)
    else:
        df_weapons_final = pd.DataFrame(columns=["WEAPON", "TOT SHOTS", "SHOT HIT", "ACC%", "DMG", "HEADSHOT", "MAX DISTANCE"])

    st.dataframe(df_weapons_final, use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# --- SEZIONE: TOTAL POINT ---
# ==========================================
elif scelta_menu == "TOTAL POINT":
    st.markdown("<div style='background-color: #0e1117; border: 2px solid #262730; border-radius: 12px; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("### 📈 Total Point Summary")

    df_leaderboard_tp = get_df_by_gid(GID_LEADERBOARD)

    if df_leaderboard_tp is not None:
        try:
            # F33:F39 (Colonna F indice 5, righe 33-39 indice 32-39)
            teams_tp = df_leaderboard_tp.iloc[32:39, 5].fillna("").tolist()
            # G33:G39 (Colonna G indice 6)
            points_tp = df_leaderboard_tp.iloc[32:39, 6].fillna(0).tolist()
            # H33:H39 (Colonna H indice 7)
            rounds_tp = df_leaderboard_tp.iloc[32:39, 7].fillna(0).tolist()

            df_total_point = pd.DataFrame({
                "TEAM": teams_tp,
                "POINT": points_tp,
                "ROUNDS PLAYED": rounds_tp
            })

            st.dataframe(df_total_point, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error extracting Total Point data from cells F33:H39: {e}")
    else:
        st.error("Unable to connect to Leaderboard tab for Total Point.")

    st.markdown("</div>", unsafe_allow_html=True)
