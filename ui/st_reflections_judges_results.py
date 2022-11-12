import json
import os
import tempfile
from typing import Dict

import streamlit as st
import sys

from ui.utils import upload_file, to_markdown_table

sys.path.append('.')
sys.path.append('..')
from src import reflections_result


def main():
    st.write("Reflections judges results\n")
    temp_dir = tempfile.tempdir

    # Visual Arts
    # Music composition
    # Literature
    # Film/Video
    # Photography
    sample_judges_expertise: Dict[str, str] = {
        "Shweta": "Visual Arts",
        "Whitney": "Music composition",
        "Thom": "Literature",
        "Trisha": "",
        "Dhivya Priya V": ""
    }

    with st.form('form_reflections_results'):
        temp_dir = st.text_input('Directory where the result will be saved', temp_dir)
        min_num_judges_per_entry: int = st.number_input('min judges per entry', min_value=1, max_value=7, step=1, value=3)
        ignore_coi = st.checkbox('ignore conflict of interest?')
        reveal_score_in_report = st.checkbox('reveal score in judge completion report?')
        judges_expertise= json.loads(st.text_area('Enter judge and expertise in json format', json.dumps(sample_judges_expertise)))
        # st.json(judges_expertise)

        uploaded_judges_scoring_fp = os.path.join(temp_dir, f"judge_scores.csv")
        st.write("Hint: for judges scoring file csv download: https://docs.google.com/spreadsheets/d/1ZsCDH9OzNoAC4qagBwkpZdnDaKYOtBxFMR1hzbX_HYI/edit#gid=0")
        upload_file(file_desc="judges scoring file (csv)", out_path=uploaded_judges_scoring_fp, st=st)
        output_path = os.path.join(temp_dir, 'reflections.results.tsv')
        submitted = st.form_submit_button("Generate judges results")
        if submitted:
            st.write(f"\n{'*'*80}\n\nReflections results")
            (results, report) = reflections_result.main(judges_scores_fp=uploaded_judges_scoring_fp,
                                                     ignore_coi=ignore_coi,
                                                     min_num_judges_per_entry=min_num_judges_per_entry,
                                                     judges_expertise=judges_expertise,
                                                     reveal_score_in_report=reveal_score_in_report
                                                     )
            st.write(to_markdown_table(results))
            st.write(f"\n{'*'*80}\n\nResults stored at: {output_path}.")
            with open(output_path, 'w') as outfile:
                outfile.write(f"{results}")

            st.write(f"\nSee details of these ids at: https://docs.google.com/spreadsheets/d/1mRHPLXsvQI_TGLOOrnmO2m9ieQobasoIleBoFyl7ET0/edit#gid=0 \n")

            st.write(f"\n\n{'*'*80}\n\n Report:")
            st.write(to_markdown_table(report))





if __name__ == '__main__':
    main()
