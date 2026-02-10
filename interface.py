import streamlit as st
import re
from engine import learning_graph

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="AI Learning Agent", page_icon="🧠", layout="wide")

if "history" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "history": [], "total_subs": 0,
        "agent_state": None, "mode": "Academic", "view": "Content",
        "current_attempts": 0, "last_score": 0
    })

def parse_mcqs(quiz_str):
    questions = []
    blocks = re.split(r'Q:', quiz_str)[1:]
    for block in blocks:
        lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
        ans_match = re.search(r'Answer:\s*([A-C])', block)
        if len(lines) >= 4 and ans_match:
            questions.append({"q": lines[0], "opts": [l for l in lines if l[1:3] == ') '], "a": ans_match.group(1)})
    return questions

# --- 2. LOGIN PAGE (Empty Fields) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🧠 AI Learning Agent</h1>", unsafe_allow_html=True)
    with st.columns([1, 1.5, 1])[1]:
        st.subheader("Login")
        email = st.text_input("Email", value="", placeholder="Enter email")
        pw = st.text_input("Password", type="password", value="")
        if st.button("Login", use_container_width=True, type="primary"):
            if email and pw:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Credentials required.")
    st.stop()

# --- 3. SIDEBAR (Mastery Stats) ---
with st.sidebar:
    st.markdown("### 📊 Mastery Stats")
    mastered_count = len(st.session_state.history)
    eff = (mastered_count / st.session_state.total_subs * 100) if st.session_state.total_subs > 0 else 0.0
    st.metric("Efficiency Rate", f"{eff:.1f}%")
    st.metric("Topics Mastered", mastered_count)
    st.divider()
    st.markdown("### 📁 Knowledge Vault")
    for item in st.session_state.history:
        with st.container(border=True):
            st.markdown(f"**{item['topic']}**")
            st.caption(f"{item['attempts']} attempt(s)") #
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- 4. NAVIGATION LOGIC ---

# PROFESSIONAL END SESSION VIEW
if st.session_state.view == "EndSession":
    st.title("🏁 Learning Session Concluded")
    st.success("### Professional Summary: Mastery Achieved")
    st.write("You have successfully completed your learning modules for today. All progress has been logged in your Knowledge Vault.")
    st.info("Continuous learning is the key to expertise. Great job staying focused!")
    if st.button("Start New Learning Session", type="primary"):
        st.session_state.update({"agent_state": None, "view": "Content", "mode": "Academic", "history": [], "total_subs": 0})
        st.rerun()
    st.stop()

# TOPIC INPUT (Loading: Generating explanation...)
if st.session_state.agent_state is None:
    st.title("🧠 Master a New Topic")
    topic = st.text_input("Enter topic:", placeholder="e.g., Photosynthesis")
    if st.button("Start Learning", type="primary"):
        with st.spinner("Generating explanation..."):
            st.session_state.agent_state = learning_graph.invoke({"topic": topic})
            st.session_state.current_attempts = 0
            st.session_state.view = "Content"
            st.rerun()
    st.stop()

state = st.session_state.agent_state

# QUIZ PAGE (Displaying Attempt Number)
if st.session_state.view == "Quiz":
    st.markdown(f"### 📝 Assessment: {state['topic']}")
    st.info(f"**Attempt Number: {st.session_state.current_attempts + 1}**")
    
    q_list = parse_mcqs(state["questions"])
    with st.form("quiz_page"):
        user_ans = []
        for i, q in enumerate(q_list[:5]):
            st.markdown(f"**Q{i+1}: {q['q']}**")
            user_ans.append(st.radio("Select Answer:", q['opts'], key=f"q{i}", label_visibility="collapsed")[0])
        if st.form_submit_button("Submit Assessment", use_container_width=True):
            st.session_state.total_subs += 1
            st.session_state.current_attempts += 1
            score = sum(1 for i, q in enumerate(q_list[:5]) if user_ans[i] == q['a']) / 5
            st.session_state.last_score = int(score * 100)
            if score >= 0.75:
                st.session_state.history.append({"topic": state["topic"], "attempts": st.session_state.current_attempts})
                st.session_state.view = "PostQuizSuccess"
            else:
                st.session_state.view = "PostQuizFail"
            st.rerun()
    st.stop()

# SUCCESS SCREEN (Next Steps Options)
if st.session_state.view == "PostQuizSuccess":
    st.success(f"### 🎊 Mastery Achieved! \nScore: **{st.session_state.last_score}%**")
    c1, c2 = st.columns(2)
    if c1.button("Learn Next Topic", use_container_width=True, type="primary"):
        st.session_state.agent_state = None
        st.session_state.view = "Content"
        st.rerun()
    if c2.button("End Learning Session", use_container_width=True):
        st.session_state.view = "EndSession"
        st.rerun()
    st.stop()

# FAILURE SCREEN (Encouraging Message)
if st.session_state.view == "PostQuizFail":
    st.error(f"### ⚠️ Assessment Failed \nScore: **{st.session_state.last_score}%**")
    st.markdown("##### It's okay, let's learn simpler using Feynman explanation")
    if st.button("Proceed to Detailed Analogy", use_container_width=True):
        st.session_state.mode = "Feynman"
        st.session_state.view = "Content"
        st.rerun()
    st.stop()

# MAIN CONTENT VIEW
st.title(f"Focus: {state['topic']}")
st.subheader("💡 Feynman Analogy" if st.session_state.mode == "Feynman" else "📖 Academic Breakdown")
st.write(state["feynman_text"] if st.session_state.mode == "Feynman" else state["explanation"])

if st.button("Attempt Quiz" if st.session_state.mode == "Academic" else "Re-Attempt Quiz", use_container_width=True, type="primary"):
    with st.spinner("Preparing quiz..."):
        st.session_state.agent_state = learning_graph.invoke({"topic": state["topic"]})
        st.session_state.view = "Quiz"
        st.rerun()