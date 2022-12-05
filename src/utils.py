# read csv
# abbreviate second column (take the first char of the string)
import csv
import os
from pathlib import Path

def split_csv(s, lowercase=False):
    return [(x.lower() if lowercase else x).strip() for x in s.split(",") if x.strip()]


def abbreviate_lname(lname:str) -> str:
    # tabdob => T.
    if not lname:
        return ""
    return f"{str.capitalize(lname[0])}."

def abbreviate_all(input_fp: str, output_fp: str):
    '''

    :param input_fp: "data/todo-abbreviate-lastname.csv"
    :return: a new file with updated record
    '''
    with open(input_fp, 'r') as in_csv:
        with open(output_fp, 'w') as out_csv:
            for d in csv.DictReader(in_csv):
                fl = f'{str.capitalize(d["Student"])} {abbreviate_lname(lname=d["name"])}'.strip()
                out_csv.write(f"{fl}\n")

def ensure_path(fp: str, is_dir: bool):
    # Create parent level subdirectories if not exists.
    p = Path(fp)
    if p.exists():
        return
    # if path indicates a dir: Create parent level subdirectories if not exists.
    if not is_dir:
        p.parent.mkdir(parents=True, exist_ok=True)
    # if path indicates a file: Create parent level subdirectories if not exists
    elif is_dir:
        p.mkdir(parents=True, exist_ok=True)



def save_to_file(content: str, out_fp: str):
    ensure_path(out_fp, False)
    with open(out_fp, 'w') as outfile:
        outfile.write(content)

def csv_to_dict(csv_path, key_id, val_id, split_val_on=None):
    dic = {}
    with open(csv_path, 'r') as in_csv:
        for d in csv.DictReader(in_csv):
            dic[d[key_id]] = [x.strip() for x in d[val_id].split(split_val_on)] if split_val_on is not None else d[val_id]
    return dic

if __name__ == '__main__':
    abbreviate_all(input_fp="data/todo-abbreviate-lastname.csv",
                   output_fp="data/done-abbreviate-lastname.csv")


