import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import exp

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(layout="wide", page_title="AURASTATS")

# =================================================
# DARK THEME + RED SPIDER
# =================================================
st.markdown("""
<style>
.stApp {
    background-color:#0b0b0b;
    color:white;
}
.stApp::before{
    content:"🕷️";
    position:fixed;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    font-size:500px;
    color:#ff0000;
    opacity:0.15;
    pointer-events:none;
}
h1,h2,h3{color:#ff3b3b;}
[data-testid="stMetricValue"]{
    color:#00ff99;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🕷️ AURASTATS – Gamer Performance Intelligence")

# =================================================
# LOAD FILE
# =================================================
file = st.file_uploader("Upload Gamer CSV", type=["csv"])
if not file:
    st.stop()

df = pd.read_csv(file)
df.columns = df.columns.str.lower()

# =================================================
# COLUMN NORMALIZATION
# =================================================
rename_map = {
    "name":"player_name",
    "player":"player_name",
    "matches":"matches_played",
    "kills":"eliminations",
    "damage_dealt":"damage",
    "totaldamage":"damage"
}
df.rename(columns=rename_map, inplace=True)

# =================================================
# SAFE DEFAULTS
# =================================================
for c in ["damage","wins","assists","revives","headshots"]:
    if c not in df:
        df[c] = 0

# =================================================
# GROUPED PLAYER STATS (⭐ FIX FOR KD BUG)
# =================================================
player_stats = (
    df.groupby("player_name")
    .agg({
        "matches_played":"sum",
        "eliminations":"sum",
        "deaths":"sum",
        "damage":"sum",
        "wins":"sum"
    })
    .reset_index()
)

player_stats["kd"] = player_stats["eliminations"] / (player_stats["deaths"] + 1)

# =================================================
# SIDEBAR
# =================================================
players = ["All Players"] + list(player_stats["player_name"])
selected = st.sidebar.selectbox("Select Player", players)

df_f = player_stats if selected=="All Players" else player_stats[player_stats["player_name"]==selected]

# =================================================
# HIST FUNCTION
# =================================================
def make_hist(data,title,color,col):
    fig,ax = plt.subplots(figsize=(4,3))
    ax.hist(data,bins=15,color=color,edgecolor="white")
    ax.set_title(title,color="white")
    ax.set_facecolor("#121212")
    fig.patch.set_facecolor("#121212")
    ax.tick_params(colors="white")
    col.pyplot(fig)

# =================================================
# PERFORMANCE LABEL
# =================================================
def performance_label(kd):
    if kd < 2:
        return "🐣 NOOB (Low Performer)"
    elif kd < 4:
        return "⚔ PRO (Good Performer)"
    else:
        return "👑 LEGEND (High Performer)"

# =================================================
# TABS
# =================================================
tab1,tab2,tab3,tab4,tab5 = st.tabs([
"📊 Dashboard",
"🏆 Leaderboard",
"⚔ Compare Players",
"🎯 Win Predictor",
"🧠 Performance Analyzer"
])

# =================================================
# DASHBOARD
# =================================================
with tab1:

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Players",len(df_f))
    c2.metric("Avg KD",round(df_f["kd"].mean(),2))
    c3.metric("Avg Kills",round(df_f["eliminations"].mean(),1))
    c4.metric("Avg Damage",round(df_f["damage"].mean(),1))

    col1,col2,col3 = st.columns(3)

    make_hist(df_f["eliminations"],"Kills","#ff3b3b",col1)
    make_hist(df_f["kd"],"KD","#00cfff",col2)
    make_hist(df_f["matches_played"],"Matches","#ff9f1c",col3)

    st.dataframe(df_f,use_container_width=True)

# =================================================
# LEADERBOARD
# =================================================
with tab2:
    rank = player_stats.copy()
    rank["score"] = rank["kd"]*50 + rank["damage"]*0.01 + rank["eliminations"]
    st.dataframe(rank.sort_values("score",ascending=False).head(20))

# =================================================
# COMPARE PLAYERS (⭐ FIXED KD HERE)
# =================================================
with tab3:

    p1 = st.selectbox("Player 1", player_stats["player_name"])
    p2 = st.selectbox("Player 2", player_stats["player_name"], index=1)

    d1 = player_stats[player_stats["player_name"]==p1].iloc[0]
    d2 = player_stats[player_stats["player_name"]==p2].iloc[0]

    labels = ["Kills","KD","Damage"]
    v1 = [d1["eliminations"], d1["kd"], d1["damage"]]
    v2 = [d2["eliminations"], d2["kd"], d2["damage"]]

    fig,ax = plt.subplots(figsize=(5,3))
    x = np.arange(len(labels))

    ax.bar(x-0.2,v1,0.4,label=p1,color="#00ff99")
    ax.bar(x+0.2,v2,0.4,label=p2,color="#ff3b3b")

    ax.set_xticks(x)
    ax.set_xticklabels(labels,color="white")
    ax.set_facecolor("#121212")
    fig.patch.set_facecolor("#121212")
    ax.legend()

    st.pyplot(fig)

# =================================================
# WIN PREDICTOR
# =================================================
with tab4:

    kills = st.number_input("Kills",0.0)
    damage = st.number_input("Damage",0.0)
    kd = st.number_input("KD",0.0)

    if st.button("Predict"):
        score = 0.4*kd + 0.0002*damage + 0.02*kills
        prob = (1/(1+exp(-score)))*100
        st.metric("Win Probability",f"{prob:.1f}%")

# =================================================
# PERFORMANCE ANALYZER
# =================================================
with tab5:

    player = st.selectbox("Select Player", player_stats["player_name"])

    row = player_stats[player_stats["player_name"]==player].iloc[0]

    label = performance_label(row["kd"])

    st.metric("KD",round(row["kd"],2))
    st.metric("Total Kills",row["eliminations"])
    st.metric("Total Damage",row["damage"])

    st.success(label)
