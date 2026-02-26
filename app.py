import streamlit as st
import requests

# --- SETUP ---
ZYLA_KEY = st.secrets["ZYLA_API_KEY"] # Store this in Streamlit's "Secrets" settings
BASE_URL = "https://zylalabs.com/api/1813/virtual+phone+number+generator+api"
HEADERS = {"Authorization": f"Bearer {ZYLA_KEY}"}

st.title("📲 Virtual Number & OTP Manager")

# 1. Select Country
st.subheader("Step 1: Get a Number")
country_id = st.selectbox("Select Country Code", ["1", "44", "49", "91"], help="1=USA, 44=UK, 49=Germany, 91=India")

if st.button("Generate New Number"):
    res = requests.get(f"{BASE_URL}/1467/get+number+by+country+id?countryCode={country_id}", headers=HEADERS).json()
    if res['success']:
        st.session_state.current_number = res['data'][0]
        st.success(f"Your Number: +{st.session_state.current_number}")
    else:
        st.error("Could not fetch number. Check API balance.")

# 2. Check SMS
if 'current_number' in st.session_state:
    st.divider()
    st.subheader(f"Step 2: Check SMS for +{st.session_state.current_number}")
    
    if st.button("📩 Refresh SMS History"):
        sms_res = requests.get(f"{BASE_URL}/1469/check+sms+history?countryCode={country_id}&phoneNumber={st.session_state.current_number}", headers=HEADERS).json()
        
        if sms_res['success'] and sms_res['data']:
            for msg in sms_res['data'][:5]: # Show last 5 messages
                with st.chat_message("user"):
                    st.write(f"**From:** {msg['from']}")
                    st.code(msg['text'], language="text")
                    st.caption(f"Received: {msg['createdAt']}")
        else:
            st.info("No messages found yet. Keep waiting...")
