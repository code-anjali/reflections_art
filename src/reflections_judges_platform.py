# Input= the submitted entries data tsv
# 1. Generate 38 (or xxx) number of html pages. Each web page has entry id and a secret passcode field for the judges and art work link and judging criteria and points
# 2. On submission on any form, a web service on the form will be invoked.
# 3. This will add an entry to the excel sheet.
import csv
import os
from typing import Dict, Any, List

from src.utils import ensure_path, save_to_file, split_csv


# (future_todo) a cleaner way would be to use a class with the following entries.
# entry metadata (entry_id, entry_category, entry_statement, entry_urls, entry_student_first_name,
#                 entry_student_last_name, entry_student_teacher_name, entry_grade, entry_parent_email_id, entry_file_types)
# judge_name
# judge_secret
# interpretation
# interpretation_comments
# creativity
# creativity_comments
# technique
# technique_comments
# confidence
# other_comments


# <body onload="parse_remote_csv()">
def fill_overall_template(form_arr, entry_ids, categories, grades, judges):
    head = ''' 
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {
  background-color: white;
}
.button {
        display: inline-block;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        color: #ffffff;
        background-color: #2196F3;
        border-radius: 6px;
        outline: none;
}
</style>
</head>
<body>
<div>
<h3> Welcome judges! Please evaluate your entries.</h3> <br><br>
</div>
'''
    # body = '<p id="http://www.shrikrishnajewels.com/compile/kirtans/1/1.mp3">Kirtan 1: and its <a href="forms/form1.html">link is this</a> </p>'
    rows = []  # for every row, there is an array.
    newline= "\n"

    # table at main/index.html
    # entry id -- judge1, judge2, judge3, judge4, judge5
    #    1         done    done     xxx     xxx    done
    #  ...
    # TODO read is_evaluated status from a google sheet.

    # can make this less hardcoded.
    headers = ["Entry","..."]
    # for judge in judges:
    #     headers.append(f"Judge {str.capitalize(judge)}")

    rows.append(f"<tr>{newline.join(['<th>' + x + '</th>' + newline for x in headers])}</tr>\n")
    for form_full_path, entry_id, category, grade in zip(form_arr, entry_ids, categories, grades):
        rows.append(f'<tr>')
        rows.append(f'\n\t<td id="entry_{entry_id}"> <a href="{form_full_path}">Entry {entry_id}  --  ({category}) -- {grade}</a></td>')
        rows.append(f'\n\t<td id="dummy_{entry_id}">  </td>')
        # for judge in judges:
        #     rows.append(f'\n\t<td id=f"judge_{judge.lower()}_{entry_id}"> x </td>')
        rows.append('</tr>')

    body = '\n<table style=\"border:2px solid blue; padding: 10px 20px; \">' + '\n'.join(rows) + '\n</table>'
    tail='''
</body>
</html>
'''
    return f"{head}\n\n{body}\n\n{tail}"


def iframe_url(x: str):
    x = x.replace("/view?usp=share_link", "/preview").replace("/view?usp=drivesdk", "/preview").replace("/view","/preview")
    x = x.replace("https://drive.google.com/open?id=", "https://drive.google.com/file/d/") \
        .replace("/view","/preview")
    if not x.endswith("/preview"):
        x += "/preview"
    return x



