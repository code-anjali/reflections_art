import streamlit as st
import sys

from prettytable import PrettyTable

sys.path.append('.')
sys.path.append('..')

from src.judges_score_backend import JudgeScoresBackend


def main():
    st.set_page_config(layout="wide")
    st.write("Reflections Judges Dashboard (takes a few seconds to load)\n")
    if "backend" not in st.session_state:
        st.session_state["backend"] = JudgeScoresBackend()  # cache backend in streamlit cache

    with st.form('form_reflections_results'):
        judge_secret = st.text_input('Secret passcode', 'yummy')
        judge_name= st.text_input('Judge name', '')
        submitted = st.form_submit_button("Generate dashboard")
        if submitted:
            st.write(f"\n{'*'*80}\n\nAssignments for {judge_name}")
            results = st.session_state["backend"].lookup_judge_scores(judge_name=judge_name, judge_secret=judge_secret)
            pt_table: PrettyTable = st.session_state["backend"].to_pretty_table(entries=results)
            st.markdown(pt_table.get_html_string(), unsafe_allow_html=True)



if __name__ == '__main__':
    main()
