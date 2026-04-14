import streamlit as st
import pandas as pd
import time
from services.ave_api_client import AveApiClient
from services.alert_manager import AlertManager

# Set Page Config (Collapsed sidebar to mimic a full web app)
st.set_page_config(page_title="AveScope Alerts", layout="wide", page_icon="🔭", initial_sidebar_state="collapsed")

# ----------------- CUSTOM CSS: NAVY BLUE & COINGECKO THEME -----------------
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0a1428; /* Deep Navy Blue */
        color: #ffffff;
    }
    
    /* Hide default Streamlit header */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    
    /* Top Nav Styling */
    .top-nav {
         background-color: #111f38; /* Slightly lighter navy */
         padding: 15px 30px;
         display: flex;
         justify-content: space-between;
         align-items: center;
         border-bottom: 1px solid #1e3050;
         margin-top: -60px; /* pull up to replace streamlit header */
         margin-bottom: 20px;
    }
    .nav-logo {
         font-size: 24px;
         font-weight: 800;
         color: #8cc63f; /* CoinGecko Green Accent */
         display: flex;
         align-items: center;
         gap: 10px;
    }
    .nav-user {
         font-size: 14px;
         color: #ffffff;
         background-color: #1e3050;
         padding: 8px 16px;
         border-radius: 20px;
         font-weight: bold;
    }
    .nav-button {
         background-color: #8cc63f;
         color: #0a1428;
         border: none;
         padding: 8px 16px;
         border-radius: 6px;
         font-weight: bold;
         cursor: pointer;
    }
    
    /* Cards and Containers */
    div[data-testid="stExpander"] {
        background-color: #111f38;
        border: 1px solid #1e3050;
        border-radius: 8px;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "tracked_tokens" not in st.session_state:
    st.session_state.tracked_tokens = [
        {"symbol": "WBTC", "contract": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "network": "ethereum"},
        {"symbol": "WETH", "contract": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "network": "ethereum"},
        {"symbol": "SOL", "contract": "So11111111111111111111111111111111111111112", "network": "solana"}
    ]
if "alerts_config" not in st.session_state:
    st.session_state.alerts_config = []
if "notification_logs" not in st.session_state:
    st.session_state.notification_logs = []
if "username" not in st.session_state:
    st.session_state.username = None
if "ave_api_key" not in st.session_state:
    st.session_state.ave_api_key = None

# Instantiate Services
ave_client = AveApiClient(api_key=st.session_state.get("ave_api_key"))
alert_manager = AlertManager()

# ----------------- TOP NAVBAR MOCKUP -----------------
nav_html = f"""
<div class="top-nav">
    <div class="nav-logo">🔭 AveScope</div>
    <div>
        {f'<span class="nav-user">👤 {st.session_state.username}</span>' if st.session_state.username else '<span class="nav-user">Not Logged In</span>'}
    </div>
</div>
"""
st.markdown(nav_html, unsafe_allow_html=True)

# ----------------- AUTHENTICATION FLOW -----------------
if not st.session_state.username:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### Create Account / Login")
        temp_user = st.text_input("Username", placeholder="e.g., DegenKing99")
        temp_ave = st.text_input("Ave.ai API Key", type="password", placeholder="Paste your API key here to fetch live accurate prices")
        if st.button("Log In / Create Account", use_container_width=True):
            if temp_user:
                st.session_state.username = temp_user
                st.session_state.ave_api_key = temp_ave if temp_ave else None
                st.rerun()
    st.stop() # Wait for login

# ----------------- MAIN DASHBOARD -----------------
st.title("Cryptocurrency Prices & AI Alerts")
st.markdown("Monitor the market and set smart conditions with generative AI summaries.")

# Control Panel
col1, col2 = st.columns(2)

with col1:
    with st.expander("➕ Track New Coin"):
        symbol = st.text_input("Symbol (e.g., PEPE)")
        contract = st.text_input("Contract Address / ID")
        network = st.selectbox("Network", ["solana", "bsc", "ethereum", "arbitrum"])
        if st.button("Add to Portfolio"):
            if symbol and contract:
                st.session_state.tracked_tokens.append({
                    "symbol": symbol.upper(),
                    "contract": contract,
                    "network": network
                })
                st.success(f"Added {symbol} to monitoring list!")

with col2:
    with st.expander("🔔 Create Target Alert"):
        if len(st.session_state.tracked_tokens) > 0:
            alert_symbol = st.selectbox("Select Token", [t['symbol'] for t in st.session_state.tracked_tokens])
            metric = st.selectbox("Metric", ["price", "market_cap", "volume_24h"])
            condition = st.selectbox("Condition", ["above", "below"])
            threshold = st.number_input("Threshold Value", min_value=0.0, format="%.6f")
            
            if st.button("Set Alert Rule"):
                st.session_state.alerts_config.append({
                    "symbol": alert_symbol,
                    "metric": metric,
                    "condition": condition,
                    "value": threshold
                })
                st.success(f"Tracking {alert_symbol} {metric} {condition} {threshold}!")
        else:
            st.info("Add a tracked token first.")

st.markdown("---")

# 1. Fetch live data
live_data = {}
tokens_display = []

for idx, token in enumerate(st.session_state.tracked_tokens):
    data = ave_client.get_token_price_and_volume(token['contract'], token['network'])
    live_data[token['symbol']] = data
    
    tokens_display.append({
        "#": idx + 1,
        "Coin": token['symbol'],
        "Price": f"${data.get('price', 0):.4f}",
        "24h Volume": f"${data.get('volume_24h', 0):,.0f}",
        "Market Cap": f"${data.get('market_cap', 0):,.0f}",
        "Network": token['network'].capitalize()
    })
    
st.subheader("Today's Cryptocurrency Prices")
if tokens_display:
    df = pd.DataFrame(tokens_display)
    # Removing the index to look cleaner
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Your portfolio is empty. Add a coin above.")

st.markdown("<br><br>", unsafe_allow_html=True)

# 2. Check Alerts & Render
triggered = alert_manager.check_alerts(st.session_state.alerts_config, live_data)
for msg in triggered:
    st.session_state.notification_logs.insert(0, msg)
    
log_col, rules_col = st.columns([2, 1])

with log_col:
    st.subheader("🚨 AI Vibe Trigger Logs")
    if st.session_state.notification_logs:
        for log in st.session_state.notification_logs[:5]: 
            st.info(log)
    else:
        st.write("Quiet in the markets... No alerts triggered yet.")

with rules_col:
    st.subheader("Active Rules")
    if st.session_state.alerts_config:
        rules_df = pd.DataFrame(st.session_state.alerts_config)
        st.dataframe(rules_df, use_container_width=True, hide_index=True)
    else:
        st.write("No active rules.")

# Auto-refresh loop
time.sleep(5)
st.rerun()
