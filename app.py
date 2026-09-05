import subprocess
import sys
import streamlit as st
from src.copilot import answer_question

st.set_page_config(
    page_title="NexusMart Retail Copilot",
    page_icon="🛒",
    layout="wide",
)

st.title("🛒 NexusMart Retail Sales & Inventory Copilot")
st.caption("Ask questions about inventory, sales, and product performance.")

user_question = st.text_input(
    "Ask the retail copilot:",
    placeholder="e.g. Which products currently need inventory attention?"
)

if st.button("Ask Copilot"):
    if user_question.strip():
        with st.spinner("Analyzing..."):
            answer = answer_question(user_question)
        st.write(answer)
    else:
        st.warning("Please enter a question.")


if __name__ == "__main__":
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port=8000",
        "--server.address=localhost",
    ])