def img_and_other_elems(file_types, urls):
    arr = []
    # <img src=url width="500" height="600">
    # <a href="url" target="_blank"> original link</a>
    for file_type, url in zip(file_types, urls):
        if file_type == "jpg" or file_type == "jpeg":
            # perhaps: create thumbnail from url (because original art does not load)
            # https://drive.google.com/file/d/14hz3ySPn-zB
            # https://drive.google.com/thumbnail?id=14hz3ySPn-zB
            # https://drive.google.com/thumbnail?id=1v-5TIU0_NXb6LVrdLvXCFJxFCoOjzjo7

            # This used to work till 2021 but now thumbnail are stored under lh3
            # url_thumbnail = url.replace("https://drive.google.com/file/d/", "https://drive.google.com/thumbnail?id=")
            # url_thumbnail = url_thumbnail.replace("https://drive.google.com/open?", "https://drive.google.com/thumbnail?")
            # https://drive.google.com/file/d/1WOdQZQ18xhBK8q8ZplJ2jHIpRPlEUN4l/view
            # https://drive.google.com/open?id=1WOdQZQ18xhBK8q8ZplJ2jHIpRPlEUN4l

            url_thumbnail = url.replace("https://drive.google.com/open?id=", "https://drive.google.com/file/d/")
            url_thumbnail = url_thumbnail.replace("https://drive.google.com/file/d/", "https://lh3.googleusercontent.com/d/")
            url_thumbnail = url_thumbnail.replace("/view", "/preview")
            arr.append(f'<img src="{url_thumbnail}" width="500" height="600">')
            arr.append(f'<a href="{url}" target="_blank">Original image high resolution</a>')
        elif file_type == "mp3":
            url_mp3 = iframe_url(url)
            arr.append(f'<iframe src="{url_mp3}" frameborder="1" width="640" height="480"></iframe>')
            arr.append(f'<a href={url_mp3}>Original audio link</a>')
        elif file_type == "mp4":
            url_mp4 = iframe_url(url)
            arr.append(f'<iframe src="{url_mp4}" frameborder="1" width="640" height="480"></iframe>')
            arr.append(f'<a href={url_mp4}>Original video link</a>')
        elif file_type == "pdf":
            # https://drive.google.com/open?id=1ySyK_mZ97BafYSGHzAtNKvxe9c8p28XI
            # https://drive.google.com/file/d/1ySyK_mZ97BafYSGHzAtNKvxe9c8p28XI/view
            # https://drive.google.com/file/d/1aGh69Sm5bta5U63Iu-EaxV1mWn9iyvPT/edit
            url_pdf = iframe_url(url)
            arr.append(f'<iframe src="{url_pdf}" frameborder="1" width="640" height="480"></iframe>')
            # arr.append(f'<a href={url}>Original PDF link</a>')
        elif file_type == "docx":
            url_docx = iframe_url(url)
            arr.append(f'<iframe src="{url_docx}" frameborder="1" width="640" height="480"></iframe>')
            arr.append(f'<a href={url_docx}>Original docx link</a>')
        else:
            arr.append(f'<a href="{url}" target="_blank">Original link (file type: {file_type})</a>')

    return "\n<br><br>".join(arr)

def fill_form_template(form_action: str, data: Dict[str, Any]):
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <title>Judging</title>
    <style>
    .button {
        display: inline-block;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        color: #ffffff;
        background-color: #2196F3;
        border-radius: 6px;
        outline: none;
    }
    .div_sixty_pc{
       width: 60%;
    }
    table{
        table-layout: fixed;
        width: 90%;
    }
    .half_ul{
        width: 60%;
    }
    body{
        padding-left: 1px;
        padding-right: 1px;
        margin: 20px;
    }

    input, select, checkbox {
         width: 45%;
         border:solid 2px #2196F3;
         background-color: white;
         color: black;
         float: left;
         box-sizing: border-box;
         -webkit-box-sizing:border-box;
         -moz-box-sizing: border-box;
    }
    .half_p{
        width: 50%;
    }

    td {
        width: 40%;
    }

</style>
</head>
''' + f'''


<body>
<p><br/>
</p>

<div align="center">
    <h2><b>Scoring form for Judges</b></h2>

    <h3><b><i>2022-23 theme: “Show your voice...” </i></b></h3>
    <br>

    <div align="left">
    Scoring: All PTA Reflections program entries are judged on three criteria: <br>
    1. Interpretation of Theme (40 pts.) <br>
    2. Creativity (30 pts.)<br>
    3. Technique (30 pts.)<br>

    2022-23 Judges guide is <a href="https://drive.google.com/file/d/1E0BydGTOqaN2mR1t4kx5N4cW9RHpFO6a/view"
                               style="color: #0000FF">here</a>
    </div>

