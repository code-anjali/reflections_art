from prettytable import PrettyTable


def upload_file(file_desc: str, out_path: str, st):
    '''

    :param file_desc: e.g. correct answers csv
    :param out_path: where will the uploaded data be stored.
    :return:
    '''
    uploaded_correct_file_content = st.file_uploader(f"Upload {file_desc}", type="csv")
    if uploaded_correct_file_content is not None:
        with open(out_path, 'wb') as outfile:
            for line_num, line in enumerate(uploaded_correct_file_content):
                outfile.write(line)
            if line_num == 0:
                st.write(f"Sample line from {file_desc}\n")
                st.write(line)

def to_markdown_table(pt: PrettyTable):
    """
    credit: https://gist.github.com/dbzm/68256c86c60d70072576
    Print a pretty table as a markdown table

    :param pt:obj:`prettytable.PrettyTable` pt: a pretty table object.  Any customization
      beyond int and float style may have unexpected effects

    :rtype: str
    :returns: A string that adheres to git markdown table rules
    """
    markdown = "<cannot create pretty pt table>"
    if pt:
        _junc = pt.junction_char
        if _junc != "|":
            pt.junction_char = "|"
        markdown = [row[1:-1] for row in pt.get_string().split("\n")[1:-1]]
        pt.junction_char = _junc
    return "\n".join(markdown)
