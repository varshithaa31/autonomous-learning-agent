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
        if st.button("📊 VIEW LEARNING HISTORY", use_container_width=True):
            st.session_state.view = "History"; st.rerun()
        if st.button("Logout", use_container_width=True): 
            st.session_state.view = "Auth"; st.rerun()

# --- INITIALIZE SESSION STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "view" not in st.session_state: st.session_state.view = "Auth"
if "agent_data" not in st.session_state: st.session_state.agent_data = None

# --- VIEWS ---
if st.session_state.view == "Auth":
    st.markdown("<h1 class='main-header'>Mastery AI Learning Agent</h1>", unsafe_allow_html=True)
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
    if st.button("START LEARNING JOURNEY"):
        with st.spinner("Generating Info..."):
            res = learning_graph.invoke({"topic": topic, "attempt_count": 1})
            st.session_state.update({"topic": topic, "agent_data": res, "view": "Explanation"})
            st.rerun()

elif st.session_state.view == "Explanation":
    draw_sidebar()
    # SAFE ACCESS CHECK
    data = st.session_state.agent_data
    if data and "explanation" in data:
        st.markdown(f"<div class='content-box'>{data['explanation']}</div>", unsafe_allow_html=True)
        if st.button("QUIZ ME"): st.session_state.view = "Quiz"; st.rerun()
    else:
        st.error("Session expired.")
        if st.button("Home"): st.session_state.view = "Dashboard"; st.rerun()

# ... (Include Quiz, Result, and Feynman views following the same 'if data' pattern)

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