</div>


<form action="{form_action}" class="w3-container" method="GET">
    <input id="entry_student_first_name" name="entry_student_first_name" value="{data['entry_student_first_name']}" type="hidden" readonly/><br/>
    <input id="entry_student_last_name" name="entry_student_last_name" value="{data['entry_student_last_name']}" type="hidden" readonly/><br/>
    <input id="entry_student_teacher_name" name="entry_student_teacher_name" value="{data['entry_student_teacher_name']}" type="hidden" readonly/><br/>
    <input id="entry_grade" name="entry_grade" value="{data['entry_grade']}" type="hidden" readonly/><br/>
    <input id="entry_parent_email_id" name="entry_parent_email_id" value="{data['entry_parent_email_id']}" type="hidden" readonly/><br/>
    <input id="entry_file_types" name="entry_file_types" value="{data['entry_file_types']}"  type="hidden" readonly/>
    <input id="entry_statement" name="entry_statement" value="{data['entry_statement']}"  type="hidden" readonly/>
    <input id="entry_urls" name="entry_urls" value="{data['entry_urls']}"  type="hidden" readonly/>
    <input id="entry_id" name="entry_id" value="{data['entry_id']}" type="hidden" readonly/>
    <input id="entry_category" name="entry_category" value="{data['entry_category']}" type="hidden" readonly/>
    <input id="judge_secret" name="judge_secret" value="dummy" type="hidden" readonly/>
    
    <div class="w3-card-4">
        <div class="w3-container w3-blue div_sixty_pc">
            <h5>Entry # {data['entry_id']}  &rarr;  ({data['entry_category']})   &rarr;  {data['entry_grade']}</h5>
        </div>
    
        <p class="half_p"> <b>Title</b>: {data['entry_title']} </p>
        <p class="half_p"> <b>Statement</b>: {data['entry_statement']} </p>
    
        {img_and_other_elems(file_types=split_csv(data['entry_file_types']), urls=split_csv(data['entry_urls']))}
        
        
        <br><br>
        <div class="w3-container w3-blue div_sixty_pc">

            <h6>Interpretation - How closely the piece relates to the theme, based on the work itself and the artist
                statement.</h6>
        </div>
        <ul class="half_ul">
            <li>Beginning - 1-8 pts. - The interpretation lacks clarity and does not communicate the student’s
                concept.
            </li>
            <li>Developing - 9-16 pts. - The interpretation lacks clarity and does not fully communicate the student’s
                concept based on the theme.
            </li>
            <li>Proficient - 17-24 pts. - The interpretation communicates the student’s concept based on the theme.</li>
            <li>Accomplished - 25-32 pts. - The interpretation clearly communicates the student’s concept based on the
                theme but lacks meaning, purpose, and integrity.
            </li>
            <li>Advanced - 33-40 pts. - The interpretation clearly communicates the student's whole concept based on the
                theme with meaning, purpose and integrity.
            </li>
        </ul>


        <table>
            <tr>
                <td> &#9989; Enter score for "Interpretation"</td>
                <td>
                    <input id="interpretation" name="interpretation" placeholder="" required type="text"/>
                </td>
            </tr>


            <tr>
                <td><label for="interpretation_comments"> &#9989; Your comments/notes on "Interpretation of the topic" </label>
                </td>
                <td><input id="interpretation_comments" name="interpretation_comments" placeholder="" type="text"/></td>
            </tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>

        </table>


        <div class="w3-container w3-blue div_sixty_pc"><h6>Creativity - How creative and original the piece is in its conception of
                                              the theme and its presentation. </h6></div>
        <br>

        <ul class="half_ul">
            <li>Beginning - 1-6 pts. - Work is somewhat original and reflects the theme using very conventional ways.
            </li>
            <li>Developing - 7-12 pts. - Work is somewhat original and reflects the theme using conventional ways.</li>
            <li>Proficient - 13-18 pts. - Work is original and reflects the theme using conventional ways.</li>
            <li>Accomplished - 19-24 pts. - Work is primarily original and reflects the theme using imaginative ways.
            </li>
            <li>Advanced - 25-30 pts. - Work is highly original and reflects the theme using un-conventional,
                interesting, imaginative and new ways.
            </li>
        </ul>

        <table>
            <tr>
                <td> &#9989; Enter score for "Creativity"</td>
                <td><input id="creativity" name="creativity" placeholder="" required type="text"/></td>
            </tr>

            <tr>
                <td><label for="creativity_comments"> &#9989; Your comments/notes on "Creativity"</label></td>
                <td><input id="creativity_comments" name="creativity_comments" placeholder="" type="text"/></td>
            </tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
        </table>


        <div class="w3-container w3-blue div_sixty_pc">
            <h6>Technique - The level of skill demonstrated in the basic principles/ techniques of the arts area. </h6>
        </div>
        <br>


        <ul class="half_ul">
            <li>Beginning - 1-6 pts. - Work demonstrates very limited skill of the arts area.</li>
            <li>Developing - 7-12 pts. - Work demonstrates limited skill of the arts area.</li>
            <li>Proficient - 13-18 pts. - Work demonstrates capable skill of the arts area.</li>
            <li>Accomplished - 19-24 pts. - Work demonstrates expertise of skill of the arts area.</li>
            <li>Advanced - 25-30 pts. - Work demonstrates mastery of skill and knowledge of the arts area.</li>
        </ul>

        <table>
            <tr>
                <td> &#9989; Enter score for "Technique"</td>
                <td><input id="technique" name="technique" placeholder="" required type="text"/></td>
            </tr>

            <tr>
                <td><label for="technique_comments"> &#9989; Your comments/notes on "Technique"</label></td>
                <td><input id="technique_comments" name="technique_comments" placeholder="" type="text"/></td>
            </tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
        </table>

        <div class="w3-container w3-blue div_sixty_pc">
            <h6>Other questions. </h6>
        </div>
        <br>

        <table>
            <tr>
                    <td><label for="judge_name"> &#9989; Judge's first name</label></td>
                    <td><input id="judge_name" name="judge_name" placeholder="" required type="text"/></td>
            </tr>

            <tr>
                <td><label for="confidence"> &#9989; Your confidence in this evaluation</label></td>
                <td><select id="confidence" name="confidence" required>
                    <option value="Select confidence" selected>-</option>
                    <option value="Not confident">Not confident</option>
                    <option value="Sort of confident">Sort of confident</option>
                    <option value="Very confident">Very confident</option>
                </select></td>
            </tr>

            <tr>
                <td><label for="coi"> &#9989; Is there any conflict of interest? Please check if any.</label></td>
                <td><input id="coi" name="coi" placeholder="" type="checkbox" value="yes"/></td>
            </tr>

            <tr>
                <td><label for="other_comments"> &#9989;  Other comments if any</label></td>
                <td><input id="other_comments" name="other_comments" placeholder="" type="text"/></td>
            </tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>

        </table>
    </div>

    <br>
    <div style="text-align: center;">
        <input class="button" type="submit" value="Submit"/>
    </div>
