import streamlit as st
import sys


sys.path.append('.')
sys.path.append('..')

from src.judges_score_backend import JudgeScoresBackend
from ui.utils import to_markdown_table



def main():
    st.set_page_config(layout="wide")
    st.write("Reflections judges_platform\n")
    if "backend" not in st.session_state:
        st.session_state["backend"] = JudgeScoresBackend()  # cache backend in streamlit cache

    with st.form('form_reflections_results'):
        judge_secret = st.text_input('Secret passcode', 'e.g., yummy')
        judge_name= st.text_input('Judge name', 'e.g., Marie')
        submitted = st.form_submit_button("Generate dashboard")
        if submitted:
            st.write(f"\n{'*'*80}\n\nAssignments for {judge_name}")
            if judge_secret == "dummy":
                results = st.session_state["backend"].lookup_judge_scores(judge_name=judge_name)
                st.write(to_markdown_table(st.session_state["backend"].to_pretty_table(entries=results)))
            else:
                st.error(f"Incorrect judge secret -- ask Anjali.")



if __name__ == '__main__':
    main()
