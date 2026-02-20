import streamlit as st
import json
import os
from datetime import datetime
from engine import learning_graph

# --- PERSISTENCE HELPERS ---
DB_FILE = "users_db.json"

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

st.set_page_config(page_title="Mastery Portal", layout="wide")

# --- CSS STYLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #1e40af 100%) !important; 
        color: #f1f5f9 !important; font-family: 'Inter', sans-serif !important; 
    }
    .main-header { 
        background: linear-gradient(135deg, #ffffff 0%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 4rem !important; font-weight: 800; text-align: center; margin-bottom: 40px;
    }
    .content-box { 
        background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(12px);
        padding: 45px; border-radius: 28px; border: 1px solid rgba(56, 189, 248, 0.2);
        line-height: 1.9; font-size: 1.3rem !important; border-left: 8px solid #38bdf8;
    }
    .stButton>button { 
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%) !important;
        color: white !important; border-radius: 14px; font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

def draw_sidebar():
    with st.sidebar:
        st.markdown(f"<h1 style='color:#38bdf8;'>👤 {st.session_state.get('user', 'User')}</h1>", unsafe_allow_html=True)
        
        if st.button("📊 VIEW HISTORY", use_container_width=True):
            st.session_state.view = "History"; st.rerun()
            
        # --- KNOWLEDGE VAULT SECTION ---
        st.markdown("---")
        st.markdown("<p style='color:#94a3b8; font-weight:600; font-size:0.9rem; letter-spacing:1px;'>KNOWLEDGE VAULT</p>", unsafe_allow_html=True)
        
        if not st.session_state.get('history'):
            st.info("No mastered topics yet.")
        else:
            for item in st.session_state.history:
                st.markdown(f"""
                    <div class="vault-card">
                        <div style="font-weight:600; font-size:1rem;">{item['topic']}</div>
                        <div style="color:#38bdf8; font-size:0.8rem;">Attempts: {item['attempts']}</div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("---")
        # -------------------------------
        
        if st.button("Logout", use_container_width=True): 
            st.session_state.view = "Auth"; st.rerun()

# --- INITIALIZE SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "view" not in st.session_state: st.session_state.view = "Auth"
if "agent_data" not in st.session_state: st.session_state.agent_data = None

# --- VIEWS ---
if st.session_state.view == "Auth":
    st.markdown("<h1 class='main-header'>Mastery AI</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        db = load_users()
        if email in db and st.button("SIGN IN", use_container_width=True):
            if pwd == db[email]['p']:
                st.session_state.update({"user": db[email]['u'], "email": email, "history": db[email].get('h', []), "view": "Dashboard"})
                st.rerun()
        elif email and st.button("CREATE ACCOUNT", use_container_width=True):
            u = st.text_input("Username")
            db[email] = {'u': u, 'p': pwd, 'h': []}
            save_db(db)
            st.session_state.update({"user": u, "email": email, "history": [], "view": "Dashboard"})
            st.rerun()

elif st.session_state.view == "Dashboard":
    draw_sidebar()
    topic = st.text_input("What shall we master today?")
    if st.button("START"):
        with st.spinner("Thinking..."):
            res = learning_graph.invoke({"topic": topic, "attempt_count": 1})
            st.session_state.update({"topic": topic, "agent_data": res, "view": "Explanation"})
            st.rerun()

elif st.session_state.view == "Explanation":
    draw_sidebar()
    data = st.session_state.agent_data
    if data and "explanation" in data:
        st.markdown(f"<div class='content-box'>{data['explanation']}</div>", unsafe_allow_html=True)
        if st.button("QUIZ ME"): st.session_state.view = "Quiz"; st.rerun()
    else:
        st.error("Session expired.")
        if st.button("Home"): st.session_state.view = "Dashboard"; st.rerun()

# ... (Include Quiz, Result, and Feynman views following the same 'if data' pattern)