</form>
</body>
</html>
'''

def alternate_dict_keys(d, alt_keys):
    for a in alt_keys:
        if a in d:
            return d[a]
    return ""


# TODO update these dict keys (e.g, timestamp can be missing).
# Timestamp Email Address   Student first name  Student last name   Grade   Teacher's  name Upload entry form with file name as (firstname.lastname.grade.pdf)                      Arts Category   Grade division  Upload entry file                                                       Are the file names you are uploading like so  (firstname.lastname.grade.pdf) ?  Does your artwork follow the submission guidelines (size/format etc.)?  Title of artwork    Are you submitting again with updates?  Artist's statement  Artwork details
#           Email Address   Student first name  Student last name   Grade   Teacher's  name "entry form - google drive link with file name as (form.firstname.lastname.grade.pdf)"  Arts Category   Grade division  "Upload entry file with file name as (firstname.lastname.grade)"                                                                                                                                                                    Title of artwork                                            Artist statement    Artwork details
# TODO ensure school name where it is hosted.
def rename_dict_keys(d):
    # GIVEN:
    # Timestamp,Email Address,Student first name,Student last name,Grade,Teacher's  name,
    # Upload entry form with file name as (firstname.lastname.grade.pdf) ,
    # Select the art category for submission,Upload entry file,
    # Are the file names you are uploading like so  (firstname.lastname.grade.pdf) ?,
    # Does your artwork follow the submission guidelines (size/format etc.)?,
    # Artist's statement,Are you submitting again with updates?,id,is_valid_final_entry,file_type,
    # Artwork details

    # EXPECTED:
    # entry_id, entry_category, entry_statement, entry_urls, entry_student_first_name,
    # entry_student_last_name, entry_student_teacher_name, entry_parent_email_id, entry_file_types
    d["entry_id"] = d["id"]
    d["entry_category"] = alternate_dict_keys(d=d, alt_keys=["Select the art category for submission", "Arts Category", "Category:"])
    d["entry_statement"] = alternate_dict_keys(d=d, alt_keys=["Artist's statement" ,"Artist statement", "Artist Statement: (Please type EXACTLY as artist submitted on entry form; do not correct for grammatical and/or spelling errors.)"])
    d["entry_urls"] = alternate_dict_keys(d=d, alt_keys=["Upload entry file" , "Upload entry file with file name as (firstname.lastname.grade)", "Upload entry file. File should be named as (art.school.firstname.lastname.pdf/jpg/mp4)"])
    d["entry_student_first_name"] = alternate_dict_keys(d=d, alt_keys=["Student first name", "Artist's first name"])
    d["entry_student_last_name"] = alternate_dict_keys(d=d, alt_keys=["Student last name", "Artist's last name"])
    d["entry_student_teacher_name"] = alternate_dict_keys(d=d, alt_keys=["Teacher's name", "Teacher's  name"])
    d["entry_grade_division"] = d["Grade division"]
    # Sometimes (e.g., at ISD level) only grade division is used.
    d["entry_grade"] = alternate_dict_keys(d=d, alt_keys=["Grade"]) or d["entry_grade_division"]
    d["entry_parent_email_id"] = d["Email Address"]
    d["entry_file_types"] = d.get("file_type", "")   # TODO check file type
    # TODO add special arts category?
    d["entry_title"] = d["Title of artwork"]
    d["entry_is_valid"] = d.get("is_valid_final_entry", "")
    return d


def load_data_to_forms(fp, out_dir, form_action, website_base_addr, judges):

    index_html = f"{out_dir}/index.html"
    successful_forms = 0
    with open(fp) as f_handle:
        form_online_paths_arr = []
        entry_id_arr = []
        category_arr = []
        grades_arr = []

        for d in csv.DictReader(f_handle):
            id_ = d["id"]
            fname = f'{id_}.html'
            rename_dict_keys(d)
            if d["entry_is_valid"] == "0":
                print(f"Skipping {id_} because entry_is_valid = {d['entry_is_valid']}")
                continue
            form_path_local = os.path.join(out_dir, fname)
            html_form_content = fill_form_template(form_action=form_action, data=d)
            save_to_file(content=html_form_content, out_fp=form_path_local)
            form_path_online = os.path.join(website_base_addr, fname)
            print(f"{form_path_online}'s form : {form_path_local}")
            form_online_paths_arr.append(form_path_online)
            entry_id_arr.append(id_)
            grades_arr.append(d["entry_grade"])
            category_arr.append(d["entry_category"])
            successful_forms += 1
        print(f"Saving index.html to {index_html}")
        save_to_file(content=fill_overall_template(
                                form_arr=form_online_paths_arr,
                                entry_ids=entry_id_arr,
                                categories=category_arr,
                                grades=grades_arr,
                                judges=judges),
                     out_fp=index_html)
        return successful_forms


def main(data_entries_fp: str, out_dir: str, judges: List[str], website_base_addr: str, form_action: str):
    """
    :param data_entries_fp: "data/judges_input/real-judges-data.csv"
    :param out_dir: "data/forms"
    :param judges: ["Dhivya", "Shweta", "Thom", "Trisha", "Whitney"]
    :param website_base_addr: "file://" # http://www.shrikrishnajewels.com/compile/forms
    :param form_action: "https://script.google.com/macros/s/AKfycbyi-42Psz_6118nWOeQNqSL_nXu4VejtnWVtuzH1U5P92w8IZTEXGKdtbmtXyi53ZJR8w/exec"
    :return:
    """
    assert os.path.exists(data_entries_fp), f"\n\ndata entries (input csv) for judges does not exist: {data_entries_fp}"
    ensure_path(fp=out_dir, is_dir=True)
    return load_data_to_forms(fp=data_entries_fp,
                       out_dir=out_dir,
                       judges=judges,
                       website_base_addr=website_base_addr,
                       form_action=form_action)

if __name__ == '__main__':
    # for 2021-22 (Discovery)
    # main(data_entries_fp= "data/judges_input/real-judges-data.csv",
    #      out_dir= "data/forms",
    #      judges =["Dhivya", "Shweta", "Thom", "Trisha", "Whitney"],
    #      website_base_addr = "https://shrikrishnajewels.com/reflections",
    #      form_action="https://script.google.com/macros/s/AKfycbyi-42Psz_6118nWOeQNqSL_nXu4VejtnWVtuzH1U5P92w8IZTEXGKdtbmtXyi53ZJR8w/exec"
    #      )

    # for 2022-23 (Challenger)
    # main(data_entries_fp= "/private/tmp/reflections.sheet1.csv",
    #      out_dir= "data/forms",
    #      judges =["Ryan Eronemo", "Larisa Eronemo", "Sabah Najam","Heidi Bennick", "Kim Blanchard"],
    #      website_base_addr = "https://anjali.tandon.info/schools/reflections_challenger",
    #      form_action="https://script.google.com/macros/s/AKfycbxUWRtQFUmzUb5RlX5dp9pzFyl2vMPfjZkZC-KX1eNE3HqeiPa3bZiWOP5YWun8ZpXT/exec"
    #      )

    # for 2022-23 (Discovery)
    # main(data_entries_fp= "/Users/nikett/Desktop/reflections.discovery.2022.csv",
    #      out_dir= "data/forms",
    #      judges =["Dhivya", "Shweta", "Thom", "Trisha", "Whitney"],
    #      website_base_addr = "https://anjali.tandon.info/schools/reflections_discovery",
    #      form_action="https://script.google.com/macros/s/AKfycbyjb-sQNrv-wq0s-6Cv8HN3Z0IErmcL_4YiymPQnfpqgRN8FqXJUHAE7492NABX6QW0rg/exec"
    #      )

    # for 2022-23 (ISD)
    main(data_entries_fp= "/Users/nikett/Desktop/reflections.isd.entries3.csv",
         out_dir= "data/forms_isd",
         judges =[""],
         website_base_addr = "https://anjali.tandon.info/schools/reflections_isd",
         form_action="https://script.google.com/macros/s/AKfycbyHqmjviglhSTKc4zcrsTT7KiXjZJIWdFDSzml62XkXO4xnP2I3lc-wJMpg_nya7nUwww/exec"
         )
