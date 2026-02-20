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

# --- CSS ENHANCEMENTS: RADIANT BLUE GRADIENT THEME ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #1e40af 100%) !important; 
        color: #f1f5f9 !important; 
        font-family: 'Inter', sans-serif !important; 
    }
    
    .main-header { 
        background: linear-gradient(135deg, #ffffff 0%, #38bdf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 4rem !important; font-weight: 800; text-align: center; margin-bottom: 40px;
        letter-spacing: -2px;
        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.3));
    }
    
    p, li, label, div { font-size: 1.2rem !important; color: #f1f5f9 !important; }
    
    .content-box { 
        background: rgba(15, 23, 42, 0.6); 
        backdrop-filter: blur(12px);
        padding: 45px; border-radius: 28px; 
        border: 1px solid rgba(56, 189, 248, 0.2); line-height: 1.9;
        font-size: 1.3rem !important; color: #f1f5f9; border-left: 8px solid #38bdf8;
    }
    
    .feedback-card { padding: 25px; border-radius: 18px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); }
    .correct-card { background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; }
    .wrong-card { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; }
    
    .stButton>button { 
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 14px; 
        font-weight: 800; 
        padding: 0.8rem 2rem; 
        font-size: 1.1rem !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #38bdf8 0%, #3b82f6 100%) !important;
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0px 12px 30px rgba(56, 189, 248, 0.4);
        border-color: #ffffff !important;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

def draw_sidebar():
    with st.sidebar:
        st.markdown(f"<h1 style='color:#38bdf8; font-size: 2.8rem; margin-bottom: 0;'>👤 {st.session_state.get('user', 'User')}</h1>", unsafe_allow_html=True)
        st.divider()
        if st.button("📊 VIEW LEARNING HISTORY", use_container_width=True):
            st.session_state.view = "History"; st.rerun()
        st.divider()
        if st.button("Logout", use_container_width=True): 
            st.session_state.view = "Auth"; st.session_state.user = None; st.session_state.email = None; st.rerun()

# --- INITIALIZE SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "view" not in st.session_state: st.session_state.view = "Auth"
if "attempt" not in st.session_state: st.session_state.attempt = 1
if "agent_data" not in st.session_state: st.session_state.agent_data = None

# --- AUTH ---
if st.session_state.view == "Auth":
    st.markdown("<h1 class='main-header'>Mastery AI Learning Agent</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        auth_email = st.text_input("Email")
        auth_pwd = st.text_input("Password", type="password")
        db = load_users()
        if auth_email in db:
            st.info(f"Welcome back, {db[auth_email]['u']}!")
            if st.button("SIGN IN", use_container_width=True):
                if auth_pwd == db[auth_email]['p']:
                    st.session_state.update({"user": db[auth_email]['u'], "email": auth_email, "history": db[auth_email].get('h', []), "view": "Dashboard"})
                    st.rerun()
                else: st.error("Invalid password.")
        elif auth_email:
            st.warning("No account found. Enter a username to register.")
            auth_user = st.text_input("New Username")
            if st.button("CREATE ACCOUNT & ENTER", use_container_width=True):
                if auth_user and auth_pwd:
                    db[auth_email] = {'u': auth_user, 'p': auth_pwd, 'h': []}
                    save_db(db)
                    st.session_state.update({"user": auth_user, "email": auth_email, "history": [], "view": "Dashboard"})
                    st.rerun()

# --- DASHBOARD ---
elif st.session_state.view == "Dashboard":
    draw_sidebar()
    st.markdown(f"<h1 class='main-header'>Welcome, {st.session_state.user}</h1>", unsafe_allow_html=True)
    topic = st.text_input("What complex topic shall we master today?")
    if st.button("START LEARNING", use_container_width=True):
        if topic:
            with st.spinner("Generating Info..."):
                res = learning_graph.invoke({"topic": topic, "attempt_count": 1})
                st.session_state.update({"topic": topic, "agent_data": res, "view": "Explanation", "attempt": 1})
                st.rerun()
        else:
            st.error("Please enter a topic!")

# --- HISTORY ---
elif st.session_state.view == "History":
    draw_sidebar()
    st.markdown("<h1 class='main-header'>Mastery Log</h1>", unsafe_allow_html=True)
    if st.session_state.history:
        display_data = [{"S.No": i+1, "Topic Mastered": it['topic'], "Session": it['session'], "Attempts": it['attempts'], "Score": it['score']} for i, it in enumerate(st.session_state.history)]
        st.table(display_data)
    else: st.info("No learning history found.")
    if st.button("Back to Dashboard"): st.session_state.view = "Dashboard"; st.rerun()

# --- EXPLANATION ---
elif st.session_state.view == "Explanation":
    draw_sidebar()
    if st.session_state.agent_data:
        st.markdown(f"<h2 style='text-align:center; color:#38bdf8;'>{st.session_state.topic}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='content-box'>{st.session_state.agent_data.get('explanation', 'No explanation available.')}</div>", unsafe_allow_html=True)
        if st.button("PROCEED TO ASSESSMENT", use_container_width=True): 
            st.session_state.view = "Quiz"; st.rerun()
    else:
        st.error("Session data missing. Returning to Dashboard...")
        st.session_state.view = "Dashboard"; st.rerun()

# --- QUIZ ---
elif st.session_state.view == "Quiz":
    draw_sidebar()
    if st.session_state.agent_data:
        quiz = st.session_state.agent_data.get('quiz_data', [])
        st.markdown(f"<h1 class='main-header'>Assessment ({st.session_state.attempt})</h1>", unsafe_allow_html=True)
        with st.form("quiz_form"):
            for i, q in enumerate(quiz):
                st.markdown(f"<h3 style='color:#38bdf8;'>Question {i+1}</h3>", unsafe_allow_html=True)
                st.write(q['q'])
                st.radio("Options:", q['opts'], key=f"q_{i}", label_visibility="collapsed")
                st.divider()
            if st.form_submit_button("SUBMIT ASSESSMENT", use_container_width=True):
                u_ans = [st.session_state[f"q_{i}"] for i in range(len(quiz))]
                correct = sum(1 for i, q in enumerate(quiz) if u_ans[i][0] == q['a'])
                st.session_state.update({"score": (correct/len(quiz))*100, "user_ans": u_ans, "view": "Result"})
                st.rerun()
    else:
        st.session_state.view = "Dashboard"; st.rerun()

# --- RESULT ---
elif st.session_state.view == "Result":
    draw_sidebar()
    if st.session_state.agent_data:
        score, quiz, u_ans = st.session_state.score, st.session_state.agent_data['quiz_data'], st.session_state.user_ans
        current_time = datetime.now().strftime("%Y-%m-%d, %H:%M")
        if score >= 70: st.success(f"Score: {score}% — Congratulations! You've mastered this topic.")
        else: st.error(f"Current Score: {score}% — Let's reinforce the concept with a Feynman analogy.")
        
        for i, q in enumerate(quiz):
            status_class = "correct-card" if u_ans[i][0] == q['a'] else "wrong-card"
            st.markdown(f"<div class='feedback-card {status_class}'><b>{i+1}. {q['q']}</b><br>Your Answer: {u_ans[i]}<br>Correct: {q['a']}<br><i>{q['exp']}</i></div>", unsafe_allow_html=True)
        
        if score >= 70:
            if not any(it['topic'] == st.session_state.topic for it in st.session_state.history):
                st.session_state.history.append({"topic": st.session_state.topic, "score": f"{score}%", "attempts": st.session_state.attempt, "session": current_time})
                db = load_users(); db[st.session_state.email]['h'] = st.session_state.history; save_db(db)
            
            col1, col2 = st.columns(2)
            if col1.button("NEW TOPIC", use_container_width=True): 
                st.session_state.view = "Dashboard"; st.rerun()
            if col2.button("END LEARNING SESSION", use_container_width=True): 
                st.session_state.view = "End"; st.rerun()
        else:
            if st.button("FEYNMAN EXPLANATION", use_container_width=True): 
                st.session_state.view = "Feynman"; st.rerun()
    else:
        st.session_state.view = "Dashboard"; st.rerun()

# --- FEYNMAN ---
elif st.session_state.view == "Feynman":
    draw_sidebar()
    if st.session_state.agent_data:
        st.markdown("<h1 class='main-header'>Feynman Analogy</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='content-box'>{st.session_state.agent_data.get('feynman_text', 'Analogy not found.')}</div>", unsafe_allow_html=True)
        if st.button("RETRY ASSESSMENT", use_container_width=True):
            st.session_state.attempt += 1
            with st.spinner("Preparing retry..."):
                res = learning_graph.invoke({"topic": st.session_state.topic, "attempt_count": st.session_state.attempt})
                st.session_state.agent_data = res; st.session_state.view = "Quiz"; st.rerun()
    else:
        st.session_state.view = "Dashboard"; st.rerun()

# --- END VIEW ---
elif st.session_state.view == "End":
    draw_sidebar()
    st.markdown("<h1 class='main-header'>Session Complete</h1>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='content-box' style='text-align: center;'>
            <h2 style='color:#38bdf8;'>Great Work Today, {st.session_state.user}! ✨</h2>
            <p style='margin-top: 20px;'>
                "Education is the most powerful weapon which you can use to change the world."
            </p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("START NEW SESSION", use_container_width=True):
        st.session_state.view = "Dashboard"; st.rerun()