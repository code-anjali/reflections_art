import os
import tempfile

import streamlit as st
import sys

from src.utils import split_csv
from ui.utils import upload_file

sys.path.append('.')
sys.path.append('..')
from src import reflections_judges_platform


def main():
    st.write("Reflections judges_platform\n")
    # temp_dir = "/tmp/"
    temp_dir = tempfile.tempdir

    with st.form('form_judges_platform'):
        website_base_addr = st.text_input('Where will the forms be hosted (e.g., https://shrikrishnajewels.com/reflections', '')
        judges_csv = st.text_input('First names of judges (comma separated)', 'Dhivya, Shweta, Thom, Trisha, Whitney')
        form_action = st.text_input('Web app from Google sheets (scripts editor)', 'https://script.google.com/macros/s/AKfycbyi-42Psz_6118nWOeQNqSL_nXu4VejtnWVtuzH1U5P92w8IZTEXGKdtbmtXyi53ZJR8w/exec')
        temp_dir = st.text_input('Path where the output html files will be stored', temp_dir)
        uploaded_data_entries_fp = os.path.join(temp_dir, f"data_entries.csv")
        st.write("Hint: to upload data for entries download as csv : https://docs.google.com/spreadsheets/d/1mRHPLXsvQI_TGLOOrnmO2m9ieQobasoIleBoFyl7ET0/edit#gid=0")
        upload_file(file_desc="data entries file (csv)", out_path=uploaded_data_entries_fp, st=st)
        submitted = st.form_submit_button("Generate judges_platform")

        if submitted:
            out_dir = os.path.join(temp_dir, "judges_forms")
            st.write(f"judges_platform at : {out_dir}")
            judges_platform_cnt = reflections_judges_platform.main(data_entries_fp=uploaded_data_entries_fp,
                                                                   out_dir=out_dir,
                                                                   website_base_addr=website_base_addr,
                                                                   judges=split_csv(judges_csv),
                                                                   form_action=form_action
                                                                   )
            index_html_url = f"file://{out_dir}/index.html"
            st.write(f"{judges_platform_cnt} new forms (referenced in the index.html) "
                     f"are stored at the local directory: {out_dir}. \n\nmain web page is at {index_html_url}")

            # st.write(f"[click here to see the generated file]({index_html_url})")


if __name__ == '__main__':
    main()
