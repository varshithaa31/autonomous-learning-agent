import streamlit as st
import re
from engine import learning_graph

def parse_mcqs(quiz_str):
    questions = []
    blocks = re.split(r'Q:', quiz_str)[1:] 
    for block in blocks:
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if len(lines) < 4: continue
        q_text = lines[0]
        options = [l for l in lines if l.startswith(('A)', 'B)', 'C)'))]
        ans_match = re.search(r'Answer:\s*([A-C])', block)
        if q_text and len(options) >= 3 and ans_match:
            questions.append({"question": q_text, "options": options, "answer": ans_match.group(1)})
    return questions

# 1. State Initialization
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None
if "history" not in st.session_state:
    st.session_state.history = []
if "show_decision" not in st.session_state:
    st.session_state.show_decision = False
if "finished" not in st.session_state:
    st.session_state.finished = False

st.set_page_config(page_title="AI Mastery Tutor", layout="wide")

# --- SIDEBAR: LEARNING PROGRESS ---
with st.sidebar:
    st.header("📈 Your Progress")
    if not st.session_state.history:
        st.write("No topics mastered yet.")
    for i, topic in enumerate(st.session_state.history):
        st.success(f"✅ {topic}")
    if st.session_state.history:
        st.divider()
        st.metric("Topics Completed", len(st.session_state.history))

# --- UI FLOWS ---
if st.session_state.finished:
    st.title("🎓 Journey Complete")
    st.balloons()
    st.success("Thank you for learning! You've successfully expanded your knowledge base.")
    if st.button("Start New Session"):
        st.session_state.clear()
        st.rerun()
    st.stop()

if st.session_state.agent_state is None:
    st.title("🧠 Master a New Topic")
    user_topic = st.text_input("What would you like to learn about?")
    if st.button("Begin Lesson"):
        if user_topic:
            with st.spinner("Preparing detailed lesson..."):
                st.session_state.agent_state = learning_graph.invoke({"topic": user_topic, "is_feynman": False})
                st.session_state.show_decision = False
                st.rerun()
    st.stop()

# --- ACTIVE LESSON ---
state = st.session_state.agent_state
st.title(f"Topic: {state['topic']}")
st.markdown(state["explanation"])

if state.get("is_feynman"):
    st.divider()
    st.warning("💡 **Feynman Simplification:**")
    st.markdown(state["feynman_text"])

st.divider()
st.subheader("📝 Practice Quiz")
quiz_data = parse_mcqs(state["questions"])

# If already passed, show results and next-step prompt
if st.session_state.show_decision:
    st.success(f"🎯 100% Mastery Achieved for {state['topic']}!")
    st.write("### Would you like to learn the next topic?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, keep going!"):
            st.session_state.history.append(state['topic'])
            st.session_state.agent_state = None
            st.session_state.show_decision = False
            st.rerun()
    with col2:
        if st.button("❌ No, I'm finished"):
            st.session_state.history.append(state['topic'])
            st.session_state.finished = True
            st.rerun()
else:
    # Show Quiz Form
    if quiz_data:
        with st.form(key=f"quiz_{state['topic']}"):
            user_responses = []
            for i, q in enumerate(quiz_data):
                st.write(f"**Q{i+1}: {q['question']}**")
                choice = st.radio("Select:", q['options'], key=f"q_{i}", label_visibility="collapsed")
                user_responses.append(choice[0])
            
            if st.form_submit_button("Submit Answers"):
                correct = sum(1 for i, q in enumerate(quiz_data) if user_responses[i] == q['answer'])
                score = int((correct / len(quiz_data)) * 100)
                
                if score >= 75:
                    st.session_state.show_decision = True
                    st.rerun()
                else:
                    st.error(f"Score: {score}%. Let's try the Feynman Loop...")
                    st.session_state.agent_state = learning_graph.invoke({**state, "is_feynman": True})
                    st.rerun()